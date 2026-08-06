#!/usr/bin/env python3
"""
Fast content fetcher using subprocess curl
"""
import subprocess
import os
import re
import sys
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup

INSTANCE = int(sys.argv[1]) if len(sys.argv) > 1 else 1
BATCH_SIZE = 4000
SKIP = (INSTANCE - 1) * BATCH_SIZE

COOKIE = "__RequestVerificationToken=auAnT41Ci5CAu44LxcWEzzCQk4sugOPht7YpE6Eccmkk_esV056Bp8vYd00CpHT6Ec6aBHZZsRJQzJcq8u1Gp-28aZv4aBkcQos8U5-ATUo1; ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj"


def get_id(doc):
    cn = doc.get('casename', '')
    if cn and len(cn) > 4 and re.match(r'^\d{4}[A-Z]', cn):
        return cn
    cid = doc.get('case_id', '')
    if cid and cid.startswith('pls_'):
        p = cid[4:]
        if re.match(r'^\d{4}[A-Z]+\d+$', p):
            return p
    if cid and re.match(r'^\d{4}[A-Z]', cid):
        return cid
    ct = doc.get('case_type_id', '')
    if ct and re.match(r'^\d{4}[A-Z]', ct):
        return ct
    return None


def fetch(caseid):
    try:
        result = subprocess.run([
            'curl', '-s', '--max-time', '15', '-X', 'POST',
            'https://www.pakistanlawsite.com/Login/GetCaseFile',
            '-H', f'Cookie: {COOKIE}',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-d', f'caseName={caseid}&headNotes=0'
        ], capture_output=True, text=True, timeout=20)
        return result.stdout
    except:
        return ''


def parse(html):
    if not html or len(html) < 100:
        return ''
    try:
        html = html.encode().decode('unicode_escape')
    except:
        pass
    soup = BeautifulSoup(html, 'html.parser')
    return '\n'.join([l.strip() for l in soup.get_text(separator='\n').split('\n') if l.strip()])


def main():
    print(f"[{INSTANCE}] Starting (skip={SKIP})", flush=True)
    
    client = MongoClient('mongodb://localhost:27017')
    db = client['test_database']
    
    cursor = db.pls_caselaws.find({
        '$and': [
            {'$or': [{'full_judgment': {'$exists': False}}, {'full_judgment': ''}, {'full_judgment': None}, {'full_judgment': '1'}]},
            {'$or': [{'full_content': {'$exists': False}}, {'full_content': ''}, {'full_content': None}]}
        ]
    }).skip(SKIP).limit(BATCH_SIZE)
    
    cases = list(cursor)
    print(f"[{INSTANCE}] Found {len(cases)} cases", flush=True)
    
    fetched = failed = 0
    
    for i, case in enumerate(cases):
        fid = get_id(case)
        if not fid:
            failed += 1
            continue
        
        html = fetch(fid)
        
        if 'Login' in html and 'Password' in html and len(html) < 2000:
            print(f"[{INSTANCE}] SESSION EXPIRED!", flush=True)
            break
        
        content = parse(html)
        
        if content and len(content) > 100:
            db.pls_caselaws.update_one(
                {'_id': case['_id']},
                {'$set': {
                    'casename': fid,
                    'full_content': content,
                    'content_fetched_at': datetime.utcnow().isoformat()
                }}
            )
            fetched += 1
        else:
            failed += 1
        
        if (i + 1) % 100 == 0:
            print(f"[{INSTANCE}] {i+1}/{len(cases)} | OK:{fetched} FAIL:{failed}", flush=True)
    
    print(f"[{INSTANCE}] DONE: Fetched={fetched}, Failed={failed}", flush=True)
    client.close()


if __name__ == "__main__":
    main()
