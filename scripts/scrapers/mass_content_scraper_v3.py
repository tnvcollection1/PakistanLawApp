"""
Mass Content Scraper V3 - Mass content scraper with batching
"""
import json
import requests
from bs4 import BeautifulSoup
import concurrent.futures

BASE_URL = "https://www.pls-beta.com"

class MassContentScraperV3:
    def __init__(self, max_workers=50, batch_size=100):
        self.max_workers = max_workers
        self.batch_size = batch_size

    def fetch_content(self, url):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                return None
            soup = BeautifulSoup(resp.text, 'html.parser')
            content = soup.select_one('.content')
            return content.get_text(strip=True) if content else None
        except Exception as e:
            return None

    def scrape_batch(self, urls):
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

    def scrape_all(self, urls):
        all_results = {}
        for i in range(0, len(urls), self.batch_size):
            batch = urls[i:i + self.batch_size]
            print(f"Processing batch {i // self.batch_size + 1}: {len(batch)} URLs")
            results = self.scrape_batch(batch)
            all_results.update(results)
        return all_results

if __name__ == '__main__':
    scraper = MassContentScraperV3()
    urls = [f"{BASE_URL}/cases/{i}" for i in range(1, 101)]
    results = scraper.scrape_all(urls)
    print(f"Fetched {len(results)} items")
    with open('mass_content_v3.json', 'w') as f:
        json.dump(results, f, indent=2)
