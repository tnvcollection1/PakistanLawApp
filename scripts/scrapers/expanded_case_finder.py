"""
Expanded Case Finder - Find cases with expanded search criteria
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class ExpandedCaseFinder:
    def __init__(self):
        self.session = requests.Session()

    def search_cases(self, query, year=None, court=None):
        params = {'q': query}
        if year:
            params['year'] = year
        if court:
            params['court'] = court
        url = f"{BASE_URL}/search"
        resp = self.session.get(url, params=params)
        soup = BeautifulSoup(resp.text, 'html.parser')
        cases = []
        for item in soup.select('.search-result'):
            cases.append({
                'title': item.select_one('.title').get_text(strip=True) if item.select_one('.title') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
                'citation': item.select_one('.citation').get_text(strip=True) if item.select_one('.citation') else None,
                'date': item.select_one('.date').get_text(strip=True) if item.select_one('.date') else None,
                'court': item.select_one('.court').get_text(strip=True) if item.select_one('.court') else None,
            })
        return cases

if __name__ == '__main__':
    finder = ExpandedCaseFinder()
    cases = finder.search_cases("property", year=2023, court="Supreme Court")
    print(json.dumps(cases, indent=2))
