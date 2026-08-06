"""
EastLaw Scraper Rev - Revised EastLaw scraper
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.eastlaw.pk"

class EastLawScraperRev:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def scrape_citations(self, query):
        url = f"{BASE_URL}/citations"
        params = {'q': query}
        resp = self.session.get(url, params=params)
        soup = BeautifulSoup(resp.text, 'html.parser')
        citations = []
        for item in soup.select('.citation-item'):
            citations.append({
                'citation': item.select_one('.citation-text').get_text(strip=True) if item.select_one('.citation-text') else None,
                'case': item.select_one('.case-name').get_text(strip=True) if item.select_one('.case-name') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
            })
        return citations

    def scrape_case_detail(self, url):
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return {
            'title': soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else None,
            'content': soup.select_one('.case-content').get_text(strip=True) if soup.select_one('.case-content') else None,
            'citations': [c.get_text(strip=True) for c in soup.select('.citation')],
            'judges': [j.get_text(strip=True) for j in soup.select('.judge')],
        }

if __name__ == '__main__':
    scraper = EastLawScraperRev()
    citations = scraper.scrape_citations("property")
    print(json.dumps(citations, indent=2))
