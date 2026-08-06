#!/usr/bin/env python3
"""
Scrape Pakistan Code - Federal Laws & Statutes
"""
import subprocess
import re
import csv
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
import time
import urllib.parse

OUTPUT_CSV = "/app/backend/pakistan_code_laws.csv"
BASE_URL = "https://pakistancode.gov.pk/english/"

def fetch(url):
    try:
        result = subprocess.run([
            'curl', '-sL', '--max-time', '30', '-A', 'Mozilla/5.0', url
        ], capture_output=True, text=True, timeout=35)
        return result.stdout
    except:
        return ''


def get_law_links():
    html = fetch(f"{BASE_URL}sHyuRiF.php")
    soup = BeautifulSoup(html, 'html.parser')
    
    links = []
    for a in soup.find_all('a', href=True):
        href = a.get('href', '')
        text = a.get_text(strip=True)
        
        # Match law links (UY2F pattern)
        if 'UY2F' in href and text and len(text) > 5:
            year_match = re.search(r'(\d{4})', text)
            year = year_match.group(1) if year_match else ''
            
            # Build full URL
            full_url = href if href.startswith('http') else f"{BASE_URL}{href}"
            
            links.append({
                'title': text,
                'url': full_url,
                'year': year
            })
    
    return links


def get_law_content(url):
    html = fetch(url)
    if not html:
        return '', ''
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove scripts and styles
    for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
        tag.decompose()
    
    # Get main content
    text = soup.get_text(separator='\n', strip=True)
    
    # Find PDF link
    pdf_link = ''
    for a in soup.find_all('a', href=True):
        href = a.get('href', '')
        if '.pdf' in href.lower():
            pdf_link = href if href.startswith('http') else f"https://pakistancode.gov.pk/{href}"
            break
    
    return text[:50000], pdf_link


def main():
    print("=" * 60)
    print("PAKISTAN CODE SCRAPER")
    print("=" * 60)
    
    client = MongoClient('mongodb://localhost:27017')
    db = client['test_database']
    
    print("Fetching law list...")
    laws = get_law_links()
    print(f"Found {len(laws)} laws")
    
    if not laws:
        print("No laws found!")
        return
    
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['title', 'year', 'url', 'pdf_link', 'scraped_at'])
        
        scraped = 0
        
        for i, law in enumerate(laws):
            title = law['title']
            url = law['url']
            year = law['year']
            
            content, pdf_link = get_law_content(url)
            
            writer.writerow([title, year, url, pdf_link, datetime.now().isoformat()])
            
            db.pakistan_code_laws.update_one(
                {'title': title},
                {'$set': {
                    'title': title,
                    'year': year,
                    'url': url,
                    'pdf_link': pdf_link,
                    'content': content,
                    'scraped_at': datetime.now().isoformat(),
                    'source': 'pakistancode.gov.pk'
                }},
                upsert=True
            )
            
            scraped += 1
            
            if (i + 1) % 50 == 0:
                print(f"Progress: {i+1}/{len(laws)} ({100*(i+1)/len(laws):.1f}%)")
                csvfile.flush()
            
            time.sleep(0.2)
    
    print("=" * 60)
    print(f"COMPLETE: {scraped} laws scraped")
    print(f"CSV: {OUTPUT_CSV}")
    print("=" * 60)
    
    client.close()


if __name__ == "__main__":
    main()
