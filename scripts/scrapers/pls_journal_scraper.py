#!/usr/bin/env python3
"""
PLS Journal Scraper - Scraper for PLS (Pakistan Legal Services) journals.
"""

import os
import sys
import json
import time
import re
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup


class PLSJournalScraper:
    """Scraper for PLS journals and legal publications."""
    
    def __init__(self, base_url: str = "https://pls.com.pk"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.results = []
    
    def fetch_page(self, url: str, retries: int = 3) -> Optional[str]:
        """
        Fetch a page with retry logic.
        
        Args:
            url: URL to fetch
            retries: Number of retries
            
        Returns:
            Page content or None
        """
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return None
    
    def parse_journal_list(self, html: str) -> List[Dict]:
        """
        Parse journal list from HTML.
        
        Args:
            html: HTML content
            
        Returns:
            List of journal dictionaries
        """
        soup = BeautifulSoup(html, 'html.parser')
        journals = []
        
        # Find journal entries (adjust selectors based on actual page structure)
        entries = soup.find_all('div', class_='journal-entry')
        
        for entry in entries:
            try:
                journal = {
                    'title': entry.find('h3').get_text(strip=True) if entry.find('h3') else '',
                    'citation': entry.find('span', class_='citation').get_text(strip=True) if entry.find('span', class_='citation') else '',
                    'court': entry.find('span', class_='court').get_text(strip=True) if entry.find('span', class_='court') else '',
                    'date': entry.find('span', class_='date').get_text(strip=True) if entry.find('span', class_='date') else '',
                    'summary': entry.find('p', class_='summary').get_text(strip=True) if entry.find('p', class_='summary') else '',
                    'url': entry.find('a')['href'] if entry.find('a') else ''
                }
                journals.append(journal)
            except Exception as e:
                print(f"Error parsing entry: {e}")
                continue
        
        return journals
    
    def parse_journal_detail(self, html: str) -> Dict:
        """
        Parse journal detail page.
        
        Args:
            html: HTML content
            
        Returns:
            Journal detail dictionary
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        detail = {
            'title': soup.find('h1').get_text(strip=True) if soup.find('h1') else '',
            'full_text': soup.find('div', class_='full-text').get_text(strip=True) if soup.find('div', class_='full-text') else '',
            'headnotes': soup.find('div', class_='headnotes').get_text(strip=True) if soup.find('div', class_='headnotes') else '',
            'citation': soup.find('span', class_='citation').get_text(strip=True) if soup.find('span', class_='citation') else '',
            'court': soup.find('span', class_='court').get_text(strip=True) if soup.find('span', class_='court') else '',
            'judges': soup.find('span', class_='judges').get_text(strip=True) if soup.find('span', class_='judges') else '',
            'date': soup.find('span', class_='date').get_text(strip=True) if soup.find('span', class_='date') else ''
        }
        
        return detail
    
    def scrape_journals(self, month: int, year: int, max_results: int = 50) -> List[Dict]:
        """
        Scrape journals for a specific month and year.
        
        Args:
            month: Month (1-12)
            year: Year
            max_results: Maximum results to return
            
        Returns:
            List of journal dictionaries
        """
        print(f"Scraping journals for {month}/{year}")
        
        url = f"{self.base_url}/journals/{year}/{month}"
        html = self.fetch_page(url)
        
        if not html:
            print("Failed to fetch journal list")
            return []
        
        journals = self.parse_journal_list(html)
        
        # Limit results
        journals = journals[:max_results]
        
        print(f"Found {len(journals)} journals")
        return journals
    
    def scrape_journal_detail(self, journal_url: str) -> Optional[Dict]:
        """
        Scrape detailed journal information.
        
        Args:
            journal_url: URL of journal detail page
            
        Returns:
            Journal detail dictionary or None
        """
        full_url = f"{self.base_url}{journal_url}"
        html = self.fetch_page(full_url)
        
        if not html:
            return None
        
        return self.parse_journal_detail(html)
    
    def search_journals(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Search journals by query.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of matching journals
        """
        print(f"Searching journals for: {query}")
        
        url = f"{self.base_url}/search"
        params = {'q': query, 'type': 'journals'}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            journals = self.parse_journal_list(response.text)
            return journals[:max_results]
            
        except requests.RequestException as e:
            print(f"Search failed: {e}")
            return []
    
    def save_results(self, filepath: str):
        """Save results to JSON file."""
        output = {
            'scraped_at': datetime.now().isoformat(),
            'total_results': len(self.results),
            'results': self.results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to {filepath}")
    
    def export_to_csv(self, filepath: str):
        """Export results to CSV."""
        import csv
        
        if not self.results:
            print("No results to export")
            return
        
        keys = self.results[0].keys()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.results)
        
        print(f"Results exported to {filepath}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='PLS Journal Scraper')
    parser.add_argument('--month', type=int, help='Month (1-12)')
    parser.add_argument('--year', type=int, help='Year')
    parser.add_argument('--search', help='Search query')
    parser.add_argument('--output', default='pls_journals.json', help='Output file')
    parser.add_argument('--csv', help='Export to CSV')
    parser.add_argument('--max-results', type=int, default=50, help='Maximum results')
    
    args = parser.parse_args()
    
    scraper = PLSJournalScraper()
    
    if args.search:
        results = scraper.search_journals(args.search, args.max_results)
        scraper.results = results
    elif args.month and args.year:
        results = scraper.scrape_journals(args.month, args.year, args.max_results)
        scraper.results = results
    else:
        print("Please specify --search or --month and --year")
        return
    
    scraper.save_results(args.output)
    
    if args.csv:
        scraper.export_to_csv(args.csv)


if __name__ == '__main__':
    main()
