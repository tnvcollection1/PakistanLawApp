#!/usr/bin/env python3
"""Comprehensive case list finder for PLS Beta."""

import requests
import json
import time
from pathlib import Path

BASE_URL = "https://beta.pakistanlawsite.com"
OUTPUT_DIR = Path("data/caselists")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
}

session = requests.Session()

def fetch_caselist(court=None, year=None, page=1):
    params = {"page": page}
    if court:
        params["court"] = court
    if year:
        params["year"] = year
    url = f"{BASE_URL}/api/cases"
    try:
        resp = session.get(url, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching caselist: {e}")
        return None

def find_all_caselists():
    all_cases = []
    courts = ["Supreme Court", "High Court", "Lahore High Court", "Sindh High Court"]
    years = list(range(1950, 2025))
    
    for court in courts:
        for year in years:
            print(f"Fetching {court} {year}...")
            page = 1
            while True:
                data = fetch_caselist(court, year, page)
                if not data:
                    break
                cases = data.get('cases', [])
                if not cases:
                    break
                all_cases.extend(cases)
                if not data.get('has_more', False):
                    break
                page += 1
                time.sleep(0.3)
    
    output_file = OUTPUT_DIR / "all_caselists.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_cases, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(all_cases)} cases to {output_file}")
    return all_cases

def main():
    find_all_caselists()

if __name__ == '__main__':
    main()
