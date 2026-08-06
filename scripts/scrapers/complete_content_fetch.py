"""
Complete Content Fetch - Fetch complete content for all cases
"""
import json
import requests
from bs4 import BeautifulSoup
import concurrent.futures

BASE_URL = "https://www.pls-beta.com"

class CompleteContentFetcher:
    def __init__(self, max_workers=20):
        self.max_workers = max_workers

    def fetch_content(self, url):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                return None
            soup = BeautifulSoup(resp.text, 'html.parser')
            title = soup.select_one('h1')
            content = soup.select_one('.content')
            return {
                'title': title.get_text(strip=True) if title else None,
                'content': content.get_text(strip=True) if content else None,
            }
        except Exception as e:
            return None

    def fetch_all(self, urls):
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.fetch_content, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"Error for {url}: {e}")
        return results

if __name__ == '__main__':
    fetcher = CompleteContentFetcher()
    urls = [f"{BASE_URL}/cases/{i}" for i in range(1, 11)]
    results = fetcher.fetch_all(urls)
    print(f"Fetched {len(results)} items")
    with open('complete_content.json', 'w') as f:
        json.dump(results, f, indent=2)
