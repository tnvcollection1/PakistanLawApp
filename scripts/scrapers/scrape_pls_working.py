#!/usr/bin/env python3
"""Working scraper for Pakistan Law Site"""

import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = "https://www.pakistanlawsite.com"

def get_session():
    """Create a requests session with proper headers"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    })
    return session

def scrape_case_list(page=1):
    """Scrape case list from PLS"""
    session = get_session()
    url = f"{BASE_URL}/cases?page={page}"
    
    try:
        response = session.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        cases = []
        for item in soup.find_all('div', class_='case-item'):
            case = {
                'title': item.find('h3').text.strip() if item.find('h3') else '',
                'citation': item.find('span', class_='citation').text.strip() if item.find('span', class_='citation') else '',
                'date': item.find('span', class_='date').text.strip() if item.find('span', class_='date') else '',
                'url': item.find('a')['href'] if item.find('a') else ''
            }
            cases.append(case)
        
        return cases
    except Exception as e:
        print(f"Error scraping page {page}: {e}")
        return []

def main():
    all_cases = []
    for page in range(1, 5):
        print(f"Scraping page {page}...")
        cases = scrape_case_list(page)
        all_cases.extend(cases)
        time.sleep(1)
    
    with open('pls_cases.json', 'w') as f:
        json.dump(all_cases, f, indent=2)
    print(f"Scraped {len(all_cases)} cases")

if __name__ == '__main__':
    main()
