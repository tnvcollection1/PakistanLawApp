#!/usr/bin/env python3
"""
Scrape Legal Terms from pakistanlawsite.com
Similar to Words & Phrases but type=term
"""
import subprocess
import time
from datetime import datetime
from pymongo import MongoClient
from bs4 import BeautifulSoup

COOKIE = "ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj; __RequestVerificationToken=bC2SxKAWEsfNzmsxm-AYKKZcfTmzOA_A_xKIB10bKcYf6Nl6nplba8FAPIhYoalWIYJvEMksYzj0ukpCReoXe10NiNIfNzhTyDmCl1cMymA1"

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"


def fetch_terms_by_letter(letter):
    """Fetch legal terms starting with given letter"""
    url = f"https://www.pakistanlawsite.com/Login/WordsAndPhrasesCharSearch?character={letter}&type=term"
    
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


def parse_terms(html):
    """Parse terms from HTML response"""
    terms = []
    soup = BeautifulSoup(html, 'html.parser')
    
    rows = soup.find_all('tr', class_='searchCase')
    for row in rows:
        tds = row.find_all('td')
        if len(tds) >= 3:
            term = tds[2].text.strip()
            term_id = row.get('casetypeid', '')
            if term and term_id:
                terms.append({
                    'term_id': term_id,
                    'term': term,
                    'type': 'legal_term'
                })
    return terms


def main():
    print("=" * 60)
    print("Legal Terms Scraper")
    print("=" * 60)
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db['legal_terms']
    
    # Clear existing
    collection.delete_many({})
    
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    total_terms = 0
    
    for letter in letters:
        print(f"📚 Fetching terms starting with '{letter}'...", end=" ", flush=True)
        
        html = fetch_terms_by_letter(letter)
        
        if 'Login' in html and 'Password' in html and len(html) < 2000:
            print("⚠️ SESSION EXPIRED!")
            break
        
        terms = parse_terms(html)
        
        if terms:
            for term in terms:
                term['letter'] = letter
                term['scraped_at'] = datetime.utcnow().isoformat()
            
            collection.insert_many(terms)
            total_terms += len(terms)
            print(f"✅ {len(terms)} terms (Total: {total_terms})", flush=True)
        else:
            print(f"0 terms", flush=True)
        
        time.sleep(0.5)
    
    # Create indexes
    collection.create_index('term_id')
    collection.create_index('term')
    collection.create_index('letter')
    
    print(f"\n{'=' * 60}")
    print(f"✅ DONE: {total_terms} legal terms saved")
    print("=" * 60)
    
    client.close()


if __name__ == "__main__":
    main()
