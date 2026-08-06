"""
LHC Scraper Desktop - Desktop-optimized LHC scraper
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://lhc.gov.pk"

class LHCScraperDesktop:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        })

    def scrape_judgments(self, page=1):
        url = f"{BASE_URL}/judgments?page={page}"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        judgments = []
        for item in soup.select('.judgment-item'):
            judgments.append({
                'title': item.select_one('.title').get_text(strip=True) if item.select_one('.title') else None,
                'date': item.select_one('.date').get_text(strip=True) if item.select_one('.date') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
            })
        return judgments

    def scrape_judgment_detail(self, url):
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return {
            'title': soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else None,
            'content': soup.select_one('.judgment-content').get_text(strip=True) if soup.select_one('.judgment-content') else None,
        }

if __name__ == '__main__':
    scraper = LHCScraperDesktop()
    judgments = scraper.scrape_judgments(1)
    print(json.dumps(judgments, indent=2))
