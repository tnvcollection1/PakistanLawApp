"""
Simple ID Scraper - Basic ID-based scraper for PLS cases
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class SimpleIdScraper:
    def __init__(self):
        self.session = requests.Session()

    def scrape_case(self, case_id):
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

    def scrape_range(self, start, end):
        results = []
        for case_id in range(start, end + 1):
            case = self.scrape_case(case_id)
            if case:
                results.append(case)
        return results

if __name__ == '__main__':
    scraper = SimpleIdScraper()
    results = scraper.scrape_range(1, 10)
    print(json.dumps(results, indent=2))
