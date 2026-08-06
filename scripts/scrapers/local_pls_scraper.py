"""
Local PLS Scraper - Local development scraper for PLS
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:3000"

class LocalPLSScraper:
    def __init__(self):
        self.session = requests.Session()

    def scrape_cases(self, page=1):
        url = f"{BASE_URL}/cases?page={page}"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        cases = []
        for item in soup.select('.case-item'):
            cases.append({
                'title': item.select_one('.title').get_text(strip=True) if item.select_one('.title') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
            })
        return cases

    def scrape_case_detail(self, case_id):
        url = f"{BASE_URL}/cases/{case_id}"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return {
            'title': soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else None,
            'content': soup.select_one('.content').get_text(strip=True) if soup.select_one('.content') else None,
        }

if __name__ == '__main__':
    scraper = LocalPLSScraper()
    cases = scraper.scrape_cases(1)
    print(json.dumps(cases, indent=2))
