#!/usr/bin/env python3
"""Scrape courts list from PLS Beta."""

import requests
import json
from pathlib import Path

BASE_URL = "https://beta.pakistanlawsite.com"
OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
}

def fetch_courts():
    url = f"{BASE_URL}/api/courts"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching courts: {e}")
        return None

def main():
    data = fetch_courts()
    if data:
        courts = data.get('courts', [])
        output_file = OUTPUT_DIR / "courts.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(courts, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(courts)} courts to {output_file}")
        for court in courts:
            print(f"  - {court.get('name', '')}")

if __name__ == '__main__':
    main()
