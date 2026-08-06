#!/usr/bin/env python3
"""Extract all cases from Pakistan Legal System"""

import requests
import json
import time
from bs4 import BeautifulSoup

def extract_case_details(case_url):
    """Extract detailed case information"""
    try:
        response = requests.get(case_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        case = {
            'url': case_url,
            'title': soup.find('h1', class_='case-title').text.strip() if soup.find('h1', class_='case-title') else '',
            'citation': soup.find('div', class_='citation').text.strip() if soup.find('div', class_='citation') else '',
            'date': soup.find('div', class_='date').text.strip() if soup.find('div', class_='date') else '',
            'court': soup.find('div', class_='court').text.strip() if soup.find('div', class_='court') else '',
            'content': soup.find('div', class_='case-content').text.strip() if soup.find('div', class_='case-content') else ''
        }
        return case
    except Exception as e:
        print(f"Error extracting {case_url}: {e}")
        return None

def get_all_case_urls(base_url="https://www.pakistanlawsite.com"):
    """Get all case URLs"""
    urls = []
    for page in range(1, 100):
        url = f"{base_url}/cases?page={page}"
        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', class_='case-link')
            if not links:
                break
            for link in links:
                urls.append(f"{base_url}{link['href']}")
            time.sleep(0.5)
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break
    return urls

def main():
    """Main extraction function"""
    print("Getting all case URLs...")
    urls = get_all_case_urls()
    print(f"Found {len(urls)} cases")
    
    all_cases = []
    for i, url in enumerate(urls):
        print(f"Extracting case {i+1}/{len(urls)}: {url}")
        case = extract_case_details(url)
        if case:
            all_cases.append(case)
        time.sleep(0.5)
    
    with open('all_cases.json', 'w') as f:
        json.dump(all_cases, f, indent=2)
    
    print(f"Extracted {len(all_cases)} cases")

if __name__ == '__main__':
    main()
