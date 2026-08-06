"""
Scrape PLS Working - Working PLS scraper with basic functionality
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class PLSWorkingScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

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

    def scrape_statutes(self, page=1):
        url = f"{BASE_URL}/statutes?page={page}"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        statutes = []
        for item in soup.select('.statute-item'):
            statutes.append({
                'title': item.select_one('.title').get_text(strip=True) if item.select_one('.title') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
            })
        return statutes

if __name__ == '__main__':
    scraper = PLSWorkingScraper()
    cases = scraper.scrape_cases(1)
    print(f"Scraped {len(cases)} cases")
    print(json.dumps(cases[:3], indent=2))
