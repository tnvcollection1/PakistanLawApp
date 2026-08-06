#!/usr/bin/env python3
"""Full scrape of PLS Beta data."""

import requests
import json
import time
from pathlib import Path

BASE_URL = "https://beta.pakistanlawsite.com"
OUTPUT_DIR = Path("data/pls_full")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
}

session = requests.Session()

def fetch_all_data():
    endpoints = {
        'courts': '/api/courts',
        'categories': '/api/categories',
        'journals': '/api/journals',
        'years': '/api/years',
        'alphabets': '/api/alphabets',
    }
    
    for name, endpoint in endpoints.items():
        url = f"{BASE_URL}{endpoint}"
        try:
            resp = session.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            output_file = OUTPUT_DIR / f"{name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Saved {name} to {output_file}")
        except Exception as e:
            print(f"Error fetching {name}: {e}")
        time.sleep(0.5)

def fetch_cases_by_category():
    categories_file = OUTPUT_DIR / "categories.json"
    if not categories_file.exists():
        print("Categories file not found. Run fetch_all_data first.")
        return
    
    with open(categories_file, 'r', encoding='utf-8') as f:
        categories = json.load(f)
    
    all_cases = []
    for category in categories:
        cat_id = category.get('id')
        cat_name = category.get('name', '')
        print(f"Fetching cases for category: {cat_name}...")
        
        page = 1
        while True:
            url = f"{BASE_URL}/api/cases?category={cat_id}&page={page}"
            try:
                resp = session.get(url, headers=HEADERS, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                cases = data.get('cases', [])
                if not cases:
                    break
                all_cases.extend(cases)
                if not data.get('has_more', False):
                    break
                page += 1
                time.sleep(0.3)
            except Exception as e:
                print(f"Error fetching category {cat_name}: {e}")
                break
    
    output_file = OUTPUT_DIR / "cases_by_category.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_cases, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(all_cases)} cases to {output_file}")

def main():
    fetch_all_data()
    fetch_cases_by_category()

if __name__ == '__main__':
    main()
