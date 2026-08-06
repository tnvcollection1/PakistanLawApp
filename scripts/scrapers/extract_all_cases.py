"""
Extract All Cases - Extract all cases from PLS with pagination
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class AllCaseExtractor:
    def __init__(self):
        self.session = requests.Session()

    def extract_all(self, max_pages=10):
        all_cases = []
        for page in range(1, max_pages + 1):
            url = f"{BASE_URL}/cases?page={page}"
            resp = self.session.get(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            cases = []
            for item in soup.select('.case-item'):
                cases.append({
                    'title': item.select_one('.title').get_text(strip=True) if item.select_one('.title') else None,
                    'url': item.select_one('a')['href'] if item.select_one('a') else None,
                })
            if not cases:
                break
            all_cases.extend(cases)
            print(f"Extracted page {page}: {len(cases)} cases")
        return all_cases

if __name__ == '__main__':
    extractor = AllCaseExtractor()
    cases = extractor.extract_all(5)
    print(f"Total cases: {len(cases)}")
    with open('all_cases.json', 'w') as f:
        json.dump(cases, f, indent=2)
