#!/usr/bin/env python3
"""List extractor for case lists and other structured data"""

import requests
from bs4 import BeautifulSoup
import json

def extract_list_items(url, selector):
    """Extract list items from a URL using CSS selector"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = []
        for element in soup.select(selector):
            items.append({
                'text': element.get_text(strip=True),
                'href': element.get('href', '')
            })
        
        return items
    except Exception as e:
        print(f"Error extracting from {url}: {e}")
        return []

def save_items(items, filename):
    """Save extracted items to JSON file"""
    with open(filename, 'w') as f:
        json.dump(items, f, indent=2)
    print(f"Saved {len(items)} items to {filename}")

def main():
    """Main extraction function"""
    # Example: Extract case list
    url = "https://www.pakistanlawsite.com/cases"
    items = extract_list_items(url, '.case-list-item')
    save_items(items, 'extracted_cases.json')

if __name__ == '__main__':
    main()
