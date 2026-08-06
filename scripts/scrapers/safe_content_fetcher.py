#!/usr/bin/env python3
"""
Safe Content Fetcher v2 - Fixed case_id format
"""
import subprocess
import os
import sys
import time
import random
import re
from datetime import datetime
from pymongo import MongoClient
from bs4 import BeautifulSoup

INSTANCE = int(sys.argv[1]) if len(sys.argv) > 1 else 1
TOTAL_INSTANCES = int(sys.argv[2]) if len(sys.argv) > 2 else 1
BATCH_SIZE = 1000

COOKIE = "ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj; __RequestVerificationToken=bC2SxKAWEsfNzmsxm-AYKKZcfTmzOA_A_xKIB10bKcYf6Nl6nplba8FAPIhYoalWIYJvEMksYzj0ukpCReoXe10NiNIfNzhTyDmCl1cMymA1"

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = 'test_database'


def fetch_content(case_id):
    try:
        result = subprocess.run([
            'curl', '-s', '--max-time', '20', '-X', 'POST',
            'https://www.pakistanlawsite.com/Login/GetCaseFile',
            '-H', f'Cookie: {COOKIE}',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            '-d', f'caseName={case_id}&headNotes=0'
        ], capture_output=True, text=True, timeout=25)
        return result.stdout
    except:
        return ''


def parse_html(html):
    if not html or len(html) < 100:
        return ''
    try:
        html = html.encode().decode('unicode_escape')
    except:
        pass
    soup = BeautifulSoup(html, 'html.parser')
    return '\n'.join([l.strip() for l in soup.get_text(separator='\n').split('\n') if l.strip()])


def main():
    print(f"[{INSTANCE}/{TOTAL_INSTANCES}] Starting...", flush=True)
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Query for proper case_id format (YYYYX###)
    query = {
        "case_id": {"$regex": r"^\d{4}[A-Z]+\d+$"},
        "$and": [
            {"$or": [{"full_content": {"$exists": False}}, {"full_content": ""}, {"full_content": None}]},
            {"$or": [{"full_judgment": {"$exists": False}}, {"full_judgment": ""}, {"full_judgment": None}, {"full_judgment": "1"}]}
        ]
    }
    
    total_pending = db.pls_caselaws.count_documents(query)
    print(f"[{INSTANCE}] Total pending: {total_pending}", flush=True)
    
    # Get cases for this instance
    skip = (INSTANCE - 1) * BATCH_SIZE
    cases = list(db.pls_caselaws.find(query, {"_id": 1, "case_id": 1}).skip(skip).limit(BATCH_SIZE))
    
    print(f"[{INSTANCE}] Processing {len(cases)} cases (skip={skip})", flush=True)
    
    success = 0
    failed = 0
    
    for i, case in enumerate(cases):
        case_id = case.get('case_id', '')
        
        # Random delay for safety
        time.sleep(random.uniform(0.3, 0.8))
        
        html = fetch_content(case_id)
        
        # Session check
        if html and 'Login' in html and 'Password' in html and len(html) < 2000:
            print(f"[{INSTANCE}] ⚠️ SESSION EXPIRED at case {i}!", flush=True)
            break
        
        content = parse_html(html)
        
        if content and len(content) > 100:
            db.pls_caselaws.update_one(
                {"_id": case["_id"]},
                {"$set": {
                    "full_content": content,
                    "content_fetched_at": datetime.utcnow().isoformat()
                }}
            )
            success += 1
            if success % 10 == 0:
                print(f"[{INSTANCE}] ✅ {case_id} | Total: {success}", flush=True)
        else:
            failed += 1
        
        if (i + 1) % 100 == 0:
            print(f"[{INSTANCE}] Progress: {i+1}/{len(cases)} | ✅{success} ❌{failed}", flush=True)
    
    print(f"[{INSTANCE}] DONE: ✅{success} ❌{failed}", flush=True)
    client.close()


if __name__ == "__main__":
    main()
