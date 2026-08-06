#!/usr/bin/env python3
"""
FAST content fetcher - minimal delays
"""
import asyncio
import httpx
import os
import re
import sys
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

INSTANCE = int(sys.argv[1]) if len(sys.argv) > 1 else 1
TOTAL_INSTANCES = 10
BATCH_SIZE = 4000

COOKIE = "__RequestVerificationToken=auAnT41Ci5CAu44LxcWEzzCQk4sugOPht7YpE6Eccmkk_esV056Bp8vYd00CpHT6Ec6aBHZZsRJQzJcq8u1Gp-28aZv4aBkcQos8U5-ATUo1; ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj"
HEADERS = {
    'Cookie': COOKIE,
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest',
}
URL = "https://www.pakistanlawsite.com/Login/GetCaseFile"


def parse(html):
    try:
        html = html.encode().decode('unicode_escape')
    except:
        pass
    soup = BeautifulSoup(html, 'html.parser')
    return '\n'.join([l.strip() for l in soup.get_text(separator='\n').split('\n') if l.strip()])


def get_id(doc):
    cn = doc.get('casename', '')
    if cn and len(cn) > 4:
        return cn
    cid = doc.get('case_id', '')
    if cid.startswith('pls_'):
        p = cid[4:]
        if re.match(r'^\d{4}[A-Z]+\d+$', p):
            return p
    if cid and re.match(r'^\d{4}[A-Z]', cid):
        return cid
    ct = doc.get('case_type_id', '')
    if ct and re.match(r'^\d{4}[A-Z]', ct):
        return ct
    return None


async def main():
    print(f"[{INSTANCE}] Starting...")
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['test_database']
    
    skip = (INSTANCE - 1) * BATCH_SIZE
    cursor = db.pls_caselaws.find({
        '$and': [
            {'$or': [{'full_judgment': {'$exists': False}}, {'full_judgment': ''}, {'full_judgment': None}, {'full_judgment': '1'}]},
            {'$or': [{'full_content': {'$exists': False}}, {'full_content': ''}, {'full_content': None}]}
        ]
    }).skip(skip).limit(BATCH_SIZE)
    
    cases = await cursor.to_list(BATCH_SIZE)
    print(f"[{INSTANCE}] Processing {len(cases)} cases (skip={skip})")
    
    async with httpx.AsyncClient(timeout=20.0) as http:
        fetched = failed = 0
        
        for i, case in enumerate(cases):
            fid = get_id(case)
            if not fid:
                failed += 1
                continue
            
            try:
                r = await http.post(URL, data={'caseName': fid, 'headNotes': '0'}, headers=HEADERS)
                if r.status_code != 200:
                    failed += 1
                    continue
                
                txt = r.text
                if 'Login' in txt and 'Password' in txt and len(txt) < 2000:
                    print(f"[{INSTANCE}] SESSION EXPIRED!")
                    break
                
                if txt == '"1"' or len(txt) < 100:
                    failed += 1
                    continue
                
                content = parse(txt)
                if content and len(content) > 100:
                    await db.pls_caselaws.update_one(
                        {'_id': case['_id']},
                        {'$set': {'casename': fid, 'full_content': content, 'content_fetched_at': datetime.utcnow().isoformat()}}
                    )
                    fetched += 1
                else:
                    failed += 1
            except:
                failed += 1
            
            if (i+1) % 200 == 0:
                print(f"[{INSTANCE}] {i+1}/{len(cases)} | OK:{fetched} FAIL:{failed}")
            
            await asyncio.sleep(0.05)  # Minimal delay
    
    print(f"[{INSTANCE}] DONE: Fetched={fetched}, Failed={failed}")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
