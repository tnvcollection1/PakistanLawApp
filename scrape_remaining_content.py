#!/usr/bin/env python3
"""
scrape_remaining_content.py
Scrapes remaining content types from Pakistan Law Site.
"""

import os, sys, json, re, time, logging, requests
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://www.pakistanlawsite.com"
OUTPUT_DIR = "/tmp/pls_remaining"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                return r.text
        except Exception as e:
            logger.warning(f"Fetch error: {e}")
        time.sleep(2 ** attempt)
    return None


def scrape_dictionary():
    logger.info("Scraping dictionary...")
    html = fetch(f"{BASE_URL}/Login/DictionaryPage")
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    entries = []
    
    for elem in soup.find_all(['dt', 'dd']):
        text = elem.get_text(strip=True)
        if text:
            entries.append({
                'term': text[:500],
                'source': 'pls_dictionary',
                'scraped_at': datetime.utcnow().isoformat()
            })
    
    logger.info(f"  Found {len(entries)} dictionary entries")
    return entries


def scrape_articles():
    logger.info("Scraping articles...")
    html = fetch(f"{BASE_URL}/Login/ArticlePage")
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    articles = []
    
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if 'ArticleDetail' in href or 'fileID' in href:
            match = re.search(r'fileID=(\d+)', href)
            file_id = match.group(1) if match else None
            articles.append({
                'title': text[:500],
                'file_id': file_id,
                'url': href,
                'source': 'pls_articles',
                'scraped_at': datetime.utcnow().isoformat()
            })
    
    logger.info(f"  Found {len(articles)} articles")
    return articles


def scrape_topics():
    logger.info("Scraping topics...")
    html = fetch(f"{BASE_URL}/Login/TopicPage")
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    topics = []
    
    for elem in soup.find_all(attrs={'topicid': True}):
        topic_id = elem.get('topicid')
        text = elem.get_text(strip=True)
        topics.append({
            'topic_id': topic_id,
            'name': text[:500],
            'source': 'pls_topics',
            'scraped_at': datetime.utcnow().isoformat()
        })
    
    logger.info(f"  Found {len(topics)} topics")
    return topics


def save_data(data, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"  Saved to {filepath}")


def main():
    logger.info("=" * 50)
    logger.info("Scraping Remaining Content")
    logger.info("=" * 50)
    
    dictionary = scrape_dictionary()
    if dictionary:
        save_data(dictionary, f"dictionary_{datetime.now().strftime('%Y%m%d')}.json")
    
    articles = scrape_articles()
    if articles:
        save_data(articles, f"articles_{datetime.now().strftime('%Y%m%d')}.json")
    
    topics = scrape_topics()
    if topics:
        save_data(topics, f"topics_{datetime.now().strftime('%Y%m%d')}.json")
    
    logger.info("=" * 50)
    logger.info("Complete")
    logger.info(f"  Dictionary: {len(dictionary)}")
    logger.info(f"  Articles: {len(articles)}")
    logger.info(f"  Topics: {len(topics)}")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
