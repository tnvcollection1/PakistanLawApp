"""
Scrape Articles - Article scraper for legal articles
"""
import json
import requests
from bs4 import BeautifulSoup

class ArticleScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def scrape_articles(self, page=1):
        url = f"{self.base_url}/articles?page={page}"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        articles = []
        for item in soup.select('.article-item'):
            articles.append({
                'title': item.select_one('.article-title').get_text(strip=True) if item.select_one('.article-title') else None,
                'author': item.select_one('.article-author').get_text(strip=True) if item.select_one('.article-author') else None,
                'url': item.select_one('a')['href'] if item.select_one('a') else None,
            })
        return articles

    def scrape_article_detail(self, url):
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        content = soup.select_one('.article-content')
        return content.get_text(strip=True) if content else None

if __name__ == '__main__':
    scraper = ArticleScraper("https://example.com")
    articles = scraper.scrape_articles(1)
    print(json.dumps(articles, indent=2))
