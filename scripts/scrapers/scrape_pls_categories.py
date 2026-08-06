"""
Scrape PLS Categories - Category scraper for PLS
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class PLSCategoryScraper:
    def __init__(self):
        self.session = requests.Session()

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
                'description': item.select_one('.category-description').get_text(strip=True) if item.select_one('.category-description') else None,
            })
        return categories

    def scrape_category_cases(self, url):
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        cases = []
        for item in soup.select('.case-item'):
            cases.append({
                'title': item.select_one('.case-title').get_text(strip=True) if item.select_one('.case-title') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
                'date': item.select_one('.case-date').get_text(strip=True) if item.select_one('.case-date') else None,
            })
        return cases

if __name__ == '__main__':
    scraper = PLSCategoryScraper()
    categories = scraper.scrape_categories()
    print(json.dumps(categories, indent=2))
