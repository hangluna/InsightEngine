#!/usr/bin/env python3
"""
Playwright-based scraper for job listing pages (renders JS-heavy sites).
Reads tmp/seed_queries.json and writes tmp/listings_raw.json (overwrites) with rendered link lists.
"""
import json, os, time
from datetime import datetime
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

SEED_PATH = 'tmp/seed_queries.json'
OUT_PATH = 'tmp/listings_raw.json'
PLATFORMS = ['itviec','vietnamworks','topcv','indeed']
PER_PLATFORM_LIMIT = 20

def plausible_job_url(u):
    u = (u or '').lower()
    terms = ['job','viec','viec-lam','it-jobs','jobs','ung-vien','recruit','career','/viec-lam/']
    try:
        parsed = urlparse(u)
        if parsed.scheme not in ('http','https'):
            return False
    except Exception:
        return False
    for t in terms:
        if t in u:
            return True
    return False

def extract_links_from_html(html, base_url):
    import re
    urls = set()
    for m in re.findall(r'href=["\']([^"\']+)["\']', html, re.I):
        if m.startswith('javascript:') or m.startswith('#'):
            continue
        urls.add(urljoin(base_url, m))
    return list(urls)

def main():
    os.makedirs('tmp', exist_ok=True)
    if not os.path.exists(SEED_PATH):
        print('Seed file missing:', SEED_PATH); return
    seeds = json.load(open(SEED_PATH,'r',encoding='utf-8')).get('seeds',[])
    by_platform = {p:[] for p in PLATFORMS}
    for s in seeds:
        p = s.get('platform')
        if p in by_platform and len(by_platform[p]) < PER_PLATFORM_LIMIT:
            by_platform[p].append(s)

    results = {'generated_at': datetime.utcnow().isoformat()+'Z', 'batches': []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
        page = context.new_page()
        for platform, items in by_platform.items():
            print('== Platform', platform, len(items), 'seeds')
            batch = {'platform': platform, 'fetched_at': datetime.utcnow().isoformat()+'Z', 'entries': []}
            for s in items:
                qurl = s.get('query_url')
                print(' Render:', qurl)
                try:
                    page.goto(qurl, timeout=60000, wait_until='domcontentloaded')
                    page.wait_for_timeout(1200)
                    # basic interaction
                    try:
                        page.mouse.move(200,200)
                        page.evaluate('window.scrollTo(0, document.body.scrollHeight/3)')
                        page.wait_for_timeout(800)
                        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                        page.wait_for_timeout(800)
                    except Exception:
                        pass
                    html = page.content()
                    links = extract_links_from_html(html, qurl)
                    filtered = [u for u in links if plausible_job_url(u) and urlparse(u).netloc]
                except Exception as e:
                    print(' error rendering', e)
                    filtered = []
                batch['entries'].append({'seed': s, 'found_count': len(filtered), 'found_urls': filtered})
                time.sleep(1.0)
            results['batches'].append(batch)
            time.sleep(1.0)
        try:
            browser.close()
        except Exception:
            pass

    open(OUT_PATH,'w',encoding='utf-8').write(json.dumps(results, ensure_ascii=False, indent=2))
    print('✅ Saved rendered listings to', OUT_PATH)

if __name__ == '__main__':
    main()
