#!/usr/bin/env python3
"""Mass content scraper v2 with improved features"""

import requests
import json
import concurrent.futures
from bs4 import BeautifulSoup
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_content(url, timeout=30):
    """Fetch content from URL"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return {
            'url': url,
            'status': 'success',
            'title': soup.find('title').text.strip() if soup.find('title') else '',
            'content': soup.find('body').text.strip() if soup.find('body') else ''
        }
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

def mass_scrape_v2(urls, max_workers=10, batch_size=100):
    """Scrape multiple URLs in parallel with batching"""
    all_results = []
    
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(urls) + batch_size - 1)//batch_size}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(fetch_content, url): url for url in batch}
            for future in concurrent.futures.as_completed(future_to_url):
                result = future.result()
                all_results.append(result)
        
        time.sleep(1)  # Pause between batches
    
    return all_results

def save_results(results, filename='mass_scrape_v2_results.json'):
    """Save scraping results"""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    success = sum(1 for r in results if r['status'] == 'success')
    logger.info(f"Saved {len(results)} results ({success} successful) to {filename}")

def main():
    urls = [
        "https://www.pakistanlawsite.com/cases/1",
        "https://www.pakistanlawsite.com/statutes/1"
    ]
    results = mass_scrape_v2(urls)
    save_results(results)

if __name__ == '__main__':
    main()
