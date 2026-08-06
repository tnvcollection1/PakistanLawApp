#!/usr/bin/env python3
"""Fetch missing content for cases"""

import requests
import json
import sqlite3
from bs4 import BeautifulSoup
import time

def get_cases_missing_content(db_path='cases.db'):
    """Get cases that have no content"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, url FROM cases 
        WHERE content IS NULL OR content = ''
    ''')
    cases = cursor.fetchall()
    conn.close()
    return cases

def fetch_case_content(url):
    """Fetch content for a case"""
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content = soup.find('div', class_='case-content')
        return content.text.strip() if content else ''
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ''

def update_case_content(case_id, content, db_path='cases.db'):
    """Update case content in database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE cases SET content = ? WHERE id = ?',
        (content, case_id)
    )
    conn.commit()
    conn.close()

def main():
    missing = get_cases_missing_content()
    print(f"Found {len(missing)} cases missing content")
    
    for case_id, url in missing:
        print(f"Fetching content for case {case_id}...")
        content = fetch_case_content(url)
        if content:
            update_case_content(case_id, content)
        time.sleep(0.5)
    
    print("Done fetching missing content")

if __name__ == '__main__':
    main()
