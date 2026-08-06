"""
Turbo List Scraper - Fast list scraper for PLS
"""
import json
import requests
from bs4 import BeautifulSoup
import concurrent.futures

BASE_URL = "https://www.pls-beta.com"

class TurboListScraper:
    def __init__(self, max_workers=30):
        self.max_workers = max_workers

    def fetch_page(self, page):
        url = f"{BASE_URL}/cases?page={page}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                return []
            soup = BeautifulSoup(resp.text, 'html.parser')
            cases = []
            for item in soup.select('.case-item'):
                cases.append({
                    'title': item.select_one('.title').get_text(strip=True) if item.select_one('.title') else None,
                    'url': item.select_one('a')['href'] if item.select_one('a') else None,
                })
            return cases
        except Exception as e:
            return []

    def scrape_pages(self, start, end):
        all_cases = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_page = {executor.submit(self.fetch_page, page): page for page in range(start, end + 1)}
            for future in concurrent.futures.as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    cases = future.result()
                    all_cases.extend(cases)
                    print(f"Page {page}: {len(cases)} cases")
                except Exception as e:
                    print(f"Error for page {page}: {e}")
        return all_cases

if __name__ == '__main__':
    scraper = TurboListScraper()
    cases = scraper.scrape_pages(1, 10)
    print(f"Total cases: {len(cases)}")
    with open('turbo_list_cases.json', 'w') as f:
        json.dump(cases, f, indent=2)
