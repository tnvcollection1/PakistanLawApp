#!/usr/bin/env python3
"""Scraper for article/content pages"""

import requests
import json
from bs4 import BeautifulSoup
import time

def scrape_article(url):
    """Scrape a single article"""
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        article = {
            'url': url,
            'title': soup.find('h1').text.strip() if soup.find('h1') else '',
            'author': soup.find('span', class_='author').text.strip() if soup.find('span', class_='author') else '',
            'date': soup.find('span', class_='date').text.strip() if soup.find('span', class_='date') else '',
            'content': soup.find('div', class_='article-content').text.strip() if soup.find('div', class_='article-content') else ''
        }
        return article
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def scrape_articles(urls):
    """Scrape multiple articles"""
    articles = []
    for url in urls:
        print(f"Scraping: {url}")
        article = scrape_article(url)
        if article:
            articles.append(article)
        time.sleep(0.5)
    return articles

def main():
    urls = [
        "https://www.pakistanlawsite.com/articles/1",
        "https://www.pakistanlawsite.com/articles/2"
    ]
    articles = scrape_articles(urls)
    with open('articles.json', 'w') as f:
        json.dump(articles, f, indent=2)

if __name__ == '__main__':
    main()
