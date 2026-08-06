#!/usr/bin/env python3
"""
Scrape Words and Phrases from pakistanlawsite.com
Fetches all words A-Z and saves to MongoDB
"""
import subprocess
import json
import time
from datetime import datetime
from pymongo import MongoClient
from bs4 import BeautifulSoup

COOKIE = "ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj; __RequestVerificationToken=bC2SxKAWEsfNzmsxm-AYKKZcfTmzOA_A_xKIB10bKcYf6Nl6nplba8FAPIhYoalWIYJvEMksYzj0ukpCReoXe10NiNIfNzhTyDmCl1cMymA1"

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"


def fetch_words_by_letter(letter):
    """Fetch words starting with given letter"""
    url = f"https://www.pakistanlawsite.com/Login/WordsAndPhrasesCharSearch?character={letter}&type=words"
    
    try:
        result = subprocess.run([
            'curl', '-s', '--max-time', '30', url,
            '-H', f'Cookie: {COOKIE}',
            '-H', 'X-Requested-With: XMLHttpRequest',
            '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        ], capture_output=True, text=True, timeout=35)
        return result.stdout
    except:
        return ''


def parse_words(html):
    """Parse words from HTML response"""
    words = []
    soup = BeautifulSoup(html, 'html.parser')
    
    rows = soup.find_all('tr', class_='searchCase')
    for row in rows:
        tds = row.find_all('td')
        if len(tds) >= 3:
            word = tds[2].text.strip()
            word_id = row.get('casetypeid', '')
            if word and word_id:
                words.append({
                    'word_id': word_id,
                    'word': word,
                    'type': 'words'
                })
    return words


def main():
    print("=" * 60)
    print("Words & Phrases Scraper")
    print("=" * 60)
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db['words_and_phrases']
    
    # Clear existing
    collection.delete_many({})
    
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    total_words = 0
    
    for letter in letters:
        print(f"\n📚 Fetching words starting with '{letter}'...", flush=True)
        
        html = fetch_words_by_letter(letter)
        
        if 'Login' in html and 'Password' in html and len(html) < 2000:
            print("⚠️ SESSION EXPIRED!")
            break
        
        words = parse_words(html)
        
        if words:
            for word in words:
                word['letter'] = letter
                word['scraped_at'] = datetime.utcnow().isoformat()
            
            collection.insert_many(words)
            total_words += len(words)
            print(f"   ✅ Found {len(words)} words (Total: {total_words})", flush=True)
        else:
            print(f"   ⚠️ No words found", flush=True)
        
        time.sleep(0.5)
    
    # Create index
    collection.create_index('word_id', unique=True)
    collection.create_index('word')
    collection.create_index('letter')
    
    print(f"\n{'=' * 60}")
    print(f"✅ DONE: {total_words} words saved")
    print("=" * 60)
    
    client.close()


if __name__ == "__main__":
    main()
