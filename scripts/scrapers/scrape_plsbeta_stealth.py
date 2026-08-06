"""
Pakistan Legal Scraper - Stealth mode scraper for PLS Beta
"""
import json
import os
import random
import sys
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://pls-beta.com"
CASES_URL = f"{BASE_URL}/cases"
STATUTES_URL = f"{BASE_URL}/statutes"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

class StealthScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.delay = (1, 3)

    def get(self, url, **kwargs):
        time.sleep(random.uniform(*self.delay))
        return self.session.get(url, **kwargs)

    def scrape_case_list(self, page=1):
        url = f"{CASES_URL}?page={page}"
        resp = self.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        cases = []
        for item in soup.select(".case-list-item"):
            cases.append({
                "title": item.select_one(".case-title").get_text(strip=True) if item.select_one(".case-title") else None,
                "citation": item.select_one(".case-citation").get_text(strip=True) if item.select_one(".case-citation") else None,
                "url": item.select_one("a")["href"] if item.select_one("a") else None,
            })
        return cases

    def scrape_case_detail(self, url):
        resp = self.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        content = soup.select_one(".case-content")
        return content.get_text(strip=True) if content else None

    def scrape_statute_list(self, page=1):
        url = f"{STATUTES_URL}?page={page}"
        resp = self.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        statutes = []
        for item in soup.select(".statute-list-item"):
            statutes.append({
                "title": item.select_one(".statute-title").get_text(strip=True) if item.select_one(".statute-title") else None,
                "url": item.select_one("a")["href"] if item.select_one("a") else None,
            })
        return statutes

    def scrape_statute_detail(self, url):
        resp = self.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        content = soup.select_one(".statute-content")
        return content.get_text(strip=True) if content else None

if __name__ == "__main__":
    scraper = StealthScraper()
    cases = scraper.scrape_case_list(1)
    print(json.dumps(cases, indent=2))
