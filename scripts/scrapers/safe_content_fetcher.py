"""
Safe Content Fetcher - Robust content fetching with retries and error handling
"""
import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class SafeContentFetcher:
    def __init__(self, max_retries=3, backoff_factor=1, timeout=30):
        self.session = requests.Session()
        retries = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.timeout = timeout

    def fetch(self, url, **kwargs):
        try:
            resp = self.session.get(url, timeout=self.timeout, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def fetch_with_delay(self, url, delay=(1, 3)):
        time.sleep(random.uniform(*delay))
        return self.fetch(url)

if __name__ == '__main__':
    fetcher = SafeContentFetcher()
    url = "https://example.com"
    resp = fetcher.fetch(url)
    if resp:
        print(f"Fetched {len(resp.text)} chars from {url}")
