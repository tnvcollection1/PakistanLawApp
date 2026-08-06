#!/usr/bin/env python3
"""Stealth full content scraper - skips cases with existing content"""
import asyncio
import httpx
import random
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
]

async def get_db():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    return client[os.environ.get('DB_NAME', 'lawsite')]

async def get_cookies(db):
    doc = await db.cookies.find_one({'source': 'pakistanlawsite'})
    if doc and isinstance(doc.get('cookies'), dict):
        return doc['cookies']
    return {}

async def fetch_content(client, cookies, case_name):
    await asyncio.sleep(random.uniform(1, 3))
    
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': '; '.join([f'{k}={v}' for k, v in cookies.items()])
    }
    
    try:
        response = await client.post(
            'https://www.pakistanlawsite.com/Login/GetCaseFile',
            data={'casetypeid': case_name},
            headers=headers
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
    
    if not cookies:
        logger.error('No cookies!')
        return
    
    logger.info('Starting scraper...')
    total_updated = 0
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        while True:
            # Get cases WITHOUT any content
            cursor = db.pls_caselaws.find({
                '$and': [
                    {'$or': [{'full_content': {'$exists': False}}, {'full_content': ''}, {'full_content': None}]},
                    {'$or': [{'full_judgment': {'$exists': False}}, {'full_judgment': ''}, {'full_judgment': None}]},
                    {'$or': [{'headnotes': {'$exists': False}}, {'headnotes': ''}, {'headnotes': None}]}
                ]
            }).limit(50)
            
            cases = await cursor.to_list(length=50)
            if not cases:
                logger.info('All cases have content!')
                break
            
            logger.info(f'Processing {len(cases)} cases...')
            
            for case in cases:
                case_name = case.get('casename')
                if not case_name:
                    continue
                
                content = await fetch_content(client, cookies, case_name)
                if content and len(content) > 100:
                    await db.pls_caselaws.update_one(
                        {'_id': case['_id']},
                        {'$set': {'full_content': content}}
                    )
                    total_updated += 1
                    if total_updated % 10 == 0:
                        logger.info(f'Updated {total_updated} cases')

if __name__ == "__main__":
    asyncio.run(main())
