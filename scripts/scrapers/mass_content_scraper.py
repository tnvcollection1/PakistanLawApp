#!/usr/bin/env python3
"""Mass content scraper for batch processing"""

import requests
import json
import concurrent.futures
from bs4 import BeautifulSoup
import time

def fetch_content(url, timeout=30):
    """Fetch content from URL"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return {
            'url': url,
            'title': soup.find('title').text.strip() if soup.find('title') else '',
            'content': soup.find('body').text.strip() if soup.find('body') else ''
        }
    except Exception as e:
        return {'url': url, 'error': str(e)}

def mass_scrape(urls, max_workers=10):
    """Scrape multiple URLs in parallel"""
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(fetch_content, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            result = future.result()
            results.append(result)
    return results

def save_results(results, filename='mass_scrape_results.json'):
    """Save scraping results"""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} results to {filename}")

def main():
    urls = [
        "https://www.pakistanlawsite.com/cases/1",
        "https://www.pakistanlawsite.com/cases/2",
        "https://www.pakistanlawsite.com/statutes/1"
    ]
    results = mass_scrape(urls)
    save_results(results)

if __name__ == '__main__':
    main()
