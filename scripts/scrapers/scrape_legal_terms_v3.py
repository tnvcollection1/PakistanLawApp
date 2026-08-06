#!/usr/bin/env python3
"""
Legal terms scraper v3 with multiprocessing and caching.
"""

import requests
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

BASE_URL = "https://www.pakistanlawsite.com"
CACHE_FILE = ".terms_cache.json"
OUTPUT_FILE = "legal_terms_v3.json"
MAX_WORKERS = 5

def load_cache():
    """Load cached terms."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save terms cache."""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def fetch_page(url):
    """Fetch page with caching."""
    cache = load_cache()
    
    if url in cache:
        return cache[url]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        cache[url] = resp.text
        save_cache(cache)
        return resp.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_terms_from_page(url):
    """Extract terms from a single page."""
    html = fetch_page(url)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    terms = []
    
    # Look for definition lists
    for dt in soup.find_all('dt'):
        term = dt.get_text().strip()
        dd = dt.find_next('dd')
        if dd:
            definition = dd.get_text().strip()
            if term and definition:
                terms.append({
                    'term': term,
                    'definition': definition,
                    'source': url
                })
    
    return terms

def scrape_legal_terms():
    """Main scraper with parallel processing."""
    print("Starting legal terms scraper v3")
    
    # Generate URLs to scrape
    urls = [
        f"{BASE_URL}/LegalTerms.aspx",
        f"{BASE_URL}/Dictionary.aspx",
        f"{BASE_URL}/Glossary.aspx",
    ]
    
    # Add paginated URLs
    for page in range(1, 5):
        urls.append(f"{BASE_URL}/LegalTerms.aspx?page={page}")
    
    all_terms = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(extract_terms_from_page, url): url for url in urls}
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                terms = future.result()
                all_terms.extend(terms)
                print(f"Found {len(terms)} terms from {url}")
            except Exception as e:
                print(f"Error processing {url}: {e}")
    
    # Deduplicate
    seen = set()
    unique = []
    for t in all_terms:
        key = t['term'].lower()
        if key not in seen:
            seen.add(key)
            unique.append(t)
    
    print(f"Total unique terms: {len(unique)}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == '__main__':
    scrape_legal_terms()
