#!/usr/bin/env python3
"""Scraper for PLS Beta site."""

import requests
from bs4 import BeautifulSoup
import json
import sys

BASE_URL = "https://beta.pakistanlawsite.com"


def fetch_page(path):
    url = f"{BASE_URL}{path}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def scrape_cases():
    soup = fetch_page("/cases")
    cases = []
    for item in soup.select(".case-item"):
        title = item.select_one(".case-title")
        court = item.select_one(".case-court")
        date = item.select_one(".case-date")
        if title:
            cases.append({
                "title": title.get_text(strip=True),
                "court": court.get_text(strip=True) if court else None,
                "date": date.get_text(strip=True) if date else None,
                "url": BASE_URL + title.get("href", "") if title.get("href") else None,
            })
    return cases


def main():
    cases = scrape_cases()
    print(json.dumps(cases, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
