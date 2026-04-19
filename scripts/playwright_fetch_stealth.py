#!/usr/bin/env python3
"""
Fetch a page using Playwright with basic stealth tricks (override navigator.webdriver,
set user agent, languages, and minimal stealth headers). Save output to tmp/stealth_fetch.html
"""
from playwright.sync_api import sync_playwright
import sys
from datetime import datetime
import os

URLS = [
    'https://itviec.com/it-jobs?keyword=fresher&location=Hà+Nội',
    'https://www.vietnamworks.com/tim-viec-lam/fresher?loc=Hà+Nội'
]

OUT_DIR = 'tmp'
os.makedirs(OUT_DIR, exist_ok=True)


def fetch(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            locale='vi-VN',
            timezone_id='Asia/Ho_Chi_Minh'
        )
        # small stealth: remove webdriver flag
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
        # languages
        context.add_init_script("Object.defineProperty(navigator, 'languages', {get: () => ['vi-VN','vi','en-US','en']});")
        page = context.new_page()
        try:
            page.set_default_navigation_timeout(30000)
            page.goto(url, wait_until='networkidle')
            # wait a bit for JS challenges
            page.wait_for_timeout(8000)
            html = page.content()
            ts = datetime.utcnow().isoformat()
            fname = os.path.join(OUT_DIR, 'stealth_fetch_' + ts.replace(':','-') + '.html')
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(html)
            print('SAVED', fname)
            return html
        except Exception as e:
            print('ERROR', e)
            return None
        finally:
            try:
                browser.close()
            except:
                pass


if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else URLS[0]
    print('Fetching', url)
    out = fetch(url)
    if out:
        print('Length', len(out))
    else:
        print('No content')
