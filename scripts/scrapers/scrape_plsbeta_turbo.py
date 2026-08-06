#!/usr/bin/env python3
"""Turbo scraper for PLS Beta with optimized performance"""

import requests
import json
import time
import concurrent.futures
from bs4 import BeautifulSoup

BASE_URL = "https://beta.pakistanlawsite.com"

def fetch_case(case_id):
    """Fetch a single case"""
    url = f"{BASE_URL}/case/{case_id}"
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        return {
            'case_id': case_id,
            'title': soup.find('h1').text.strip() if soup.find('h1') else '',
            'content': soup.find('div', class_='case-content').text.strip() if soup.find('div', class_='case-content') else '',
            'status': 'success'
        }
    except Exception as e:
        return {'case_id': case_id, 'status': 'error', 'error': str(e)}

def turbo_scrape(case_ids, max_workers=20):
    """Turbo scrape multiple cases"""
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(fetch_case, cid): cid for cid in case_ids}
        for future in concurrent.futures.as_completed(future_to_id):
            result = future.result()
            results.append(result)
    return results

def main():
    case_ids = [f"case_{i}" for i in range(1, 101)]
    results = turbo_scrape(case_ids)
    
    success = sum(1 for r in results if r['status'] == 'success')
    print(f"Scraped {success}/{len(results)} cases successfully")
    
    with open('plsbeta_turbo.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    main()
