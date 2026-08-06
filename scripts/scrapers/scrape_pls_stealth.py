#!/usr/bin/env python3
"""Stealth scraper with delays and random user agents"""
import asyncio
import httpx
import random
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
]

async def get_db():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    return client[os.environ.get('DB_NAME', 'lawsite')]

async def get_cookies(db):
    doc = await db.cookies.find_one({'source': 'pakistanlawsite'})
    if doc and isinstance(doc.get('cookies'), dict):
        return doc['cookies']
    return {}

async def fetch_with_delay(client, url, cookies, data=None):
    # Random delay 2-5 seconds
    await asyncio.sleep(random.uniform(2, 5))
    
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.pakistanlawsite.com/Login/Check',
        'Origin': 'https://www.pakistanlawsite.com',
    }
    
    cookie_str = '; '.join([f'{k}={v}' for k, v in cookies.items()])
    headers['Cookie'] = cookie_str
    
    try:
        if data:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            response = await client.post(url, data=data, headers=headers)
        else:
            response = await client.get(url, headers=headers)
        return response
    except Exception as e:
        logger.error(f'Error: {e}')
        return None

async def main():
    db = await get_db()
    cookies = await get_cookies(db)
    
    if not cookies:
        logger.error('No cookies found!')
        return
    
    logger.info('Starting stealth scraper...')
    
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        # Test connection first
        response = await fetch_with_delay(
            client,
            'https://www.pakistanlawsite.com/Login/IndexSearch',
            cookies,
            {'IndexSearch': '2024 PLD 1'}
        )
        
        if response and response.status_code == 200:
            logger.info(f'SUCCESS! Got {len(response.text)} bytes')
            logger.info(response.text[:500])
        else:
            logger.error(f'Failed: {response.status_code if response else "No response"}')

if __name__ == "__main__":
    asyncio.run(main())
