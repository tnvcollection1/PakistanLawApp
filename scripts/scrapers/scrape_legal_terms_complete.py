#!/usr/bin/env python3
"""Complete scraper for legal terms and definitions"""

import requests
from bs4 import BeautifulSoup
import json

def scrape_legal_terms():
    """Scrape legal terms from various sources"""
    terms = {}
    
    # Pakistan Law Site
    url = "https://www.pakistanlawsite.com/legal-terms"
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.find_all('div', class_='term-item'):
            term = item.find('dt')
            definition = item.find('dd')
            if term and definition:
                terms[term.text.strip()] = definition.text.strip()
    except Exception as e:
        print(f"Error scraping legal terms: {e}")
    
    return terms

def save_terms(terms, filename='legal_terms.json'):
    """Save terms to JSON file"""
    with open(filename, 'w') as f:
        json.dump(terms, f, indent=2)
    print(f"Saved {len(terms)} legal terms")

def main():
    terms = scrape_legal_terms()
    save_terms(terms)

if __name__ == '__main__':
    main()
