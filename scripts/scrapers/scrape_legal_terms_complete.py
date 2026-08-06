"""
Scrape Legal Terms Complete - Comprehensive legal terms scraper
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class LegalTermsScraper:
    def __init__(self):
        self.session = requests.Session()

    def scrape_terms(self, page=1):
        url = f"{BASE_URL}/legal-terms?page={page}"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        terms = []
        for item in soup.select('.term-item'):
            terms.append({
                'term': item.select_one('.term-name').get_text(strip=True) if item.select_one('.term-name') else None,
                'definition': item.select_one('.term-definition').get_text(strip=True) if item.select_one('.term-definition') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
            })
        return terms

if __name__ == '__main__':
    scraper = LegalTermsScraper()
    terms = scraper.scrape_terms(1)
    print(json.dumps(terms, indent=2))
