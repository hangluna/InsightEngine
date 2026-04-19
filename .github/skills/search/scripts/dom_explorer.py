#!/usr/bin/env python3
"""
dom_explorer.py — Extract DOM structure from a source website for navigation/search discovery.

Usage:
  python3 dom_explorer.py <URL> [options]

Options:
  --extract nav,search,links   What to extract (default: all)
  --use-playwright             Use Playwright for JS-rendered pages
  --output <file>              Save output to file (default: stdout)

Output: JSON with nav_links, search_forms, url_patterns, api_hints
"""
import sys
import json
import argparse
import re
from urllib.parse import urljoin, urlparse


def extract_dom_structure(html_content: str, base_url: str) -> dict:
    """Extract navigation, search forms, URL patterns, and API hints from HTML."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("ERROR: beautifulsoup4 not installed. Run: pip install beautifulsoup4", file=sys.stderr)
        sys.exit(1)

    soup = BeautifulSoup(html_content, "html.parser")
    base_domain = urlparse(base_url).netloc
    result = {
        "source_url": base_url,
        "nav_links": [],
        "search_forms": [],
        "url_patterns": [],
        "api_hints": [],
    }

    # 1. Extract nav links
    nav_elements = soup.find_all(["nav", "header"]) or [soup]
    seen_hrefs = set()
    for element in nav_elements:
        for a in element.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            # Only include same-domain links
            if base_domain in parsed.netloc and href not in seen_hrefs:
                seen_hrefs.add(href)
                result["nav_links"].append({
                    "text": a.get_text(strip=True)[:60],
                    "href": href,
                    "full_url": full_url,
                })
    # Limit to most useful nav links
    result["nav_links"] = result["nav_links"][:20]

    # 2. Extract search forms
    for form in soup.find_all("form"):
        action = form.get("action", "")
        full_action = urljoin(base_url, action) if action else base_url
        inputs = []
        for inp in form.find_all(["input", "select"]):
            inp_name = inp.get("name", "")
            inp_type = inp.get("type", "text")
            if inp_name and inp_type not in ("hidden", "submit", "button", "checkbox", "radio"):
                inputs.append({"name": inp_name, "type": inp_type, "placeholder": inp.get("placeholder", "")})
        if inputs:
            result["search_forms"].append({
                "action": full_action,
                "method": form.get("method", "get").upper(),
                "inputs": inputs,
            })

    # 3. Extract URL patterns (item links — have IDs or slugs)
    item_pattern = re.compile(r"[-/](\d{4,}|[a-z0-9]+-[a-z0-9]+-\d{4,})(/|$)")
    seen_patterns = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if item_pattern.search(href):
            # Normalize to pattern
            normalized = re.sub(r"\d{4,}", "{ID}", href)
            normalized = re.sub(r"[a-z0-9]+-[a-z0-9]+-\d{4,}", "{SLUG}", normalized)
            if normalized not in seen_patterns:
                seen_patterns.add(normalized)
                result["url_patterns"].append({
                    "example": href[:120],
                    "pattern": normalized[:120],
                })
    result["url_patterns"] = result["url_patterns"][:10]

    # 4. Extract API hints from inline scripts
    for script in soup.find_all("script"):
        script_text = script.string or ""
        # Look for API endpoints
        api_matches = re.findall(r"""["'](\/(api|search|v\d+)[^"'\s]{3,60})["']""", script_text)
        for match in api_matches[:5]:
            endpoint = match[0]
            if endpoint not in result["api_hints"]:
                result["api_hints"].append(endpoint)

    return result


def fetch_with_requests(url: str) -> str:
    """Fetch URL using httpx or requests."""
    try:
        import httpx
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            return resp.text
    except ImportError:
        pass

    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}")


def fetch_with_playwright(url: str) -> str:
    """Fetch URL using Playwright for JS-rendered pages."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError("Playwright not installed. Run: pip install playwright && playwright install chromium")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2000)
            return page.content()
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description="Extract DOM structure from a source URL")
    parser.add_argument("url", help="URL to explore")
    parser.add_argument("--extract", default="all", help="Comma-separated: nav,search,links,api")
    parser.add_argument("--use-playwright", action="store_true", help="Use Playwright for JS-rendered pages")
    parser.add_argument("--output", default=None, help="Output file (default: stdout)")
    args = parser.parse_args()

    try:
        if args.use_playwright:
            html = fetch_with_playwright(args.url)
        else:
            html = fetch_with_requests(args.url)
    except Exception as e:
        print(json.dumps({"error": str(e), "source_url": args.url}))
        sys.exit(1)

    if not html or len(html) < 100:
        print(json.dumps({"error": "Empty or too-short response", "source_url": args.url, "length": len(html or "")}))
        sys.exit(1)

    structure = extract_dom_structure(html, args.url)

    output = json.dumps(structure, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"DOM structure saved to: {args.output} ({len(output)} bytes)", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
