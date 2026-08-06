#!/usr/bin/env python3
"""Lahore High Court scraper (desktop version)"""

import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = "https://lhc.gov.pk"

def scrape_lhc_judgments(page=1):
    """Scrape LHC judgments"""
    url = f"{BASE_URL}/judgments?page={page}"
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        judgments = []
        for item in soup.find_all('div', class_='judgment-item'):
            judgment = {
                'title': item.find('h3').text.strip() if item.find('h3') else '',
                'citation': item.find('span', class_='citation').text.strip() if item.find('span', class_='citation') else '',
                'date': item.find('span', class_='date').text.strip() if item.find('span', class_='date') else '',
                'bench': item.find('span', class_='bench').text.strip() if item.find('span', class_='bench') else '',
                'url': item.find('a')['href'] if item.find('a') else ''
            }
            judgments.append(judgment)
        
        return judgments
    except Exception as e:
        print(f"Error scraping page {page}: {e}")
        return []

def scrape_judgment_detail(url):
    """Scrape judgment details"""
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return {
            'title': soup.find('h1').text.strip() if soup.find('h1') else '',
            'content': soup.find('div', class_='judgment-content').text.strip() if soup.find('div', class_='judgment-content') else '',
            'parties': soup.find('div', class_='parties').text.strip() if soup.find('div', class_='parties') else '',
            'judges': soup.find('div', class_='judges').text.strip() if soup.find('div', class_='judges') else ''
        }
    except Exception as e:
        print(f"Error scraping detail {url}: {e}")
        return {}

def main():
    all_judgments = []
    for page in range(1, 3):
        print(f"Scraping LHC page {page}...")
        judgments = scrape_lhc_judgments(page)
        all_judgments.extend(judgments)
        time.sleep(1)
    
    with open('lhc_judgments.json', 'w') as f:
        json.dump(all_judgments, f, indent=2)
    print(f"Scraped {len(all_judgments)} judgments")

if __name__ == '__main__':
    main()
