"""
Scrape All Categories v2 - Improved category scraper
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class CategoryScraperV2:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def scrape_categories(self):
        url = f"{BASE_URL}/categories"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        categories = []
        for item in soup.select('.category-item'):
            categories.append({
                'name': item.select_one('.category-name').get_text(strip=True) if item.select_one('.category-name') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
                'count': item.select_one('.category-count').get_text(strip=True) if item.select_one('.category-count') else None,
            })
        return categories

    def scrape_category_detail(self, url):
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        cases = []
        for item in soup.select('.case-item'):
            cases.append({
                'title': item.select_one('.case-title').get_text(strip=True) if item.select_one('.case-title') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
            })
        return cases

if __name__ == '__main__':
    scraper = CategoryScraperV2()
    categories = scraper.scrape_categories()
    print(json.dumps(categories, indent=2))
