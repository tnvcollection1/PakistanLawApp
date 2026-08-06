"""
List Extractor - Extract case lists from PLS pages
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class ListExtractor:
    def __init__(self):
        self.session = requests.Session()

    def extract_list(self, url, selector='.case-list-item'):
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = []
        for element in soup.select(selector):
            items.append({
                'title': element.select_one('.title').get_text(strip=True) if element.select_one('.title') else None,
                'url': element.select_one('a')['href'] if element.select_one('a') else None,
                'date': element.select_one('.date').get_text(strip=True) if element.select_one('.date') else None,
            })
        return items

if __name__ == '__main__':
    extractor = ListExtractor()
    items = extractor.extract_list(f"{BASE_URL}/cases")
    print(json.dumps(items, indent=2))
