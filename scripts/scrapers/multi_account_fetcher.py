#!/usr/bin/env python3
"""
Multi-Account Content Fetcher
Uses account rotation to reduce ban risk
"""
import subprocess
import sys
import time
import random
from datetime import datetime
from pymongo import MongoClient
from bs4 import BeautifulSoup

INSTANCE = int(sys.argv[1]) if len(sys.argv) > 1 else 1
TOTAL_INSTANCES = int(sys.argv[2]) if len(sys.argv) > 2 else 1

# TWO ACCOUNTS - Rotate between them
ACCOUNTS = [
    "ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj; __RequestVerificationToken=bC2SxKAWEsfNzmsxm-AYKKZcfTmzOA_A_xKIB10bKcYf6Nl6nplba8FAPIhYoalWIYJvEMksYzj0ukpCReoXe10NiNIfNzhTyDmCl1cMymA1",
    "ASP.NET_SessionId=ugjhryc1iem0i2ikezqwv1g2; __RequestVerificationToken=wOhyKH8zHWgQUY9RPgQpiFPXFdwEttvSrsO9ciFwnFv21wqBPLMqgzq7A3IStZbWP7zEClRapyCIO9Pe4AEBQkg_T8tePmyVtjRkpFfj0OM1"
]

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

# Use account based on instance number (odd=account1, even=account2)
MY_COOKIE = ACCOUNTS[INSTANCE % 2]


def fetch_content(case_id):
    try:
        result = subprocess.run([
            'curl', '-s', '--max-time', '15', '-X', 'POST',
            'https://www.pakistanlawsite.com/Login/GetCaseFile',
            '-H', f'Cookie: {MY_COOKIE}',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            '-d', f'caseName={case_id}&headNotes=0'
        ], capture_output=True, text=True, timeout=20)
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
    account_num = (INSTANCE % 2) + 1
    print(f"[{INSTANCE}] Using Account {account_num}", flush=True)
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    col = db['pls_caselaws']
    
    # Get pending cases
    query = {
        "case_id": {"$regex": r"^\d{4}[A-Z]+\d+$"},
        "$and": [
            {"$or": [{"full_content": {"$exists": False}}, {"full_content": ""}, {"full_content": None}]},
            {"$or": [{"full_judgment": {"$exists": False}}, {"full_judgment": ""}, {"full_judgment": None}, {"full_judgment": "1"}]}
        ]
    }
    
    skip = (INSTANCE - 1) * 1000
    cases = list(col.find(query, {"_id": 1, "case_id": 1}).skip(skip).limit(1000))
    
    print(f"[{INSTANCE}] Processing {len(cases)} cases", flush=True)
    
    success = 0
    failed = 0
    
    for i, case in enumerate(cases):
        case_id = case.get('case_id', '')
        
        time.sleep(random.uniform(0.4, 0.8))
        
        html = fetch_content(case_id)
        
        if html and 'Login' in html and 'Password' in html and len(html) < 2000:
            print(f"[{INSTANCE}] ⚠️ Account {account_num} SESSION EXPIRED!", flush=True)
            break
        
        content = parse_html(html)
        
        if content and len(content) > 100:
            col.update_one(
                {"_id": case["_id"]},
                {"$set": {"full_content": content, "fetched_at": datetime.utcnow().isoformat()}}
            )
            success += 1
            if success % 10 == 0:
                print(f"[{INSTANCE}] A{account_num} ✅ {success} done", flush=True)
        else:
            failed += 1
        
        if (i + 1) % 100 == 0:
            print(f"[{INSTANCE}] Progress: {i+1}/{len(cases)} | ✅{success} ❌{failed}", flush=True)
    
    print(f"[{INSTANCE}] DONE: ✅{success} ❌{failed}", flush=True)
    client.close()


if __name__ == "__main__":
    main()
