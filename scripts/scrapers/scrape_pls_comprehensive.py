#!/usr/bin/env python3
"""
Pakistan Law Site Comprehensive Scraper
Uses discovered API endpoints
"""
import subprocess
import re
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COOKIE = "ASP.NET_SessionId=fy1xlmaj0dlu1ocwuxuzfmy2; __RequestVerificationToken=zNZnft3PlZqaRI3r4H-5HF18AyM1XqageFEKpY03fO72Osz9ItAe1pYwviWuIofab8c4N8vm3uWKoThtixgdsAtLS9k85jvhx3FkI6v_PD41"
BASE = "https://www.pakistanlawsite.com"


def fetch(url, xhr=False):
    """Fetch URL using curl"""
    cmd = ['curl', '-s', '--max-time', '60', '-H', f'Cookie: {COOKIE}']
    if xhr:
        cmd.extend(['-H', 'X-Requested-With: XMLHttpRequest'])
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def extract_cases(html):
    """Extract case citations and case IDs"""
    cases = []
    
    # Find casetypeid attributes
    ids = re.findall(r'casetypeid="([^"]+)"', html)
    for id in ids:
        cases.append({'case_type_id': id})
    
    # Find citation patterns
    citations = re.findall(r'(\d{4})\s*(PLD|SCMR|CLC|PCrLJ|YLR|MLD|PLC|PTD)\s*(\d+)', html)
    for c in citations:
        cases.append({
            'year': int(c[0]),
            'journal': c[1],
            'page': c[2],
            'citation': f"{c[0]} {c[1]} {c[2]}"
        })
    
    return cases


async def get_db():
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    client = AsyncIOMotorClient(mongo_url)
    return client[db_name]


async def scrape_statutes_search(db):
    """Search statutes by keywords"""
    logger.info("\n[1] Scraping Statutes via Search API...")
    total = 0
    
    keywords = [
        'constitution', 'criminal', 'civil', 'tax', 'property', 'family',
        'labour', 'banking', 'company', 'insurance', 'customs', 'excise',
        'income', 'sales', 'stamp', 'registration', 'evidence', 'limitation',
        'contract', 'partnership', 'trust', 'guardians', 'minor', 'arbitration',
        'administration', 'service', 'pension', 'election', 'local', 'police',
        'pakistan', 'federal', 'provincial', 'supreme', 'high', 'court'
    ]
    
    for kw in keywords:
        html = fetch(f"{BASE}/Login/GetStatuesSearch?caseName={kw}", xhr=True)
        
        if not html or 'resource cannot be found' in html.lower():
            continue
        
        soup = BeautifulSoup(html, 'html.parser')
        
        for row in soup.find_all('tr', class_='caseType'):
            case_id = row.get('casetypeid', '')
            if not case_id:
                continue
            
            # Get text from row
            text = row.get_text(strip=True)
            
            statute_data = {
                'statute_id': case_id,
                'name': text[:500],
                'search_keyword': kw,
                'source': 'pakistanlawsite_statute',
                'scraped_at': datetime.utcnow().isoformat()
            }
            
            existing = await db.pls_statutes.find_one({'statute_id': case_id})
            if not existing:
                await db.pls_statutes.insert_one(statute_data)
                total += 1
        
        if total > 0 and kw in ['tax', 'court', 'pakistan']:
            logger.info(f"    {kw}: +{total} total statutes")
    
    logger.info(f"  Statutes search: +{total} new")
    return total


async def scrape_words_phrases(db):
    """Scrape words and phrases page"""
    logger.info("\n[2] Scraping Words & Phrases...")
    total = 0
    
    html = fetch(f"{BASE}/Login/WordsAndPhrases?type=words")
    soup = BeautifulSoup(html, 'html.parser')
    
    for link in soup.find_all('a', href=True):
        text = link.get_text(strip=True)
        href = link.get('href', '')
        
        if text and len(text) > 2 and text not in ['Home', 'Login', 'Search']:
            word_data = {
                'word': text[:200],
                'url': href if href.startswith('http') else f"{BASE}{href}",
                'source': 'pakistanlawsite_words',
                'scraped_at': datetime.utcnow().isoformat()
            }
            
            existing = await db.pls_words_phrases.find_one({'word': text[:200]})
            if not existing:
                await db.pls_words_phrases.insert_one(word_data)
                total += 1
    
    logger.info(f"  Words & phrases: +{total} new")
    return total


async def scrape_maxims(db):
    """Scrape legal maxims"""
    logger.info("\n[3] Scraping Maxims...")
    total = 0
    
    html = fetch(f"{BASE}/Login/Maxim?type=maxim")
    soup = BeautifulSoup(html, 'html.parser')
    
    for elem in soup.find_all(['a', 'li', 'div']):
        text = elem.get_text(strip=True)
        
        # Maxims are typically Latin phrases
        if text and len(text) > 5 and len(text) < 500:
            # Skip navigation items
            if text.lower() in ['home', 'login', 'search', 'about', 'contact']:
                continue
            
            maxim_data = {
                'maxim': text[:500],
                'source': 'pakistanlawsite_maxims',
                'scraped_at': datetime.utcnow().isoformat()
            }
            
            existing = await db.pls_maxims.find_one({'maxim': text[:500]})
            if not existing:
                await db.pls_maxims.insert_one(maxim_data)
                total += 1
    
    logger.info(f"  Maxims: +{total} new")
    return total


async def scrape_articles(db):
    """Scrape articles page"""
    logger.info("\n[4] Scraping Articles...")
    total = 0
    
    html = fetch(f"{BASE}/Login/ArticlePage")
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find article links
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        if 'ArticleDetail' in href or 'fileID' in href:
            # Extract fileID
            match = re.search(r'fileID=(\d+)', href)
            file_id = match.group(1) if match else None
            
            article_data = {
                'title': text[:500],
                'file_id': file_id,
                'url': href if href.startswith('http') else f"{BASE}{href}",
                'source': 'pakistanlawsite_articles',
                'scraped_at': datetime.utcnow().isoformat()
            }
            
            existing = await db.pls_articles.find_one({'title': text[:500]})
            if not existing:
                await db.pls_articles.insert_one(article_data)
                total += 1
    
    logger.info(f"  Articles: +{total} new")
    return total


async def scrape_dictionary(db):
    """Scrape dictionary page"""
    logger.info("\n[5] Scraping Dictionary...")
    total = 0
    
    html = fetch(f"{BASE}/Login/DictionaryPage")
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find dictionary entries
    for elem in soup.find_all(['dt', 'dd', 'li']):
        text = elem.get_text(strip=True)
        
        if text and len(text) > 3 and len(text) < 1000:
            dict_data = {
                'term': text[:500],
                'source': 'pakistanlawsite_dictionary',
                'scraped_at': datetime.utcnow().isoformat()
            }
            
            existing = await db.pls_dictionary.find_one({'term': text[:500]})
            if not existing:
                await db.pls_dictionary.insert_one(dict_data)
                total += 1
    
    logger.info(f"  Dictionary: +{total} new")
    return total


async def scrape_topics(db):
    """Scrape topics page"""
    logger.info("\n[6] Scraping Topics...")
    total = 0
    
    html = fetch(f"{BASE}/Login/TopicPage")
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find topic IDs
    for elem in soup.find_all(attrs={'topicid': True}):
        topic_id = elem.get('topicid')
        text = elem.get_text(strip=True)
        
        topic_data = {
            'topic_id': topic_id,
            'name': text[:500],
            'source': 'pakistanlawsite_topics',
            'scraped_at': datetime.utcnow().isoformat()
        }
        
        existing = await db.pls_topics.find_one({'topic_id': topic_id})
        if not existing:
            await db.pls_topics.insert_one(topic_data)
            total += 1
    
    logger.info(f"  Topics: +{total} new")
    return total


async def scrape_statute_by_letter(db):
    """Scrape statutes by letter A-Z"""
    logger.info("\n[7] Scraping Statutes A-Z...")
    total = 0
    
    import string
    for char in string.ascii_uppercase:
        html = fetch(f"{BASE}/Login/StatuecharSearch?character={char}")
        
        if not html or 'resource cannot be found' in html.lower():
            continue
        
        soup = BeautifulSoup(html, 'html.parser')
        
        for row in soup.find_all('tr', class_='caseType'):
            case_id = row.get('casetypeid', '')
            text = row.get_text(strip=True)
            
            if case_id or text:
                statute_data = {
                    'statute_id': case_id or f"letter_{char}_{text[:50]}".replace(' ', '_'),
                    'name': text[:500],
                    'letter': char,
                    'source': 'pakistanlawsite_statute_az',
                    'scraped_at': datetime.utcnow().isoformat()
                }
                
                key = statute_data['statute_id']
                existing = await db.pls_statutes.find_one({'statute_id': key})
                if not existing:
                    await db.pls_statutes.insert_one(statute_data)
                    total += 1
        
        if char in ['E', 'M', 'S', 'Z']:
            logger.info(f"    {char}: +{total} total")
    
    logger.info(f"  Statutes A-Z: +{total} new")
    return total


async def main():
    logger.info("=" * 60)
    logger.info("Pakistan Law Site Comprehensive Scraper")
    logger.info("=" * 60)
    
    db = await get_db()
    
    # Get initial counts
    cases = await db.pls_caselaws.count_documents({})
    statutes = await db.pls_statutes.count_documents({})
    words = await db.pls_words_phrases.count_documents({})
    maxims = await db.pls_maxims.count_documents({})
    articles = await db.pls_articles.count_documents({})
    
    logger.info(f"\nInitial counts:")
    logger.info(f"  Cases: {cases:,}")
    logger.info(f"  Statutes: {statutes:,}")
    logger.info(f"  Words/Phrases: {words:,}")
    logger.info(f"  Maxims: {maxims:,}")
    logger.info(f"  Articles: {articles:,}")
    
    # Run scrapers
    await scrape_statutes_search(db)
    await scrape_statute_by_letter(db)
    await scrape_words_phrases(db)
    await scrape_maxims(db)
    await scrape_articles(db)
    await scrape_dictionary(db)
    await scrape_topics(db)
    
    # Final counts
    cases2 = await db.pls_caselaws.count_documents({})
    statutes2 = await db.pls_statutes.count_documents({})
    words2 = await db.pls_words_phrases.count_documents({})
    maxims2 = await db.pls_maxims.count_documents({})
    articles2 = await db.pls_articles.count_documents({})
    
    logger.info("\n" + "=" * 60)
    logger.info("SCRAPING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"  Cases: {cases:,} → {cases2:,} (+{cases2-cases})")
    logger.info(f"  Statutes: {statutes:,} → {statutes2:,} (+{statutes2-statutes})")
    logger.info(f"  Words: {words:,} → {words2:,} (+{words2-words})")
    logger.info(f"  Maxims: {maxims:,} → {maxims2:,} (+{maxims2-maxims})")
    logger.info(f"  Articles: {articles:,} → {articles2:,} (+{articles2-articles})")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
