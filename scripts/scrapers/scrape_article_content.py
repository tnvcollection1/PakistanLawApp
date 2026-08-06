"""
Scrape Article Content - Extract article content from legal articles
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class ArticleContentScraper:
    def __init__(self):
        self.session = requests.Session()

    def scrape_article(self, article_id):
        url = f"{BASE_URL}/articles/{article_id}"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return {
            'id': article_id,
            'title': soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else None,
            'author': soup.select_one('.author').get_text(strip=True) if soup.select_one('.author') else None,
            'content': soup.select_one('.article-content').get_text(strip=True) if soup.select_one('.article-content') else None,
            'published_date': soup.select_one('.published-date').get_text(strip=True) if soup.select_one('.published-date') else None,
        }

if __name__ == '__main__':
    scraper = ArticleContentScraper()
    article = scraper.scrape_article('1')
    print(json.dumps(article, indent=2))
