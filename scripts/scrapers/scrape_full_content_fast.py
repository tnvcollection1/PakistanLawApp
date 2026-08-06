#!/usr/bin/env python3
"""Fast parallel full content scraper"""
import asyncio
import httpx
import logging
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

START_YEAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2020
END_YEAR = int(sys.argv[2]) if len(sys.argv) > 2 else 2010

async def get_db():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    return client[os.environ.get('DB_NAME', 'lawsite')]

async def get_cookies(db):
    doc = await db.cookies.find_one({'source': 'pakistanlawsite'})
    if doc and isinstance(doc.get('cookies'), dict):
        return '; '.join([f'{k}={v}' for k, v in doc['cookies'].items()])
    return ''

async def fetch_content(client, cookies, case_id):
    try:
        response = await client.post(
            'https://www.pakistanlawsite.com/Login/GetCaseFile',
            data={'casetypeid': case_id},
            headers={'Cookie': cookies, 'Content-Type': 'application/x-www-form-urlencoded'}
        )
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                return data[0].get('CaseFile', '')
    except:
        pass
    return None

async def main():
    db = await get_db()
    cookies = await get_cookies(db)
    
    logger.info(f"Processing years {START_YEAR} to {END_YEAR}")
    total_updated = 0
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for year in range(START_YEAR, END_YEAR - 1, -1):
            # Try both int and string year formats
            cursor = db.pls_caselaws.find({
                '$or': [{'year': year}, {'year': str(year)}],
                '$or': [
                    {'full_content': {'$exists': False}},
                    {'full_content': ''},
                    {'full_content': None}
                ]
            }).limit(500)
            
            cases = await cursor.to_list(length=500)
            if not cases:
                continue
                
            logger.info(f"Year {year}: Processing {len(cases)} cases...")
            updated = 0
            
            for case in cases:
                case_id = case.get('case_id') or case.get('case_type_id') or case.get('CaseTypeID')
                if not case_id:
                    continue
                content = await fetch_content(client, cookies, case_id)
                if content and len(content) > 100:
                    await db.pls_caselaws.update_one(
                        {'_id': case['_id']},
                        {'$set': {'full_content': content}}
                    )
                    updated += 1
                await asyncio.sleep(0.1)
            
            total_updated += updated
            logger.info(f"Year {year}: +{updated} (Total: {total_updated})")

if __name__ == "__main__":
    asyncio.run(main())
