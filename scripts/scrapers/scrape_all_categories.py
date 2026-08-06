"""
Scrape All Categories - Scrape all categories from PLS
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class AllCategoryScraper:
    def __init__(self):
        self.session = requests.Session()

    def scrape_all_categories(self):
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

    def scrape_all_subcategories(self, category_url):
        resp = self.session.get(category_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        subcategories = []
        for item in soup.select('.subcategory-item'):
            subcategories.append({
                'name': item.select_one('.subcategory-name').get_text(strip=True) if item.select_one('.subcategory-name') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
            })
        return subcategories

if __name__ == '__main__':
    scraper = AllCategoryScraper()
    categories = scraper.scrape_all_categories()
    print(json.dumps(categories, indent=2))
