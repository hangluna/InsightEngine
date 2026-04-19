#!/usr/bin/env python3
"""
Generate seed queries for job data collection across Vietnamese provinces
Outputs JSON to tmp/seed_queries.json
"""
import json
from datetime import datetime

PROVINCES = [
    "Hà Nội","Hồ Chí Minh","Đà Nẵng","Hải Phòng","Cần Thơ","Bình Dương",
    "Đồng Nai","Khánh Hòa","Quảng Ninh","Bà Rịa - Vũng Tàu","Thừa Thiên Huế",
    "Nghệ An","Bắc Ninh","Hải Dương","Hưng Yên","Bắc Giang","Vĩnh Phúc",
    "Nam Định","Thanh Hóa","Thái Nguyên","Bình Thuận","Gia Lai","Kon Tum",
    "Lâm Đồng","Long An","Tiền Giang","Bến Tre","An Giang","Kiên Giang",
    "Sóc Trăng","Bắc Kạn","Bắc Giang","Bình Phước","Hòa Bình","Phú Thọ",
    "Quảng Nam","Quảng Ngãi","Quảng Trị","Ninh Bình","Hà Tĩnh","Yên Bái",
    "Sơn La","Lào Cai","Điện Biên","Hậu Giang","Vĩnh Long","Trà Vinh",
    "Bắc Liêu","Cà Mau","Phú Yên","Tây Ninh","Đắk Lắk","Đắk Nông",
    "Hậu Giang","Hải Dương"
]

KEYWORDS = [
    "fresher","junior","mới tốt nghiệp","mới ra trường","intern","thực tập"
]

SOURCES = {
    "itviec": {
        "template": "https://itviec.com/it-jobs?keyword={kw}&location={city}",
        "requires_js": False
    },
    "vietnamworks": {
        "template": "https://www.vietnamworks.com/tim-viec-lam/{kw}?loc={city}",
        "requires_js": False
    },
    "topcv": {
        "template": "https://www.topcv.vn/viec-lam?keyword={kw}&address={city}",
        "requires_js": False
    },
    "jobstreet": {
        "template": "https://www.jobstreet.vn/en/job-search/{kw}-in-{city}/",
        "requires_js": True
    },
    "mywork": {
        "template": "https://www.mywork.com.vn/tim-kiem-viec-lam?keyword={kw}&place={city}",
        "requires_js": False
    },
    "vieclam24h": {
        "template": "https://vieclam24h.vn/tim-kiem-viec-lam.html?keyword={kw}&city={city}",
        "requires_js": False
    },
    "timviecnhanh": {
        "template": "https://www.timviecnhanh.com/tim-kiem-viec-lam.html?keyword={kw}&city={city}",
        "requires_js": False
    },
    "careerbuilder": {
        "template": "https://careerbuilder.vn/viec-lam?keywords={kw}&locations={city}",
        "requires_js": False
    },
    "indeed": {
        "template": "https://www.indeed.com.vn/jobs?q={kw}&l={city}",
        "requires_js": False
    },
    "linkedin": {
        "template": "https://www.linkedin.com/jobs/search?keywords={kw}&location={city}",
        "requires_js": True
    },
    "angelco": {
        "template": "https://angel.co/jobs?query={kw}&location=Vietnam",
        "requires_js": False
    },
    "company_careers": {
        "template": "{company_careers_url}",
        "requires_js": False
    }
}


def generate_seeds():
    seeds = []
    now = datetime.utcnow().isoformat() + 'Z'
    for src, meta in SOURCES.items():
        # Skip company_careers template — requires per-company URL input handled separately
        if "{company_careers_url}" in meta.get("template", ""):
            continue
        for prov in PROVINCES:
            for kw in KEYWORDS:
                q = meta["template"].format(kw=kw.replace(' ', '+'), city=prov.replace(' ', '+'))
                seeds.append({
                    "platform": src,
                    "query_url": q,
                    "province_city": prov,
                    "keyword": kw,
                    "requires_js": meta["requires_js"],
                    "generated_at": now
                })
    return seeds


def main():
    seeds = generate_seeds()
    out = {
        "generated_at": datetime.utcnow().isoformat() + 'Z',
        "seed_count": len(seeds),
        "seeds": seeds
    }
    import os
    os.makedirs('tmp', exist_ok=True)
    with open('tmp/seed_queries.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"✅ Generated seed_queries.json with {len(seeds)} entries -> tmp/seed_queries.json")


if __name__ == '__main__':
    main()
