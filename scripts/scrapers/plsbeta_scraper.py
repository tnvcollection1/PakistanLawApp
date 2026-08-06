#!/usr/bin/env python3
"""
plsbeta_scraper.py
Scraper for Pakistan Law Site Beta version.
"""

import os, sys, json, re, time, logging, requests
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://www.pakistanlawsite.com"
OUTPUT_DIR = "/tmp/plsbeta"
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


def scrape_cases():
    logger.info("Scraping cases from PLS Beta...")
    html = fetch(f"{BASE_URL}/Login/CaseSearch")
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    cases = []
    
    for row in soup.find_all('tr', class_='caseType'):
        case_id = row.get('casetypeid', '')
        text = row.get_text(strip=True)
        if case_id or text:
            cases.append({
                'case_id': case_id,
                'text': text[:500],
                'source': 'plsbeta_cases',
                'scraped_at': datetime.utcnow().isoformat()
            })
    
    logger.info(f"  Found {len(cases)} cases")
    return cases


def scrape_statutes():
    logger.info("Scraping statutes from PLS Beta...")
    html = fetch(f"{BASE_URL}/Login/StatuePage")
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    statutes = []
    
    for row in soup.find_all('tr', class_='caseType'):
        case_id = row.get('casetypeid', '')
        text = row.get_text(strip=True)
        if case_id or text:
            statutes.append({
                'statute_id': case_id,
                'name': text[:500],
                'source': 'plsbeta_statutes',
                'scraped_at': datetime.utcnow().isoformat()
            })
    
    logger.info(f"  Found {len(statutes)} statutes")
    return statutes


def save_data(data, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"  Saved to {filepath}")


def main():
    logger.info("=" * 50)
    logger.info("PLS Beta Scraper")
    logger.info("=" * 50)
    
    cases = scrape_cases()
    if cases:
        save_data(cases, f"cases_{datetime.now().strftime('%Y%m%d')}.json")
    
    statutes = scrape_statutes()
    if statutes:
        save_data(statutes, f"statutes_{datetime.now().strftime('%Y%m%d')}.json")
    
    logger.info("=" * 50)
    logger.info("Complete")
    logger.info(f"  Cases: {len(cases)}")
    logger.info(f"  Statutes: {len(statutes)}")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
