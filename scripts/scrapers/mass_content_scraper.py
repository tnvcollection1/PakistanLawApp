"""
Mass Content Scraper - Large-scale content scraper for PLS
"""
import json
import requests
from bs4 import BeautifulSoup
import concurrent.futures

BASE_URL = "https://www.pls-beta.com"

class MassContentScraper:
    def __init__(self, max_workers=20):
        self.max_workers = max_workers

    def fetch_content(self, url):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                return None
            soup = BeautifulSoup(resp.text, 'html.parser')
            content = soup.select_one('.content')
            return content.get_text(strip=True) if content else None
        except Exception as e:
            return None

    def scrape_urls(self, urls):
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.fetch_content, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    print(f"Error for {url}: {e}")
                    results[url] = None
        return results

if __name__ == '__main__':
    scraper = MassContentScraper()
    urls = [f"{BASE_URL}/cases/{i}" for i in range(1, 11)]
    results = scraper.scrape_urls(urls)
    print(f"Fetched content for {len(results)} URLs")
    with open('mass_content.json', 'w') as f:
        json.dump(results, f, indent=2)
