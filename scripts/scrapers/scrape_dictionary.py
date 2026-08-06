#!/usr/bin/env python3
"""
Dictionary scraper for Pakistan legal dictionary.
"""

import requests
import re
import json
import time
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

BASE_URL = "https://www.pakistanlawsite.com"
OUTPUT_DIR = "./data/dictionary"

def fetch_page(url, retries=3):
    """Fetch page with retries."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml'
    }
    
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            time.sleep(2 ** attempt)
    
    return None

def extract_dictionary_entries(html):
    """Extract dictionary entries from HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    entries = []
    
    # Look for term-definition pairs
    for elem in soup.find_all(['div', 'tr', 'li']):
        term_elem = elem.find(class_=re.compile(r'term|word|title', re.I))
        def_elem = elem.find(class_=re.compile(r'definition|meaning|desc', re.I))
        
        if term_elem and def_elem:
            entry = {
                'term': term_elem.get_text().strip(),
                'definition': def_elem.get_text().strip(),
                'source_url': None
            }
            
            # Skip if too short or too long
            if 2 < len(entry['term']) < 200 and len(entry['definition']) > 10:
                entries.append(entry)
    
    return entries

def scrape_dictionary():
    """Main dictionary scraper."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Starting dictionary scraper")
    
    all_entries = []
    
    # Scrape main dictionary pages
    urls = [
        f"{BASE_URL}/Dictionary.aspx",
        f"{BASE_URL}/LegalDictionary.aspx",
        f"{BASE_URL}/BlackLaw.aspx",
    ]
    
    # Also try A-Z pages
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        urls.append(f"{BASE_URL}/Dictionary.aspx?letter={letter}")
    
    for url in urls:
        print(f"Fetching: {url}")
        html = fetch_page(url)
        
        if html:
            entries = extract_dictionary_entries(html)
            all_entries.extend(entries)
            print(f"Found {len(entries)} entries")
        
        time.sleep(1)
    
    # Deduplicate
    seen = set()
    unique = []
    for e in all_entries:
        key = e['term'].lower()
        if key not in seen:
            seen.add(key)
            unique.append(e)
    
    print(f"\nTotal unique entries: {len(unique)}")
    
    # Save
    output_file = os.path.join(OUTPUT_DIR, 'dictionary.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to {output_file}")
    
    # Also save as CSV
    import csv
    csv_file = os.path.join(OUTPUT_DIR, 'dictionary.csv')
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['term', 'definition'])
        writer.writeheader()
        writer.writerows(unique)
    
    print(f"Saved CSV to {csv_file}")

if __name__ == '__main__':
    scrape_dictionary()
