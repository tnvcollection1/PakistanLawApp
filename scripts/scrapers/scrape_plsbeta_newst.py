"""
Scrape PLS Beta Newst - Newest scraper for PLS Beta
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class NewestScraper:
    def __init__(self):
        self.session = requests.Session()

    def scrape_latest(self, count=10):
        url = f"{BASE_URL}/latest"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        cases = []
        for item in soup.select('.latest-case')[:count]:
            cases.append({
                'id': item.get('data-id'),
                'title': item.select_one('.title').get_text(strip=True) if item.select_one('.title') else None,
                'date': item.select_one('.date').get_text(strip=True) if item.select_one('.date') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
            })
        return cases

    def scrape_trending(self, count=10):
        url = f"{BASE_URL}/trending"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        cases = []
        for item in soup.select('.trending-case')[:count]:
            cases.append({
                'id': item.get('data-id'),
                'title': item.select_one('.title').get_text(strip=True) if item.select_one('.title') else None,
                'views': item.select_one('.views').get_text(strip=True) if item.select_one('.views') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
            })
        return cases

if __name__ == '__main__':
    scraper = NewestScraper()
    latest = scraper.scrape_latest(5)
    print("Latest cases:")
    print(json.dumps(latest, indent=2))
    trending = scraper.scrape_trending(5)
    print("Trending cases:")
    print(json.dumps(trending, indent=2))
