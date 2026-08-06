#!/usr/bin/env python3
"""
scrape_plsbeta_all.py
Scrapes all content types from Pakistan Law Site Beta.
"""

import os, sys, json, re, time, logging, requests
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://www.pakistanlawsite.com"
OUTPUT_DIR = "/tmp/plsbeta_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
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


def scrape_statutes():
    logger.info("Scraping statutes...")
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


def scrape_words():
    logger.info("Scraping words & phrases...")
    html = fetch(f"{BASE_URL}/Login/WordsAndPhrases?type=words")
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    words = []
    
    for link in soup.find_all('a', href=True):
        text = link.get_text(strip=True)
        if text and len(text) > 2:
            words.append({
                'word': text[:200],
                'source': 'plsbeta_words',
                'scraped_at': datetime.utcnow().isoformat()
            })
    
    logger.info(f"  Found {len(words)} words/phrases")
    return words


def scrape_maxims():
    logger.info("Scraping maxims...")
    html = fetch(f"{BASE_URL}/Login/Maxim?type=maxim")
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    maxims = []
    
    for elem in soup.find_all(['li', 'div']):
        text = elem.get_text(strip=True)
        if text and len(text) > 5:
            maxims.append({
                'maxim': text[:500],
                'source': 'plsbeta_maxims',
                'scraped_at': datetime.utcnow().isoformat()
            })
    
    logger.info(f"  Found {len(maxims)} maxims")
    return maxims


def save_data(data, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"  Saved to {filepath}")


def main():
    logger.info("=" * 50)
    logger.info("PLS Beta - All Content Scraper")
    logger.info("=" * 50)
    
    statutes = scrape_statutes()
    if statutes:
        save_data(statutes, f"statutes_{datetime.now().strftime('%Y%m%d')}.json")
    
    words = scrape_words()
    if words:
        save_data(words, f"words_{datetime.now().strftime('%Y%m%d')}.json")
    
    maxims = scrape_maxims()
    if maxims:
        save_data(maxims, f"maxims_{datetime.now().strftime('%Y%m%d')}.json")
    
    logger.info("=" * 50)
    logger.info("Scraping complete")
    logger.info(f"  Statutes: {len(statutes)}")
    logger.info(f"  Words: {len(words)}")
    logger.info(f"  Maxims: {len(maxims)}")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
