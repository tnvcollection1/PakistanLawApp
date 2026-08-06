"""
EastLaw Complete - Complete scraper for EastLaw
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.eastlaw.pk"

class EastLawCompleteScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def search(self, query, page=1):
        url = f"{BASE_URL}/search"
        params = {'q': query, 'page': page}
        resp = self.session.get(url, params=params)
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        for item in soup.select('.result-item'):
            results.append({
                'title': item.select_one('.title').get_text(strip=True) if item.select_one('.title') else None,
                'citation': item.select_one('.citation').get_text(strip=True) if item.select_one('.citation') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
                'date': item.select_one('.date').get_text(strip=True) if item.select_one('.date') else None,
                'court': item.select_one('.court').get_text(strip=True) if item.select_one('.court') else None,
            })
        return results

    def scrape_case(self, url):
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return {
            'title': soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else None,
            'content': soup.select_one('.content').get_text(strip=True) if soup.select_one('.content') else None,
            'citations': [c.get_text(strip=True) for c in soup.select('.citation')],
            'judges': [j.get_text(strip=True) for j in soup.select('.judge')],
            'headnotes': [h.get_text(strip=True) for h in soup.select('.headnote')],
        }

if __name__ == '__main__':
    scraper = EastLawCompleteScraper()
    results = scraper.search("property", 1)
    print(json.dumps(results, indent=2))
