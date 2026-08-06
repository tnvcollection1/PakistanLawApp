"""
Fetch PLS Content - Content fetcher for PLS cases and statutes
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class PLSContentFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def fetch_case(self, case_id):
        url = f"{BASE_URL}/cases/{case_id}"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return {
            'id': case_id,
            'title': soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else None,
            'content': soup.select_one('.case-content').get_text(strip=True) if soup.select_one('.case-content') else None,
            'citations': [c.get_text(strip=True) for c in soup.select('.citation')],
        }

    def fetch_statute(self, statute_id):
        url = f"{BASE_URL}/statutes/{statute_id}"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return {
            'id': statute_id,
            'title': soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else None,
            'content': soup.select_one('.statute-content').get_text(strip=True) if soup.select_one('.statute-content') else None,
        }

if __name__ == '__main__':
    fetcher = PLSContentFetcher()
    case = fetcher.fetch_case('1')
    print(json.dumps(case, indent=2))
