#!/usr/bin/env python3
"""
internal_search.py — Perform a search using a platform's internal search endpoint
discovered via DOM exploration (dom_explorer.py).

Usage:
  python3 internal_search.py <search_url> --query "<keyword>" [options]

Options:
  --query <str>          Search keyword(s)
  --method GET|POST      HTTP method (default: GET from form action)
  --fields '{"q": "keyword", "type": "jobs"}'
                         Extra form fields as JSON (override defaults)
  --use-playwright       Use Playwright browser for JS-rendered results
  --limit <N>            Max items to extract (default: 30)
  --output <file>        Save output to file (default: stdout)

Output: JSON list of {url, title, snippet} items extracted from search results
"""
import sys
import json
import argparse
import re
from urllib.parse import urljoin, urlparse, urlencode


def build_search_url(action_url: str, query: str, extra_fields: dict) -> str:
    """Build a GET search URL from action URL + query + extra fields."""
    params = {**extra_fields, "q": query}  # Extra fields may override "q" key
    # Find the first input that looks like a query field
    return action_url + ("&" if "?" in action_url else "?") + urlencode(params)


def extract_items_from_html(html: str, base_url: str) -> list:
    """Extract item URLs and titles from a search results page."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("ERROR: Install beautifulsoup4: pip install beautifulsoup4", file=sys.stderr)
        return []

    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(base_url).netloc
    items = []
    seen_urls = set()

    # Heuristic: items are links with slugs or numeric IDs in the href
    item_pattern = re.compile(r"[-/](\d{4,}|[a-z0-9]+-[a-z0-9]+-\d{3,})(/|$)")

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        # Same domain only
        if base_domain not in parsed.netloc:
            continue

        # Must look like an item page (not a listing/search/nav page)
        if not item_pattern.search(parsed.path):
            continue

        # Skip if it's a search/listing page URL
        if any(x in parsed.path for x in ["/search", "/search?", "/jobs?", "/find?", "?page=", "?q="]):
            continue
        if any(x in parsed.query for x in ["page=", "q=", "query=", "keyword="]):
            continue

        if full_url not in seen_urls:
            seen_urls.add(full_url)
            title = a.get_text(strip=True)[:120] or ""
            # Try to get surrounding context for snippet
            parent = a.parent
            snippet = parent.get_text(strip=True)[:200] if parent else ""
            items.append({
                "url": full_url,
                "title": title,
                "snippet": snippet,
            })

    return items


def fetch_html_standard(url: str) -> str:
    """Fetch URL using httpx or urllib."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,vi;q=0.9,en;q=0.8",
    }
    try:
        import httpx
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            return resp.text
    except ImportError:
        pass
    import urllib.request
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_html_playwright(url: str, method: str = "GET", post_data: dict = None) -> str:
    """Fetch URL using Playwright, optionally submitting a form via POST."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError("Install playwright: pip install playwright && playwright install chromium")

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
            if method.upper() == "POST" and post_data:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                for name, value in post_data.items():
                    try:
                        page.fill(f"input[name='{name}']", str(value))
                    except Exception:
                        pass
                page.keyboard.press("Enter")
            else:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2000)
            return page.content()
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description="Search using internal platform search endpoint")
    parser.add_argument("search_url", help="The search endpoint URL (from DOM exploration)")
    parser.add_argument("--query", required=True, help="Search keyword(s)")
    parser.add_argument("--method", default="GET", choices=["GET", "POST"], help="HTTP method")
    parser.add_argument("--fields", default="{}", help="Extra form fields as JSON")
    parser.add_argument("--use-playwright", action="store_true", help="Use Playwright browser")
    parser.add_argument("--limit", type=int, default=30, help="Max items to return")
    parser.add_argument("--output", default=None, help="Output file path")
    args = parser.parse_args()

    extra_fields = json.loads(args.fields)

    # Build search URL
    if args.method.upper() == "GET":
        url = build_search_url(args.search_url, args.query, extra_fields)
        try:
            if args.use_playwright:
                html = fetch_html_playwright(url)
            else:
                html = fetch_html_standard(url)
        except Exception as e:
            result = {"error": str(e), "search_url": args.search_url, "query": args.query, "items": []}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)
    else:
        # POST: build form data
        post_data = {**extra_fields, "q": args.query}
        try:
            html = fetch_html_playwright(args.search_url, method="POST", post_data=post_data)
        except Exception as e:
            result = {"error": str(e), "search_url": args.search_url, "query": args.query, "items": []}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)

    items = extract_items_from_html(html, args.search_url)
    items = items[:args.limit]

    result = {
        "search_url": args.search_url,
        "query": args.query,
        "method": args.method,
        "items_found": len(items),
        "items": items,
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Internal search results saved: {args.output} ({len(items)} items, {len(output)} bytes)", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
