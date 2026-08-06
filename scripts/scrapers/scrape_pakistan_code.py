"""
Scrape Pakistan Code - Scraper for Pakistan Code statutes
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://pakistancode.gov.pk"

class PakistanCodeScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def scrape_act_list(self):
        url = f"{BASE_URL}/acts"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        acts = []
        for item in soup.select('table tr')[1:]:
            cells = item.find_all('td')
            if len(cells) >= 2:
                acts.append({
                    'title': cells[0].get_text(strip=True),
                    'year': cells[1].get_text(strip=True),
                })
        return acts

    def scrape_act_detail(self, url):
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        content = soup.select_one('.content')
        return content.get_text(strip=True) if content else None

if __name__ == '__main__':
    scraper = PakistanCodeScraper()
    acts = scraper.scrape_act_list()
    print(json.dumps(acts, indent=2))
