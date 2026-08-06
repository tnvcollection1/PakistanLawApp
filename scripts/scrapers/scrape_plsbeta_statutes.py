"""
Scrape PLS Beta Statutes - Statute scraper for PLS Beta
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class PLSBetaStatuteScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def scrape_statute_list(self, page=1):
        url = f"{BASE_URL}/statutes?page={page}"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        statutes = []
        for item in soup.select('.statute-item'):
            statutes.append({
                'title': item.select_one('.statute-title').get_text(strip=True) if item.select_one('.statute-title') else None,
                'year': item.select_one('.statute-year').get_text(strip=True) if item.select_one('.statute-year') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
            })
        return statutes

    def scrape_statute_detail(self, url):
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return {
            'title': soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else None,
            'content': soup.select_one('.statute-content').get_text(strip=True) if soup.select_one('.statute-content') else None,
        }

if __name__ == '__main__':
    scraper = PLSBetaStatuteScraper()
    statutes = scraper.scrape_statute_list(1)
    print(json.dumps(statutes, indent=2))
