#!/usr/bin/env python3
"""
pls_api_scraper.py
Scraper using Pakistan Law Site API endpoints.
"""

import os, sys, json, re, time, logging, requests
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://www.pakistanlawsite.com"
OUTPUT_DIR = "/tmp/pls_api"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/javascript, */*",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_json(url, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            logger.warning(f"Fetch error: {e}")
        time.sleep(2 ** attempt)
    return None


def fetch_html(url, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                return r.text
        except Exception as e:
            logger.warning(f"Fetch error: {e}")
        time.sleep(2 ** attempt)
    return None


def scrape_search_results(keyword):
    """Scrape search results for a keyword."""
    logger.info(f"Searching for '{keyword}'...")
    url = f"{BASE_URL}/Login/Search?keyword={keyword}"
    html = fetch_html(url)
    if not html:
        return []
    
    # Extract case references
    citations = re.findall(r'(\d{4})\s+(PLD|SCMR|CLC|PCrLJ|YLR|MLD|PLC|PTD)\s+(\d+)', html)
    cases = []
    for c in citations:
        cases.append({
            'year': c[0],
            'journal': c[1],
            'page': c[2],
            'citation': f"{c[0]} {c[1]} {c[2]}",
            'source': 'pls_api_search',
            'scraped_at': datetime.utcnow().isoformat()
        })
    
    logger.info(f"  Found {len(cases)} citations")
    return cases


def save_data(data, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"  Saved to {filepath}")


def main():
    logger.info("=" * 50)
    logger.info("PLS API Scraper")
    logger.info("=" * 50)
    
    keywords = ['constitution', 'criminal', 'civil', 'tax', 'property']
    all_cases = []
    
    for kw in keywords:
        cases = scrape_search_results(kw)
        all_cases.extend(cases)
        time.sleep(1)
    
    if all_cases:
        save_data(all_cases, f"search_results_{datetime.now().strftime('%Y%m%d')}.json")
    
    logger.info("=" * 50)
    logger.info("Complete")
    logger.info(f"  Total cases: {len(all_cases)}")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
