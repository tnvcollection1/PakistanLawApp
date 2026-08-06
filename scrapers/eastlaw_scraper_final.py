#!/usr/bin/env python3
"""Final version of Eastlaw scraper"""

import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = "https://eastlaw.pk"

def get_session():
    """Create a requests session"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    return session

def scrape_eastlaw_cases(page=1):
    """Scrape cases from Eastlaw"""
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
                'court': item.find('span', class_='court').text.strip() if item.find('span', class_='court') else '',
                'url': item.find('a')['href'] if item.find('a') else ''
            }
            cases.append(case)
        
        return cases
    except Exception as e:
        print(f"Error scraping page {page}: {e}")
        return []

def scrape_case_detail(url):
    """Scrape case detail"""
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return {
            'title': soup.find('h1').text.strip() if soup.find('h1') else '',
            'content': soup.find('div', class_='case-content').text.strip() if soup.find('div', class_='case-content') else '',
            'headnotes': soup.find('div', class_='headnotes').text.strip() if soup.find('div', class_='headnotes') else '',
            'judges': soup.find('div', class_='judges').text.strip() if soup.find('div', class_='judges') else ''
        }
    except Exception as e:
        print(f"Error scraping detail {url}: {e}")
        return {}

def main():
    all_cases = []
    for page in range(1, 3):
        print(f"Scraping page {page}...")
        cases = scrape_eastlaw_cases(page)
        all_cases.extend(cases)
        time.sleep(1)
    
    with open('eastlaw_cases.json', 'w') as f:
        json.dump(all_cases, f, indent=2)
    print(f"Scraped {len(all_cases)} cases")

if __name__ == '__main__':
    main()
