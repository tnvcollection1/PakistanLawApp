"""
Case List Scraper - Scraper for case lists from PLS
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class CaseListScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def scrape_case_list(self, page=1):
        url = f"{BASE_URL}/cases?page={page}"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        cases = []
        for item in soup.select('.case-list-item'):
            cases.append({
                'title': item.select_one('.case-title').get_text(strip=True) if item.select_one('.case-title') else None,
                'citation': item.select_one('.case-citation').get_text(strip=True) if item.select_one('.case-citation') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
                'date': item.select_one('.case-date').get_text(strip=True) if item.select_one('.case-date') else None,
            })
        return cases

if __name__ == '__main__':
    scraper = CaseListScraper()
    cases = scraper.scrape_case_list(1)
    print(json.dumps(cases, indent=2))
