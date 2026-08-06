#!/usr/bin/env python3
"""Fast EastLaw scraper using parallel processing and caching."""

import asyncio
import aiohttp
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import hashlib

BASE_URL = "https://www.eastlaw.pk"
CACHE_DIR = Path("cache/eastlaw")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def get_cache_path(url):
    h = hashlib.md5(url.encode()).hexdigest()
    return CACHE_DIR / f"{h}.html"

def fetch_page(url, use_cache=True):
    cache_path = get_cache_path(url)
    if use_cache and cache_path.exists():
        return cache_path.read_text(encoding='utf-8')
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        html = resp.text
        if use_cache:
            cache_path.write_text(html, encoding='utf-8')
        return html
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_case_list(html):
    soup = BeautifulSoup(html, 'html.parser')
    cases = []
    for item in soup.select('.case-list-item'):
        case = {
            'title': item.select_one('.case-title').get_text(strip=True) if item.select_one('.case-title') else '',
            'citation': item.select_one('.case-citation').get_text(strip=True) if item.select_one('.case-citation') else '',
            'court': item.select_one('.case-court').get_text(strip=True) if item.select_one('.case-court') else '',
            'year': item.select_one('.case-year').get_text(strip=True) if item.select_one('.case-year') else '',
            'link': item.select_one('a')['href'] if item.select_one('a') else '',
        }
        cases.append(case)
    return cases

def parse_case_detail(html):
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.select_one('.case-content, .judgment-content, .content')
    if content:
        return {'content': content.get_text(separator='\n', strip=True)}
    return {'content': ''}

def scrape_case_list(page=1):
    url = f"{BASE_URL}/cases?page={page}"
    html = fetch_page(url)
    if html:
        return parse_case_list(html)
    return []

def scrape_case_detail(case_url):
    url = f"{BASE_URL}{case_url}"
    html = fetch_page(url)
    if html:
        return parse_case_detail(html)
    return {}

def run_parallel(items, func, max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(func, items))
    return results

def main():
    print("Starting fast EastLaw scraper...")
    
    # Scrape first 10 pages of case list
    all_cases = []
    for page in range(1, 11):
        print(f"Scraping page {page}...")
        cases = scrape_case_list(page)
        all_cases.extend(cases)
        time.sleep(0.5)
    
    print(f"Found {len(all_cases)} cases")
    
    # Scrape details for first 20 cases
    case_urls = [c['link'] for c in all_cases[:20] if c['link']]
    print(f"Scraping details for {len(case_urls)} cases...")
    
    details = run_parallel(case_urls, scrape_case_detail, max_workers=5)
    
    for i, detail in enumerate(details):
        if i < len(all_cases):
            all_cases[i]['detail'] = detail
    
    # Save results
    output_file = 'eastlaw_cases_fast.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_cases, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(all_cases)} cases to {output_file}")

if __name__ == '__main__':
    main()
