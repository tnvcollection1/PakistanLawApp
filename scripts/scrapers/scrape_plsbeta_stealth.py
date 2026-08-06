#!/usr/bin/env python3
"""Stealth PLSBeta full content scraper with delays"""
import asyncio
import httpx
import random
import logging
import os
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

async def get_db():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    return client[os.environ.get('DB_NAME', 'lawsite')]

async def get_cookies(db):
    doc = await db.cookies.find_one({'source': 'plsbeta'})
    if doc and isinstance(doc.get('cookies'), dict):
        return doc['cookies']
    return {}

async def fetch_case_content(client, cookies, case_id):
    await asyncio.sleep(random.uniform(2, 4))
    
    cookie_str = '; '.join([f'{k}={v}' for k, v in cookies.items()])
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Cookie': cookie_str,
        'Referer': 'http://www.plsbeta.com/LawOnline/law/main.asp'
    }
    
    try:
        # Try to get case details
        url = f'http://www.plsbeta.com/LawOnline/law/Result.asp?description=Case&CatSearch=Case&ID={case_id}'
        response = await client.get(url, headers=headers, follow_redirects=True)
        
        if response.status_code == 200 and 'Login.asp' not in str(response.url):
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract content from the page
            content_div = soup.find('body')
            if content_div:
                text = content_div.get_text(separator='\n', strip=True)
                if len(text) > 200:
                    return text
    except Exception as e:
        logger.error(f'Error: {e}')
    return None

async def main():
    db = await get_db()
    cookies = await get_cookies(db)
    
    if not cookies:
        logger.error('No cookies!')
        return
    
    logger.info('Starting PLSBeta stealth scraper...')
    total_updated = 0
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Get cases without full_content
        cursor = db.plsbeta_caselaws.find({
            '$or': [
                {'full_content': {'$exists': False}},
                {'full_content': ''},
                {'full_content': None}
            ]
        }).limit(100)
        
        cases = await cursor.to_list(length=100)
        logger.info(f'Found {len(cases)} cases to process')
        
        for case in cases:
            case_id = case.get('id') or case.get('case_id') or case.get('ID')
            if not case_id:
                continue
            
            content = await fetch_case_content(client, cookies, case_id)
            if content:
                await db.plsbeta_caselaws.update_one(
                    {'_id': case['_id']},
                    {'$set': {'full_content': content}}
                )
                total_updated += 1
                logger.info(f'Updated {total_updated} cases')

if __name__ == "__main__":
    asyncio.run(main())
