#!/usr/bin/env python3
"""Aggressive scraper for PLS with rate limiting and retries"""

import requests
import time
import random
from bs4 import BeautifulSoup
import json

class AggressiveScraper:
    def __init__(self, base_url="https://www.pakistanlawsite.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.delay_min = 0.5
        self.delay_max = 2.0
        self.max_retries = 3
    
    def random_delay(self):
        """Random delay between requests"""
        time.sleep(random.uniform(self.delay_min, self.delay_max))
    
    def fetch_with_retry(self, url):
        """Fetch URL with retry logic"""
        for attempt in range(self.max_retries):
            try:
                self.random_delay()
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        return None
    
    def scrape_case_page(self, case_id):
        """Scrape a single case page"""
        url = f"{self.base_url}/case/{case_id}"
        response = self.fetch_with_retry(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        return {
            'case_id': case_id,
            'title': soup.find('h1').text.strip() if soup.find('h1') else '',
            'content': soup.find('div', class_='case-content').text.strip() if soup.find('div', class_='case-content') else ''
        }

def main():
    scraper = AggressiveScraper()
    case = scraper.scrape_case_page('sample-case-id')
    print(json.dumps(case, indent=2))

if __name__ == '__main__':
    main()
