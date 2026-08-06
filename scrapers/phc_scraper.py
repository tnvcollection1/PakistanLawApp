#!/usr/bin/env python3
"""
Peshawar High Court (PHC) Scraper
Extracts case listings, judgments, and cause lists from the PHC website.
"""

import os, sys, re, json, time, logging, requests
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_URL = "https://peshawarhighcourt.gov.pk"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "scraped_data", "phc")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_page(url, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                return r.text
        except Exception as e:
            logging.warning(f"Attempt {attempt+1} failed: {e}")
        time.sleep(2 ** attempt)
    return None


def parse_judgments(html):
    """Parse judgment listings from PHC website."""
    soup = BeautifulSoup(html, "html.parser")
    judgments = []
    
    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) >= 3:
            judgments.append({
                "case_no": cols[0].get_text(strip=True),
                "title": cols[1].get_text(strip=True),
                "date": cols[2].get_text(strip=True),
                "source": "phc",
                "scraped_at": datetime.now().isoformat()
            })
    
    return judgments


def parse_cause_list(html):
    """Parse daily cause list from PHC."""
    soup = BeautifulSoup(html, "html.parser")
    cases = []
    
    for item in soup.find_all("div", class_=re.compile("cause|case", re.I)):
        text = item.get_text(strip=True)
        if text:
            cases.append({
                "details": text[:500],
                "source": "phc_cause_list",
                "scraped_at": datetime.now().isoformat()
            })
    
    return cases


def scrape_judgments():
    logging.info("Scraping PHC judgments...")
    url = f"{BASE_URL}/judgments"
    html = fetch_page(url)
    if html:
        judgments = parse_judgments(html)
        out_path = os.path.join(OUTPUT_DIR, f"judgments_{datetime.now().strftime('%Y%m%d')}.json")
        with open(out_path, "w") as f:
            json.dump(judgments, f, ensure_ascii=False, indent=2)
        logging.info(f"Saved {len(judgments)} judgments to {out_path}")
        return judgments
    return []


def scrape_cause_list():
    logging.info("Scraping PHC cause list...")
    url = f"{BASE_URL}/cause-list"
    html = fetch_page(url)
    if html:
        cases = parse_cause_list(html)
        out_path = os.path.join(OUTPUT_DIR, f"cause_list_{datetime.now().strftime('%Y%m%d')}.json")
        with open(out_path, "w") as f:
            json.dump(cases, f, ensure_ascii=False, indent=2)
        logging.info(f"Saved {len(cases)} cause list entries to {out_path}")
        return cases
    return []


def main():
    logging.info("=" * 50)
    logging.info("Peshawar High Court Scraper")
    logging.info("=" * 50)
    
    judgments = scrape_judgments()
    time.sleep(2)
    cause_list = scrape_cause_list()
    
    logging.info(f"\nTotal: {len(judgments)} judgments, {len(cause_list)} cause list entries")


if __name__ == "__main__":
    main()
