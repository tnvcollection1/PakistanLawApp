"""
Cloud Scraper - Cloud-based scraper for distributed scraping
"""
import json
import requests
from bs4 import BeautifulSoup
import concurrent.futures

BASE_URL = "https://www.pls-beta.com"

class CloudScraper:
    def __init__(self, max_workers=20):
        self.max_workers = max_workers
        self.session = requests.Session()

    def fetch_case(self, case_id):
        url = f"{BASE_URL}/cases/{case_id}"
        resp = self.session.get(url)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        return {
            'id': case_id,
            'title': soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else None,
            'content': soup.select_one('.content').get_text(strip=True) if soup.select_one('.content') else None,
        }

    def fetch_multiple(self, case_ids):
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_id = {executor.submit(self.fetch_case, cid): cid for cid in case_ids}
            for future in concurrent.futures.as_completed(future_to_id):
                case_id = future_to_id[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"Error fetching case {case_id}: {e}")
        return results

if __name__ == '__main__':
    scraper = CloudScraper()
    results = scraper.fetch_multiple(range(1, 11))
    print(f"Fetched {len(results)} cases")
    print(json.dumps(results[:3], indent=2))
