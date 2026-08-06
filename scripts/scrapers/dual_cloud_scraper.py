"""
Dual Cloud Scraper - Dual-cloud scraper with failover
"""
import json
import requests

BASE_URLS = [
    "https://www.pls-beta.com",
    "https://www.eastlaw.pk",
]

class DualCloudScraper:
    def __init__(self):
        self.sessions = [requests.Session() for _ in BASE_URLS]

    def fetch(self, endpoint, fallback=True):
        for i, session in enumerate(self.sessions):
            url = f"{BASE_URLS[i]}{endpoint}"
            try:
                resp = session.get(url, timeout=30)
                if resp.status_code == 200:
                    return resp.text
            except Exception as e:
                print(f"Error with {url}: {e}")
                continue
        return None

    def fetch_cases(self, query):
        results = []
        for i, session in enumerate(self.sessions):
            url = f"{BASE_URLS[i]}/search?q={query}"
            try:
                resp = session.get(url, timeout=30)
                if resp.status_code == 200:
                    results.append({'source': BASE_URLS[i], 'content': resp.text[:500]})
            except Exception as e:
                print(f"Error with {url}: {e}")
        return results

if __name__ == '__main__':
    scraper = DualCloudScraper()
    content = scraper.fetch("/cases/1")
    print(f"Fetched {len(content) if content else 0} chars")
