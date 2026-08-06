#!/usr/bin/env python3
"""
Pakistan Law Site - Words, Phrases, Terms, Topics, Maxims Scraper
Uses the discovered API endpoints to scrape additional legal content
"""
import asyncio
import httpx
import logging
import re
import os
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COOKIE = "ASP.NET_SessionId=fy1xlmaj0dlu1ocwuxuzfmy2; __RequestVerificationToken=zNZnft3PlZqaRI3r4H-5HF18AyM1XqageFEKpY03fO72Osz9ItAe1pYwviWuIofab8c4N8vm3uWKoThtixgdsAtLS9k85jvhx3FkI6v_PD41"

HEADERS = {
    'Cookie': COOKIE,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

BASE_URL = "https://www.pakistanlawsite.com"

# Endpoints discovered from HAR analysis
ENDPOINTS = {
    'words': '/Login/WordsAndPhrases?type=words',
    'topics': '/Login/TopicPage',
    'maxims': '/Login/Maxim?type=maxim',
    'terms': '/Login/LegalTerms',
    'dictionary': '/Login/DictionaryPage',
    'articles': '/Login/ArticlePage',
}

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


async def get_db():
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    client = AsyncIOMotorClient(mongo_url)
    return client[db_name]


async def fetch_page(http_client, url):
    try:
        response = await http_client.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        logger.debug(f"Error: {e}")
    return None


def extract_items_and_cases(html_content, section_type):
    """Extract items (words, topics, etc.) and related case links"""
    items = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find links with case references
    for a in soup.find_all('a', href=True):
        href = a.get('href', '')
        text = a.get_text(strip=True)
        
        # Look for links that lead to cases
        if any(x in href.lower() for x in ['case', 'search', 'get', 'list']):
            item_data = {
                'name': text[:500],
                'href': href,
                'type': section_type,
            }
            items.append(item_data)
    
    # Find case citations in text
    for elem in soup.find_all(['td', 'div', 'p', 'span']):
        text = elem.get_text(strip=True)
        citation_match = re.search(r'(\d{4})\s*(PLD|SCMR|CLC|PCrLJ|YLR|MLD|PLC|PTD)\s*(\d+)', text)
        
        if citation_match and len(text) > 30:
            case_data = {
                'title': text[:500],
                'citation': f"{citation_match.group(1)} {citation_match.group(2)} {citation_match.group(3)}",
                'year': int(citation_match.group(1)),
                'journal': citation_match.group(2),
                'type': section_type,
            }
            
            # Find nearest link
            link = elem.find('a', href=True)
            if link:
                case_data['href'] = link.get('href', '')
            
            items.append(case_data)
    
    return items


async def scrape_section(http_client, db, section_name, endpoint):
    """Scrape a section by alphabet"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Scraping {section_name.upper()}")
    logger.info(f"{'='*60}")
    
    url = f"{BASE_URL}{endpoint}"
    total_new = 0
    
    # Fetch main page
    html = await fetch_page(http_client, url)
    if not html:
        logger.error(f"Failed to fetch {section_name}")
        return 0
    
    if 'Login' in html and len(html) < 2000:
        logger.error("SESSION EXPIRED!")
        return 0
    
    # Try alphabet-based pagination
    for letter in ALPHABET:
        letter_url = f"{url}&alphabet={letter}" if '?' in url else f"{url}?alphabet={letter}"
        letter_html = await fetch_page(http_client, letter_url)
        
        if letter_html:
            items = extract_items_and_cases(letter_html, section_name)
            
            for item in items:
                case_id = f"pls_{section_name}_{letter}_{item.get('name', item.get('title', ''))[:60]}"
                case_id = case_id.replace(' ', '_').replace('/', '_')
                
                item['case_id'] = case_id
                item['source'] = f'pakistanlawsite_{section_name}'
                item['scraped_at'] = datetime.utcnow().isoformat()
                
                existing = await db.pls_caselaws.find_one({'case_id': case_id})
                if not existing:
                    await db.pls_caselaws.insert_one(item)
                    total_new += 1
        
        await asyncio.sleep(0.3)
    
    # Also extract from main page
    items = extract_items_and_cases(html, section_name)
    for item in items:
        case_id = f"pls_{section_name}_main_{item.get('name', item.get('title', ''))[:60]}"
        case_id = case_id.replace(' ', '_').replace('/', '_')
        
        item['case_id'] = case_id
        item['source'] = f'pakistanlawsite_{section_name}'
        item['scraped_at'] = datetime.utcnow().isoformat()
        
        existing = await db.pls_caselaws.find_one({'case_id': case_id})
        if not existing:
            await db.pls_caselaws.insert_one(item)
            total_new += 1
    
    logger.info(f"  {section_name}: +{total_new} items")
    return total_new


async def main():
    logger.info("=" * 70)
    logger.info("Pakistan Law Site - Additional Content Scraper")
    logger.info("=" * 70)
    
    db = await get_db()
    
    initial_count = await db.pls_caselaws.count_documents({})
    logger.info(f"Starting count: {initial_count:,}")
    
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as http_client:
        total_new = 0
        
        for section_name, endpoint in ENDPOINTS.items():
            new_items = await scrape_section(http_client, db, section_name, endpoint)
            total_new += new_items
    
    final_count = await db.pls_caselaws.count_documents({})
    
    logger.info("\n" + "=" * 70)
    logger.info("COMPLETE")
    logger.info("=" * 70)
    logger.info(f"New items: {total_new:,}")
    logger.info(f"Total: {initial_count:,} → {final_count:,}")


if __name__ == "__main__":
    asyncio.run(main())
