"""
Advance Search Extractor - Extract advanced search results
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class AdvanceSearchExtractor:
    def __init__(self):
        self.session = requests.Session()

    def search(self, query, filters=None):
        url = f"{BASE_URL}/search"
        params = {'q': query}
        if filters:
            params.update(filters)
        resp = self.session.get(url, params=params)
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        for item in soup.select('.search-result'):
            results.append({
                'title': item.select_one('.title').get_text(strip=True) if item.select_one('.title') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
                'snippet': item.select_one('.snippet').get_text(strip=True) if item.select_one('.snippet') else None,
                'type': item.select_one('.type').get_text(strip=True) if item.select_one('.type') else None,
            })
        return results

if __name__ == '__main__':
    extractor = AdvanceSearchExtractor()
    results = extractor.search("property law")
    print(json.dumps(results, indent=2))
