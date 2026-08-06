"""
EastLaw Scraper Final - Final version of EastLaw scraper
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.eastlaw.pk"

class EastLawScraperFinal:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def search_cases(self, query, page=1):
        url = f"{BASE_URL}/search"
        params = {'q': query, 'page': page}
        resp = self.session.get(url, params=params)
        soup = BeautifulSoup(resp.text, 'html.parser')
        cases = []
        for item in soup.select('.search-result'):
            cases.append({
                'title': item.select_one('.title').get_text(strip=True) if item.select_one('.title') else None,
                'citation': item.select_one('.citation').get_text(strip=True) if item.select_one('.citation') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
            })
        return cases

    def scrape_case_detail(self, url):
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return {
            'title': soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else None,
            'content': soup.select_one('.case-content').get_text(strip=True) if soup.select_one('.case-content') else None,
            'citations': [c.get_text(strip=True) for c in soup.select('.citation')],
        }

if __name__ == '__main__':
    scraper = EastLawScraperFinal()
    cases = scraper.search_cases("property", 1)
    print(json.dumps(cases, indent=2))
