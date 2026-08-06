#!/usr/bin/env python3
"""
Enhanced legal terms scraper with better parsing.
"""

import requests
import re
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.pakistanlawsite.com"
OUTPUT_FILE = "legal_terms_v2.json"

def fetch_page(url):
    """Fetch a page with retries."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    
    return None

def extract_terms(html):
    """Extract legal terms from HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    terms = []
    
    # Look for term definitions in various formats
    for dt in soup.find_all(['dt', 'h3', 'h4']):
        term = dt.get_text().strip()
        dd = dt.find_next(['dd', 'p'])
        
        if dd:
            definition = dd.get_text().strip()
            if term and definition and len(term) < 200:
                terms.append({
                    'term': term,
                    'definition': definition,
                    'source': 'pls'
                })
    
    return terms

def scrape_legal_terms():
    """Main scraper function."""
    print("Starting legal terms scraper v2")
    
    all_terms = []
    
    # Try common legal terms pages
    urls = [
        f"{BASE_URL}/LegalTerms.aspx",
        f"{BASE_URL}/Dictionary.aspx",
        f"{BASE_URL}/Glossary.aspx",
    ]
    
    for url in urls:
        print(f"Fetching: {url}")
        html = fetch_page(url)
        
        if html:
            terms = extract_terms(html)
            print(f"Found {len(terms)} terms from {url}")
            all_terms.extend(terms)
        
        time.sleep(1)
    
    # Deduplicate by term
    seen = set()
    unique_terms = []
    for t in all_terms:
        if t['term'].lower() not in seen:
            seen.add(t['term'].lower())
            unique_terms.append(t)
    
    print(f"Total unique terms: {len(unique_terms)}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique_terms, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == '__main__':
    scrape_legal_terms()
