"""
Mass Content Scraper V2 - Improved mass content scraper
"""
import json
import requests
from bs4 import BeautifulSoup
import concurrent.futures

BASE_URL = "https://www.pls-beta.com"

class MassContentScraperV2:
    def __init__(self, max_workers=30):
        self.max_workers = max_workers

    def fetch_content(self, url):
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code != 200:
                return None
            soup = BeautifulSoup(resp.text, 'html.parser')
            content = soup.select_one('.content')
            return content.get_text(strip=True) if content else None
        except Exception as e:
            return None

    def scrape_ids(self, ids, id_type='case'):
        urls = [f"{BASE_URL}/{id_type}s/{i}" for i in ids]
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.fetch_content, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    results[url] = None
        return results

if __name__ == '__main__':
    scraper = MassContentScraperV2()
    ids = range(1, 11)
    results = scraper.scrape_ids(ids, 'case')
    print(f"Fetched {len(results)} items")
    with open('mass_content_v2.json', 'w') as f:
        json.dump(results, f, indent=2)
