#!/usr/bin/env python3
"""
New Cases Scanner
Periodically scans for new cases from various sources and alerts on changes.
"""

import os, sys, json, time, logging, requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SOURCES = {
    "supreme_court": "https://www.supremecourt.gov.pk/",
    "shc": "https://sindhhighcourt.gov.pk/",
    "lhc": "https://lahorehighcourt.gov.pk/",
    "phc": "https://peshawarhighcourt.gov.pk/",
    "bhc": "https://bhc.gov.pk/",
}

OUTPUT_DIR = "/tmp/new_cases"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        return r.text if r.status_code == 200 else None
    except Exception as e:
        logging.warning(f"Failed to fetch {url}: {e}")
        return None


def scan_source(name, url):
    """Scan a single source for new case listings."""
    logging.info(f"Scanning {name}...")
    html = fetch(url)
    if not html:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    cases = []
    
    # Look for common patterns - links to judgments, case listings, etc.
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        
        # Filter for likely case-related links
        case_indicators = ["judgment", "case", "order", "decision", "verdict"]
        if any(ind in href.lower() or ind in text.lower() for ind in case_indicators):
            cases.append({
                "source": name,
                "title": text[:200],
                "url": href if href.startswith("http") else f"{url.rstrip('/')}/{href.lstrip('/')}",
                "scanned_at": datetime.now().isoformat()
            })
    
    logging.info(f"  Found {len(cases)} potential cases from {name}")
    return cases


def load_previous():
    """Load previously scanned cases."""
    path = os.path.join(OUTPUT_DIR, "previous_scan.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []


def save_current(cases):
    """Save current scan results."""
    path = os.path.join(OUTPUT_DIR, "previous_scan.json")
    with open(path, "w") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)


def find_new_cases(current, previous):
    """Find cases that weren't in the previous scan."""
    prev_urls = {c["url"] for c in previous}
    return [c for c in current if c["url"] not in prev_urls]


def save_new_cases(new_cases):
    """Save newly discovered cases."""
    if not new_cases:
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUTPUT_DIR, f"new_cases_{timestamp}.json")
    with open(path, "w") as f:
        json.dump(new_cases, f, ensure_ascii=False, indent=2)
    logging.info(f"Saved {len(new_cases)} new cases to {path}")


def main():
    logging.info("=" * 50)
    logging.info("New Cases Scanner")
    logging.info("=" * 50)
    
    previous = load_previous()
    all_cases = []
    
    for name, url in SOURCES.items():
        cases = scan_source(name, url)
        all_cases.extend(cases)
        time.sleep(1)
    
    new_cases = find_new_cases(all_cases, previous)
    
    if new_cases:
        logging.info(f"\n*** {len(new_cases)} NEW CASES FOUND ***")
        for c in new_cases[:10]:
            logging.info(f"  - {c['title'][:60]}... ({c['source']})")
        save_new_cases(new_cases)
    else:
        logging.info("No new cases found.")
    
    save_current(all_cases)
    logging.info(f"Total cases tracked: {len(all_cases)}")


if __name__ == "__main__":
    main()
