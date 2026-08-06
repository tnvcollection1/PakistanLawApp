#!/usr/bin/env python3
"""EastLaw full scraper with retry logic."""

import requests
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup

BASE_URL = "https://www.eastlaw.pk"
OUTPUT_DIR = Path("data/eastlaw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def fetch_with_retry(url, max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Attempt {attempt+1}/{max_retries} failed for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))
    return None

def parse_case_list(html):
    soup = BeautifulSoup(html, 'html.parser')
    cases = []
    for item in soup.select('.case-list-item, .search-result-item'):
        case = {
            'title': item.select_one('.case-title, .title').get_text(strip=True) if item.select_one('.case-title, .title') else '',
            'citation': item.select_one('.citation, .case-citation').get_text(strip=True) if item.select_one('.citation, .case-citation') else '',
            'link': item.select_one('a')['href'] if item.select_one('a') else '',
        }
        cases.append(case)
    return cases

def parse_case_detail(html):
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.select_one('.case-content, .content, .judgment-content')
    if content:
        return {'content': content.get_text(separator='\n', strip=True)}
    return {'content': ''}

def scrape_full():
    all_cases = []
    for page in range(1, 51):
        print(f"Scraping page {page}...")
        url = f"{BASE_URL}/cases?page={page}"
        html = fetch_with_retry(url)
        if not html:
            continue
        cases = parse_case_list(html)
        if not cases:
            break
        all_cases.extend(cases)
        time.sleep(1)
    
    print(f"Total cases found: {len(all_cases)}")
    
    # Save case list
    with open(OUTPUT_DIR / "case_list.json", 'w', encoding='utf-8') as f:
        json.dump(all_cases, f, indent=2, ensure_ascii=False)
    
    # Scrape details with retry
    for i, case in enumerate(all_cases):
        if not case['link']:
            continue
        print(f"Scraping detail {i+1}/{len(all_cases)}: {case['title'][:50]}...")
        url = f"{BASE_URL}{case['link']}"
        html = fetch_with_retry(url)
        if html:
            detail = parse_case_detail(html)
            case['detail'] = detail
        time.sleep(1)
    
    # Save full data
    with open(OUTPUT_DIR / "cases_full.json", 'w', encoding='utf-8') as f:
        json.dump(all_cases, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(all_cases)} cases to {OUTPUT_DIR / 'cases_full.json'}")

def main():
    scrape_full()

if __name__ == '__main__':
    main()
