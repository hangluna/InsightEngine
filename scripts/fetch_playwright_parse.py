#!/usr/bin/env python3
"""
Fetch job detail pages with Playwright and parse with BeautifulSoup.
Input: tmp/itviec_job_urls.json
Output: tmp/jobs_extracted_playwright.json
"""
import json, os, time
from datetime import datetime
from urllib.parse import urlparse

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

from playwright.sync_api import sync_playwright

INPUT = 'tmp/itviec_job_urls.json'
OUT = 'tmp/jobs_extracted_playwright.json'


def parse_job_from_html(url, html):
    if not BeautifulSoup:
        return None
    soup = BeautifulSoup(html, 'html.parser')
    title = ''
    if soup.find('meta', property='og:title'):
        title = soup.find('meta', property='og:title').get('content','').strip()
    if not title and soup.find('h1'):
        title = soup.find('h1').get_text(strip=True)
    company = ''
    csel = soup.select_one('.company-name, .company, .employer, .company-title')
    if csel:
        company = csel.get_text(strip=True)
    location = ''
    lsel = soup.select_one('.job-location, .location, .workplace, .address')
    if lsel:
        location = lsel.get_text(strip=True)
    # salary
    text = soup.get_text(' ', strip=True)
    import re
    m = re.search(r'Lương[:\s]*([^\n\|]+)', text)
    salary_raw = m.group(1).strip() if m else ''
    # experience
    m2 = re.search(r'Kinh nghiệm[:\s]*([^\n\|]+)', text)
    exp = m2.group(1).strip() if m2 else ''
    # skills
    skills = []
    for sel in soup.select('.job-requirements li, .requirements li, .skills li'):
        skills.append(sel.get_text(strip=True))
    if not skills:
        # try keywords
        kws = re.findall(r'\b(JavaScript|Java|Python|Node\.js|Node|React|Angular|Vue|PHP|Golang|Go|C\+\+|C#|SQL|MySQL|PostgreSQL|MongoDB|Docker|Kubernetes|AWS|Azure|Git)\b', text, re.I)
        skills = list(dict.fromkeys(kws))

    return {
        'job_title': title,
        'company_name': company,
        'company_address': location,
        'province_city': [],
        'salary_raw': salary_raw,
        'salary_min_mvn_m': None,
        'salary_max_mvn_m': None,
        'years_of_experience_raw': exp,
        'years_of_experience_min': None,
        'years_of_experience_max': None,
        'required_skills': skills,
        'job_detail_url': url,
        'company_website': None,
        'company_reviews_links': [],
        'workplace_rating': None,
        'source_platform': urlparse(url).netloc,
        'sources': [{'platform': urlparse(url).netloc, 'url': url, 'fetched_at': datetime.utcnow().isoformat()+'Z'}],
        'post_date': None,
        'remote_flag': 'remote' in (location or '').lower(),
        'fetched_at': datetime.utcnow().isoformat()+'Z'
    }


def main():
    os.makedirs('tmp', exist_ok=True)
    data = json.load(open(INPUT, 'r', encoding='utf-8'))
    urls = data.get('links', [])
    results = {'generated_at': datetime.utcnow().isoformat()+'Z', 'jobs': []}
    headful = os.environ.get('HEADFUL','0') in ('1','true','True')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headful)
        context = browser.new_context(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
        page = context.new_page()
        import html as _html
        for i,u in enumerate(urls,1):
            try:
                u_clean = _html.unescape(u)
                print(f'[{i}/{len(urls)}] goto', u_clean)
                page.goto(u_clean, timeout=60000, wait_until='domcontentloaded')
                # simulate simple human interaction
                try:
                    page.mouse.move(100,100)
                    page.mouse.down()
                    page.mouse.up()
                except Exception:
                    pass
                page.evaluate('window.scrollTo(0, document.body.scrollHeight/3)')
                page.wait_for_timeout(1500)
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(1000)
                page_html = page.content()
                job = parse_job_from_html(u_clean, page_html)
                if job:
                    results['jobs'].append(job)
            except Exception as e:
                print('error', e)
            time.sleep(1.0)
        try:
            browser.close()
        except:
            pass

    open(OUT, 'w', encoding='utf-8').write(json.dumps(results, ensure_ascii=False, indent=2))
    print('Saved', len(results['jobs']), 'jobs ->', OUT)


if __name__ == '__main__':
    main()
