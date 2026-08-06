"""
Scrape with cookies - Session-based scraper for PLS
"""
import json
import os
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class CookieScraper:
    def __init__(self, cookies_file=None):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        })
        if cookies_file and os.path.exists(cookies_file):
            with open(cookies_file, 'r') as f:
                cookies = json.load(f)
                for c in cookies:
                    self.session.cookies.set(c['name'], c['value'])

    def get(self, url):
        resp = self.session.get(url)
        return resp

    def scrape_case(self, case_id):
        url = f"{BASE_URL}/cases/{case_id}"
        resp = self.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.select_one('h1')
        content = soup.select_one('.case-content')
        return {
            'title': title.get_text(strip=True) if title else None,
            'content': content.get_text(strip=True) if content else None,
        }

if __name__ == '__main__':
    scraper = CookieScraper()
    result = scraper.scrape_case('1')
    print(json.dumps(result, indent=2))
