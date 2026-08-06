"""
Scrape PLS Beta Statute Sections - Section-level statute scraper
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class StatuteSectionScraper:
    def __init__(self):
        self.session = requests.Session()

    def scrape_sections(self, statute_id):
        url = f"{BASE_URL}/statutes/{statute_id}/sections"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        sections = []
        for item in soup.select('.section-item'):
            sections.append({
                'number': item.select_one('.section-number').get_text(strip=True) if item.select_one('.section-number') else None,
                'title': item.select_one('.section-title').get_text(strip=True) if item.select_one('.section-title') else None,
                'content': item.select_one('.section-content').get_text(strip=True) if item.select_one('.section-content') else None,
            })
        return sections

if __name__ == '__main__':
    scraper = StatuteSectionScraper()
    sections = scraper.scrape_sections('1')
    print(json.dumps(sections, indent=2))
