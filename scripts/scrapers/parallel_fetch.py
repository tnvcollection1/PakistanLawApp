#!/usr/bin/env python3
"""Parallel fetch utility for scraping"""

import requests
import concurrent.futures
from bs4 import BeautifulSoup
import json

def fetch_url(url, timeout=30):
    """Fetch a single URL"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return {'url': url, 'status': response.status_code, 'content': response.text}
    except Exception as e:
        return {'url': url, 'status': None, 'error': str(e)}

def fetch_urls_parallel(urls, max_workers=10):
    """Fetch multiple URLs in parallel"""
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(fetch_url, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            result = future.result()
            results.append(result)
    return results

def parse_parallel_results(results, parser_func):
    """Parse fetched content using a parser function"""
    parsed = []
    for result in results:
        if result.get('content'):
            try:
                data = parser_func(result['content'])
                parsed.append({'url': result['url'], 'data': data})
            except Exception as e:
                parsed.append({'url': result['url'], 'error': str(e)})
    return parsed

def main():
    """Example usage"""
    urls = [
        "https://www.pakistanlawsite.com/cases",
        "https://www.pakistanlawsite.com/statutes"
    ]
    results = fetch_urls_parallel(urls, max_workers=2)
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
