#!/usr/bin/env python3
"""Complete content fetcher with full extraction"""

import requests
import json
import time
from bs4 import BeautifulSoup

def fetch_complete_content(url):
    """Fetch complete content from URL"""
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all relevant content
        content = {
            'url': url,
            'title': soup.find('title').text.strip() if soup.find('title') else '',
            'headings': [h.text.strip() for h in soup.find_all(['h1', 'h2', 'h3'])],
            'paragraphs': [p.text.strip() for p in soup.find_all('p')],
            'links': [{'text': a.text.strip(), 'href': a.get('href', '')} for a in soup.find_all('a')],
            'tables': [],
            'meta': {}
        }
        
        # Extract tables
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                row = [td.text.strip() for td in tr.find_all(['td', 'th'])]
                rows.append(row)
            content['tables'].append(rows)
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            value = meta.get('content', '')
            if name:
                content['meta'][name] = value
        
        return content
    except Exception as e:
        return {'url': url, 'error': str(e)}

def main():
    url = "https://www.pakistanlawsite.com/cases/1"
    content = fetch_complete_content(url)
    with open('complete_content.json', 'w') as f:
        json.dump(content, f, indent=2)

if __name__ == '__main__':
    main()
