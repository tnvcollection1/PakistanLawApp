"""
Scrape Topics - Topic scraper for PLS
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class TopicScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def scrape_topics(self):
        url = f"{BASE_URL}/topics"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        topics = []
        for item in soup.select('.topic-item'):
            topics.append({
                'name': item.select_one('.topic-name').get_text(strip=True) if item.select_one('.topic-name') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
                'case_count': item.select_one('.case-count').get_text(strip=True) if item.select_one('.case-count') else None,
            })
        return topics

    def scrape_topic_detail(self, url):
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        cases = []
        for item in soup.select('.case-item'):
            cases.append({
                'title': item.select_one('.case-title').get_text(strip=True) if item.select_one('.case-title') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
            })
        return cases

if __name__ == '__main__':
    scraper = TopicScraper()
    topics = scraper.scrape_topics()
    print(json.dumps(topics, indent=2))
