"""
Fast Fetch Content - Fast content fetching with caching
"""
import json
import requests
from functools import lru_cache

BASE_URL = "https://www.pls-beta.com"

class FastContentFetcher:
    def __init__(self):
        self.session = requests.Session()

    @lru_cache(maxsize=1000)
    def fetch(self, url):
        resp = self.session.get(url, timeout=30)
        return resp.text if resp.status_code == 200 else None

    def fetch_case(self, case_id):
        url = f"{BASE_URL}/cases/{case_id}"
        return self.fetch(url)

    def fetch_statute(self, statute_id):
        url = f"{BASE_URL}/statutes/{statute_id}"
        return self.fetch(url)

if __name__ == '__main__':
    fetcher = FastContentFetcher()
    content = fetcher.fetch_case('1')
    print(f"Fetched {len(content) if content else 0} chars")
