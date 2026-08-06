"""
Scrape PLS Aggressive - Aggressive scraper with high concurrency
"""
import json
import requests
from bs4 import BeautifulSoup
import concurrent.futures

BASE_URL = "https://www.pls-beta.com"

class AggressiveScraper:
    def __init__(self, max_workers=50):
        self.max_workers = max_workers

    def fetch_case(self, case_id):
        url = f"{BASE_URL}/cases/{case_id}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                return None
            soup = BeautifulSoup(resp.text, 'html.parser')
            return {
                'id': case_id,
                'title': soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else None,
                'content': soup.select_one('.content').get_text(strip=True) if soup.select_one('.content') else None,
            }
        except Exception as e:
            return None

    def scrape_range(self, start, end):
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_id = {executor.submit(self.fetch_case, i): i for i in range(start, end + 1)}
            for future in concurrent.futures.as_completed(future_to_id):
                result = future.result()
                if result:
                    results.append(result)
        return results

if __name__ == '__main__':
    scraper = AggressiveScraper()
    results = scraper.scrape_range(1, 100)
    print(f"Scraped {len(results)} cases")
    with open('aggressive_results.json', 'w') as f:
        json.dump(results, f, indent=2)
