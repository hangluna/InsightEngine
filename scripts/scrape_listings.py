#!/usr/bin/env python3
"""
Lightweight scraper to fetch job listing URLs from seed queries.
Reads `tmp/seed_queries.json` and writes `tmp/listings_raw.json`.

This is a conservative fetcher: follows robots/headers politeness, limited per-platform.
"""
import json
import time
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse

try:
    import requests
except Exception:
    requests = None

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

SEED_PATH = 'tmp/seed_queries.json'
OUT_PATH = 'tmp/listings_raw.json'
PLATFORMS = ['itviec', 'vietnamworks', 'topcv', 'indeed']
PER_PLATFORM_LIMIT = 20


def fetch_url(url):
    headers = {'User-Agent': 'InsightEngineBot/1.0 (+https://example.com)'}
    try:
        if requests:
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            return r.text
        else:
            # fallback
            from urllib.request import Request, urlopen
            req = Request(url, headers=headers)
            with urlopen(req, timeout=15) as resp:
                return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None


def extract_links(html, base_url):
    urls = set()
    if not html:
        return []
    if BeautifulSoup:
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            if href.startswith('javascript:') or href.startswith('#'):
                continue
            absu = urljoin(base_url, href)
            urls.add(absu)
    else:
        import re
        for m in re.findall(r'href=["\']([^"\']+)["\']', html):
            if m.startswith('javascript:') or m.startswith('#'):
                continue
            urls.add(urljoin(base_url, m))
    return list(urls)


def plausible_job_url(u):
    # heuristics
    u = u.lower()
    terms = ['job', 'viec', 'viec-lam', 'it-jobs', 'jobs', 'ung-vien', 'recruit', 'career']
    parsed = urlparse(u)
    if parsed.scheme not in ('http', 'https'):
        return False
    for t in terms:
        if t in u:
            return True
    return False


def main():
    os.makedirs('tmp', exist_ok=True)
    if not os.path.exists(SEED_PATH):
        print('Seed file not found:', SEED_PATH)
        return
    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        seeds = json.load(f).get('seeds', [])

    by_platform = {p: [] for p in PLATFORMS}
    for s in seeds:
        p = s.get('platform')
        if p in by_platform and len(by_platform[p]) < PER_PLATFORM_LIMIT:
            by_platform[p].append(s)

    results = {'generated_at': datetime.utcnow().isoformat() + 'Z', 'batches': []}
    for p, items in by_platform.items():
        print(f'== Platform {p}: {len(items)} seeds')
        batch = {'platform': p, 'fetched_at': datetime.utcnow().isoformat() + 'Z', 'entries': []}
        for s in items:
            qurl = s.get('query_url')
            print(' Fetching:', qurl)
            html = fetch_url(qurl)
            time.sleep(1.0)
            links = extract_links(html, qurl)
            filtered = [u for u in links if plausible_job_url(u) and urlparse(u).netloc]
            # dedupe
            seen = set()
            filtered_unique = []
            for u in filtered:
                if u in seen:
                    continue
                seen.add(u)
                filtered_unique.append(u)
            entry = {'seed': s, 'found_count': len(filtered_unique), 'found_urls': filtered_unique}
            batch['entries'].append(entry)
        results['batches'].append(batch)
        # small pause between platforms
        time.sleep(2.0)

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print('✅ Saved listings to', OUT_PATH)


if __name__ == '__main__':
    main()
