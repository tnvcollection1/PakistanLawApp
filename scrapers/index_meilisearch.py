#!/usr/bin/env python3
"""Index cases in Meilisearch"""

import meilisearch
import json
import os

MEILI_HOST = os.getenv('MEILI_HOST', 'http://localhost:7700')
MEILI_KEY = os.getenv('MEILI_KEY', '')

def get_meili_client():
    """Get Meilisearch client"""
    return meilisearch.Client(MEILI_HOST, MEILI_KEY)

def index_cases(cases_file='all_cases.json'):
    """Index cases from JSON file"""
    with open(cases_file, 'r') as f:
        cases = json.load(f)
    
    client = get_meili_client()
    index = client.index('cases')
    
    # Configure index settings
    index.update_settings({
        'searchableAttributes': ['title', 'content', 'citation', 'court'],
        'filterableAttributes': ['court', 'date', 'category'],
        'sortableAttributes': ['date']
    })
    
    # Add documents in batches
    batch_size = 100
    for i in range(0, len(cases), batch_size):
        batch = cases[i:i + batch_size]
        index.add_documents(batch)
        print(f"Indexed batch {i//batch_size + 1}")
    
    print(f"Indexed {len(cases)} cases")

def search_cases(query, filters=None):
    """Search indexed cases"""
    client = get_meili_client()
    index = client.index('cases')
    
    search_params = {}
    if filters:
        search_params['filter'] = filters
    
    results = index.search(query, search_params)
    return results

def main():
    index_cases()

if __name__ == '__main__':
    main()
