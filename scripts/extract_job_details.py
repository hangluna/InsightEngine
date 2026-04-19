#!/usr/bin/env python3
"""
Extract job details from listing URLs found in tmp/listings_raw.json
Writes output to tmp/jobs_extracted.json

Limit: by default MAX_EXTRACT=500 (env var to change)
"""
import json
import os
import re
import time
from datetime import datetime
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    requests = None
    BeautifulSoup = None

SEED_FILE = 'tmp/listings_raw.json'
OUT_FILE = 'tmp/jobs_extracted.json'
PROVINCES = [
    "Hà Nội","Hồ Chí Minh","Đà Nẵng","Hải Phòng","Cần Thơ","Bình Dương",
    "Đồng Nai","Khánh Hòa","Quảng Ninh","Bà Rịa - Vũng Tàu","Thừa Thiên Huế",
    "Nghệ An","Bắc Ninh","Hải Dương","Hưng Yên","Bắc Giang","Vĩnh Phúc",
    "Nam Định","Thanh Hóa","Thái Nguyên","Bình Thuận","Gia Lai","Kon Tum",
    "Lâm Đồng","Long An","Tiền Giang","Bến Tre","An Giang","Kiên Giang",
    "Sóc Trăng","Bắc Kạn","Bắc Giang","Bình Phước","Hòa Bình","Phú Thọ",
    "Quảng Nam","Quảng Ngãi","Quảng Trị","Ninh Bình","Hà Tĩnh","Yên Bái",
    "Sơn La","Lào Cai","Điện Biên","Hậu Giang","Vĩnh Long","Trà Vinh",
    "Bắc Liêu","Cà Mau","Phú Yên","Tây Ninh","Đắk Lắk","Đắk Nông"
]


def fetch(url):
    headers = {'User-Agent': 'InsightEngineBot/1.0 (+https://example.com)'}
    try:
        if requests:
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            return r.text
        else:
            from urllib.request import Request, urlopen
            req = Request(url, headers=headers)
            with urlopen(req, timeout=15) as resp:
                return resp.read().decode('utf-8', errors='ignore')
    except Exception:
        return None


def text_of(elem):
    if not elem:
        return ''
    return elem.get_text(separator=' ', strip=True)


def find_title(soup):
    # og:title, h1, title tags
    t = None
    if soup.find('meta', property='og:title'):
        t = soup.find('meta', property='og:title').get('content', '').strip()
    if not t and soup.title:
        t = soup.title.string.strip()
    if not t:
        h1 = soup.find('h1')
        if h1:
            t = text_of(h1)
    return t or ''


def find_company(soup):
    selectors = ['.company', '.employer', '.company-name', '.job-company', '.company-title']
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            return text_of(el)
    # try meta
    if soup.find('meta', {'name': 'author'}):
        return soup.find('meta', {'name': 'author'}).get('content','').strip()
    # fallback: look for link to company
    a = soup.find('a', href=True)
    if a and 'company' in a.get('href',''):
        return text_of(a)
    return ''


def find_location(soup):
    # common labels
    text = soup.get_text(separator=' ', strip=True)
    m = re.search(r'Địa điểm[:\s]+([^\n\|\-\r]+)', text)
    if m:
        return m.group(1).strip()
    # selectors
    for sel in ['.location', '.job-location', '.workplace', '.address']:
        el = soup.select_one(sel)
        if el:
            return text_of(el)
    return ''


def find_salary(soup):
    text = soup.get_text(separator=' ', strip=True)
    # look for patterns like 8-12 triệu, 10 triệu, $1000
    m = re.search(r'((?:\d+[\.,]?\d*)\s*(?:-\s*(?:\d+[\.,]?\d*)\s*)?(?:triệu|triệu VNĐ|VND|.vn|k|K|USD|usd))', text, re.I)
    if m:
        return m.group(1).strip()
    # look for 'Lương' label
    m2 = re.search(r'Lương[:\s]*([^\n\r\|]+)', text)
    if m2:
        return m2.group(1).strip()
    return ''


def parse_salary_range(s):
    if not s:
        return None, None
    s = s.replace(',', '.').lower()
    # find numbers in triệu
    m = re.findall(r'(\d+[\.]?\d*)', s)
    nums = [float(x) for x in m] if m else []
    if 'triệu' in s or 'vnđ' in s or 'vnd' in s or 'm' in s:
        # interpret as million VND
        if len(nums) == 1:
            return nums[0], nums[0]
        elif len(nums) >= 2:
            return nums[0], nums[1]
    # USD or k handling omitted
    return (nums[0] if nums else None), (nums[1] if len(nums)>1 else (nums[0] if nums else None))


def find_experience(soup):
    text = soup.get_text(separator=' ', strip=True)
    m = re.search(r'Kinh nghiệm[:\s]*([^\n\r\|]+)', text, re.I)
    if m:
        return m.group(1).strip()
    # common english
    m2 = re.search(r'Experience[:\s]*([^\n\r\|]+)', text, re.I)
    if m2:
        return m2.group(1).strip()
    return ''


def parse_experience_range(s):
    if not s:
        return None, None
    m = re.findall(r'(\d+)', s)
    nums = [int(x) for x in m] if m else []
    if 'fresher' in s.lower() or 'mới' in s.lower() or '0' in s:
        return 0, 1
    if len(nums) == 1:
        return nums[0], nums[0]
    elif len(nums) >= 2:
        return nums[0], nums[1]
    return None, None


def find_skills(soup):
    # try lists under requirements
    skills = set()
    for sel in ['.skills', '.job-requirements', '.requirement', '.requirements', '.job-req']:
        for el in soup.select(sel):
            for li in el.find_all(['li']):
                skills.add(text_of(li))
            # fallback: comma-split
            skills.update([x.strip() for x in text_of(el).split(',') if len(x.strip())>1])
    # keyword search
    text = soup.get_text(separator=' ', strip=True)
    candidates = re.findall(r'\b(JavaScript|Java|Python|Node\.js|Node|React|Angular|Vue|PHP|Golang|Go|C\+\+|C#|SQL|MySQL|PostgreSQL|MongoDB|Docker|Kubernetes|AWS|Azure|Git)\b', text, re.I)
    for c in candidates:
        skills.add(c)
    return list(skills)


def find_company_website(soup, base_url):
    # company section links
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'http' in href and ('.' in urlparse(href).netloc) and 'facebook' not in href.lower():
            # if link text contains 'website' or 'site' or href domain differs from job site
            txt = text_of(a).lower()
            if 'website' in txt or 'website' in href or (urlparse(href).netloc not in urlparse(base_url).netloc):
                return href
    return ''


def detect_province(location_text):
    if not location_text:
        return []
    found = []
    for p in PROVINCES:
        if p.lower() in location_text.lower():
            found.append(p)
    return found


def extract_from_url(url):
    html = fetch(url)
    if not html:
        return None
    if not BeautifulSoup:
        # very small fallback
        return {'raw_html_snippet': html[:200]}
    soup = BeautifulSoup(html, 'html.parser')
    title = find_title(soup)
    company = find_company(soup)
    location = find_location(soup)
    salary_raw = find_salary(soup)
    sal_min, sal_max = parse_salary_range(salary_raw)
    exp_raw = find_experience(soup)
    exp_min, exp_max = parse_experience_range(exp_raw)
    skills = find_skills(soup)
    company_site = find_company_website(soup, url)
    provinces = detect_province(location)

    return {
        'job_title': title,
        'company_name': company,
        'company_address': location,
        'province_city': provinces,
        'salary_raw': salary_raw,
        'salary_min_mvn_m': sal_min,
        'salary_max_mvn_m': sal_max,
        'years_of_experience_raw': exp_raw,
        'years_of_experience_min': exp_min,
        'years_of_experience_max': exp_max,
        'required_skills': skills,
        'job_detail_url': url,
        'company_website': company_site,
        'company_reviews_links': [],
        'workplace_rating': None,
        'source_platform': urlparse(url).netloc,
        'sources': [{'platform': urlparse(url).netloc, 'url': url, 'fetched_at': datetime.utcnow().isoformat()+'Z'}],
        'post_date': None,
        'remote_flag': ('remote' in (location or '').lower()),
        'fetched_at': datetime.utcnow().isoformat()+'Z'
    }


def main():
    if not os.path.exists(SEED_FILE):
        print('Missing', SEED_FILE)
        return
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    urls = []
    for batch in data.get('batches', []):
        for entry in batch.get('entries', []):
            for u in entry.get('found_urls', []):
                urls.append(u)

    # dedupe
    seen = set()
    uniq_urls = []
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        uniq_urls.append(u)

    max_ex = int(os.environ.get('MAX_EXTRACT', '500'))
    to_process = uniq_urls[:max_ex]
    print(f'Found {len(uniq_urls)} unique URLs, processing {len(to_process)} (MAX_EXTRACT={max_ex})')

    results = {'generated_at': datetime.utcnow().isoformat()+'Z', 'jobs': []}
    for i, u in enumerate(to_process, 1):
        print(f'[{i}/{len(to_process)}] Extracting: {u}')
        try:
            item = extract_from_url(u)
            if item:
                results['jobs'].append(item)
        except Exception as e:
            print(' Error extracting', u, str(e))
        time.sleep(1.0)

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print('✅ Saved extracted jobs to', OUT_FILE)


if __name__ == '__main__':
    main()
