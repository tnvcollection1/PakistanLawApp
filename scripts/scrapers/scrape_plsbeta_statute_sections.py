#!/usr/bin/env python3
"""Scraper for PLS Beta statute sections"""

import requests
import json
import time
from bs4 import BeautifulSoup

def scrape_statute_sections(statute_id):
    """Scrape sections for a specific statute"""
    url = f"https://beta.pakistanlawsite.com/statute/{statute_id}/sections"
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        sections = []
        for item in soup.find_all('div', class_='section-item'):
            section = {
                'number': item.find('span', class_='section-number').text.strip() if item.find('span', class_='section-number') else '',
                'title': item.find('span', class_='section-title').text.strip() if item.find('span', class_='section-title') else '',
                'content': item.find('div', class_='section-content').text.strip() if item.find('div', class_='section-content') else ''
            }
            sections.append(section)
        
        return sections
    except Exception as e:
        print(f"Error scraping statute {statute_id}: {e}")
        return []

def scrape_all_statute_sections():
    """Scrape sections for all statutes"""
    all_sections = {}
    
    # Load statute list
    try:
        with open('statutes.json', 'r') as f:
            statutes = json.load(f)
    except FileNotFoundError:
        print("statutes.json not found")
        return {}
    
    for statute in statutes:
        statute_id = statute.get('id')
        print(f"Scraping sections for statute: {statute_id}")
        sections = scrape_statute_sections(statute_id)
        all_sections[statute_id] = sections
        time.sleep(0.5)
    
    return all_sections

def main():
    sections = scrape_all_statute_sections()
    with open('statute_sections.json', 'w') as f:
        json.dump(sections, f, indent=2)
    print(f"Scraped sections for {len(sections)} statutes")

if __name__ == '__main__':
    main()
