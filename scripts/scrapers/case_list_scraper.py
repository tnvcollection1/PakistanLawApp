#!/usr/bin/env python3
"""Case list scraper for Pakistan Legal System"""

import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = "https://www.pakistanlawsite.com"

def fetch_case_list(page=1):
    """Fetch case list from the website"""
    url = f"{BASE_URL}/cases?page={page}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching page {page}: {e}")
        return None

def parse_case_list(html):
    """Parse case list HTML"""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    cases = []
    
    # Extract case entries
    for item in soup.find_all('div', class_='case-item'):
        case = {
            'title': item.find('h3').text.strip() if item.find('h3') else '',
            'citation': item.find('span', class_='citation').text.strip() if item.find('span', class_='citation') else '',
            'date': item.find('span', class_='date').text.strip() if item.find('span', class_='date') else '',
            'court': item.find('span', class_='court').text.strip() if item.find('span', class_='court') else ''
        }
        cases.append(case)
    
    return cases

def main():
    """Main scraper function"""
    all_cases = []
    for page in range(1, 11):
        print(f"Fetching page {page}...")
        html = fetch_case_list(page)
        cases = parse_case_list(html)
        all_cases.extend(cases)
        time.sleep(1)
    
    with open('case_list.json', 'w') as f:
        json.dump(all_cases, f, indent=2)
    
    print(f"Scraped {len(all_cases)} cases")

if __name__ == '__main__':
    main()
