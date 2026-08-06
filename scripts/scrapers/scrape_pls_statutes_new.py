"""
Scrape PLS Statutes New - New statute scraper for PLS
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class NewPLSStatuteScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def scrape_statute_categories(self):
        url = f"{BASE_URL}/statute-categories"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        categories = []
        for item in soup.select('.category-item'):
            categories.append({
                'name': item.select_one('.category-name').get_text(strip=True) if item.select_one('.category-name') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
            })
        return categories

    def scrape_statute_list(self, category_url):
        resp = self.session.get(category_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        statutes = []
        for item in soup.select('.statute-item'):
            statutes.append({
                'title': item.select_one('.statute-title').get_text(strip=True) if item.select_one('.statute-title') else None,
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
    scraper = NewPLSStatuteScraper()
    categories = scraper.scrape_statute_categories()
    print(json.dumps(categories, indent=2))
