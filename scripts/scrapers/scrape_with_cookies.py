#!/usr/bin/env python3
"""
Scrape full case content from pakistanlawsite.com using session cookies
Fetches content for cases that don't have full_content yet
"""
import os
import sys
import time
import subprocess
import json
from pymongo import MongoClient
from datetime import datetime

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = 'lawsite_db'

# Session cookies - update these when expired
COOKIES = "__RequestVerificationToken=auAnT41Ci5CAu44LxcWEzzCQk4sugOPht7YpE6Eccmkk_esV056Bp8vYd00CpHT6Ec6aBHZZsRJQzJcq8u1Gp-28aZv4aBkcQos8U5-ATUo1; ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj"

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'Cookie': COOKIES
}

def fetch_case_content(case_id):
    """Fetch full content for a single case using curl"""
    url = f"https://www.pakistanlawsite.com/Login/GetCaseFile?caseName={case_id}"
    
    curl_cmd = [
        'curl', '-s', '-X', 'POST', url,
        '-H', f'Cookie: {COOKIES}',
        '-H', 'Accept: application/json, text/plain, */*',
        '-H', 'Content-Type: application/json',
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        '--max-time', '30'
    ]
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=35)
        if result.returncode == 0 and result.stdout:
            return result.stdout.strip()
    except Exception as e:
        print(f"Error fetching {case_id}: {e}")
    
    return None

def main():
    # Get worker ID and total workers from args
    worker_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    total_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db['pls_caselaws']
    
    # Get cases without full_content
    query = {'$or': [
        {'full_content': {'$exists': False}},
        {'full_content': ''},
        {'full_content': None}
    ]}
    
    cases = list(collection.find(query, {'case_id': 1}).sort('case_id', 1))
    
    # Distribute work among workers
    my_cases = [c for i, c in enumerate(cases) if i % total_workers == worker_id]
    
    print(f"Worker {worker_id}: Processing {len(my_cases)} cases out of {len(cases)} total")
    
    success = 0
    failed = 0
    
    for i, case in enumerate(my_cases):
        case_id = case['case_id']
        content = fetch_case_content(case_id)
        
        if content and len(content) > 100 and 'login' not in content.lower()[:200]:
            collection.update_one(
                {'case_id': case_id},
                {'$set': {
                    'full_content': content,
                    'content_fetched_at': datetime.utcnow().isoformat()
                }}
            )
            success += 1
        else:
            failed += 1
            if content and 'login' in content.lower()[:200]:
                print(f"SESSION EXPIRED - Need new cookies!")
                break
        
        if (i + 1) % 50 == 0:
            print(f"Worker {worker_id}: {i+1}/{len(my_cases)} processed, {success} success, {failed} failed")
        
        time.sleep(0.2)  # Rate limiting
    
    print(f"\nWorker {worker_id} Complete: {success} success, {failed} failed")
    client.close()

if __name__ == '__main__':
    main()
