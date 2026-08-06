#!/usr/bin/env python3
"""Extract missing cases using local database comparison"""

import json
import requests
from bs4 import BeautifulSoup
import sqlite3

def get_existing_cases(db_path='cases.db'):
    """Get list of existing case IDs from local database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM cases')
    existing = set(row[0] for row in cursor.fetchall())
    conn.close()
    return existing

def get_all_online_cases():
    """Get all case IDs from the website"""
    case_ids = []
    base_url = "https://www.pakistanlawsite.com/cases"
    
    for page in range(1, 50):
        try:
            response = requests.get(f"{base_url}?page={page}", timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if '/case/' in href:
                    case_id = href.split('/case/')[-1]
                    case_ids.append(case_id)
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break
    
    return case_ids

def find_missing_cases():
    """Find cases that exist online but not locally"""
    existing = get_existing_cases()
    online = set(get_all_online_cases())
    missing = online - existing
    return list(missing)

def main():
    missing = find_missing_cases()
    print(f"Found {len(missing)} missing cases")
    with open('missing_cases.json', 'w') as f:
        json.dump(missing, f, indent=2)

if __name__ == '__main__':
    main()
