#!/usr/bin/env python3
"""Advanced search result extractor"""

import requests
import json
from bs4 import BeautifulSoup
import time

def extract_search_results(search_url, params=None):
    """Extract search results from advanced search"""
    try:
        response = requests.get(search_url, params=params, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for item in soup.find_all('div', class_='search-result'):
            result = {
                'title': item.find('h3').text.strip() if item.find('h3') else '',
                'snippet': item.find('div', class_='snippet').text.strip() if item.find('div', class_='snippet') else '',
                'url': item.find('a')['href'] if item.find('a') else '',
                'type': item.find('span', class_='result-type').text.strip() if item.find('span', class_='result-type') else ''
            }
            results.append(result)
        
        return {
            'results': results,
            'total': len(results),
            'page': params.get('page', 1) if params else 1
        }
    except Exception as e:
        print(f"Error extracting search results: {e}")
        return {'results': [], 'total': 0, 'error': str(e)}

def extract_all_search_results(base_url, query, max_pages=5):
    """Extract all search results across multiple pages"""
    all_results = []
    for page in range(1, max_pages + 1):
        params = {'q': query, 'page': page}
        data = extract_search_results(base_url, params)
        all_results.extend(data['results'])
        time.sleep(0.5)
    return all_results

def main():
    results = extract_all_search_results(
        'https://www.pakistanlawsite.com/search',
        'constitutional law'
    )
    with open('search_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    main()
