#!/usr/bin/env python3
"""New scraper for PLS statutes with improved parsing"""

import requests
import json
import time
from bs4 import BeautifulSoup

def scrape_statute_list(page=1):
    """Scrape statute list from PLS"""
    url = f"https://www.pakistanlawsite.com/statutes?page={page}"
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        statutes = []
        for item in soup.find_all('div', class_='statute-item'):
            statute = {
                'title': item.find('h3').text.strip() if item.find('h3') else '',
                'year': item.find('span', class_='year').text.strip() if item.find('span', class_='year') else '',
                'category': item.find('span', class_='category').text.strip() if item.find('span', class_='category') else '',
                'url': item.find('a')['href'] if item.find('a') else ''
            }
            statutes.append(statute)
        
        return statutes
    except Exception as e:
        print(f"Error scraping page {page}: {e}")
        return []

def scrape_statute_detail(url):
    """Scrape detailed statute information"""
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return {
            'title': soup.find('h1').text.strip() if soup.find('h1') else '',
            'preamble': soup.find('div', class_='preamble').text.strip() if soup.find('div', class_='preamble') else '',
            'sections': [s.text.strip() for s in soup.find_all('div', class_='section')]
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {}

def main():
    all_statutes = []
    for page in range(1, 5):
        print(f"Scraping statutes page {page}...")
        statutes = scrape_statute_list(page)
        all_statutes.extend(statutes)
        time.sleep(1)
    
    # Get details for each statute
    detailed = []
    for statute in all_statutes:
        if statute['url']:
            detail = scrape_statute_detail(statute['url'])
            statute['detail'] = detail
            detailed.append(statute)
            time.sleep(0.5)
    
    with open('pls_statutes_new.json', 'w') as f:
        json.dump(detailed, f, indent=2)
    print(f"Scraped {len(detailed)} statutes")

if __name__ == '__main__':
    main()
