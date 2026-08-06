#!/usr/bin/env python3
"""
pls_main_scraper.py
Main scraper for Pakistan Law Site that discovers and indexes all case types.
"""

import os, sys, json, re, time, logging, requests
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://www.pakistanlawsite.com"
OUTPUT_DIR = "/tmp/pls_scraped"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                return r.text
        except Exception as e:
            logger.warning(f"Fetch error: {e}")
        time.sleep(2 ** attempt)
    return None


def extract_case_ids(html):
    """Extract case type IDs from a page."""
    ids = []
    if not html:
        return ids
    
    # Find casetypeid attributes
    found = re.findall(r'casetypeid="([^"]+)"', html)
    ids.extend(found)
    
    # Find IDs in URLs
    url_ids = re.findall(r'[?&]caseid=([^&"]+)', html)
    ids.extend(url_ids)
    
    return list(set(ids))


def scrape_all_case_types():
    """Scrape all case type listings."""
    logger.info("Scraping all case types...")
    
    case_types = {
        'civil': 'CivilPage',
        'criminal': 'CriminalPage',
        'constitutional': 'ConstitutionalPage',
        'tax': 'TaxPage',
        'family': 'FamilyPage',
        'service': 'ServicePage',
        'commercial': 'CommercialPage',
        'company': 'CompanyPage',
    }
    
    all_cases = []
    
    for ctype, page in case_types.items():
        url = f"{BASE_URL}/Login/{page}"
        html = fetch(url)
        if html:
            case_ids = extract_case_ids(html)
            logger.info(f"  {ctype}: {len(case_ids)} case IDs found")
            
            for cid in case_ids:
                all_cases.append({
                    'case_type_id': cid,
                    'category': ctype,
                    'source': 'pls_main',
                    'scraped_at': datetime.utcnow().isoformat()
                })
        
        time.sleep(1)
    
    return all_cases


def save_cases(cases):
    filename = f"all_cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(cases)} cases to {filepath}")


def main():
    logger.info("=" * 50)
    logger.info("PLS Main Scraper")
    logger.info("=" * 50)
    
    cases = scrape_all_case_types()
    
    if cases:
        save_cases(cases)
    
    logger.info(f"Total cases discovered: {len(cases)}")


if __name__ == "__main__":
    main()
