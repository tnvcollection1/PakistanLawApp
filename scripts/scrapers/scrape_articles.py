#!/usr/bin/env python3
"""
Scrape all Articles from PakistanLawSite
"""
import requests
import json
import re
import time
import html as html_lib

COOKIE = "ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj; __RequestVerificationToken=cgGcIYoNV7nI6OcGKHg1CT9MoWn8iaRUpmxN-4q7PjvEfhtYG78RWELK-UA5wM8CZE0lSLjYOX-EL-aofCi3Zth-khKoUOn8cHY7Pbuzpt01; x-hng=lang=en-US&domain=www.pakistanlawsite.com"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Cookie': COOKIE,
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.pakistanlawsite.com/Login/ArticlePage'
}

def extract_articles(html_content):
    """Extract articles from HTML"""
    articles = []
    
    # Pattern to match article rows
    rows = re.findall(r'<tr class="caseType"[^>]*casetypeid="([^"]+)"[^>]*>(.*?)</tr>', html_content, re.DOTALL)
    
    for article_id, row_content in rows:
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row_content, re.DOTALL)
        if len(tds) >= 5:
            # Clean HTML
            title = re.sub(r'<[^>]+>', '', tds[1]).strip()
            title = html_lib.unescape(title)
            author = re.sub(r'<[^>]+>', '', tds[2]).strip()
            author = html_lib.unescape(author)
            category = re.sub(r'<[^>]+>', '', tds[3]).strip()
            year = re.sub(r'<[^>]+>', '', tds[4]).strip()
            
            articles.append({
                'article_id': article_id,
                'title': title,
                'author': author,
                'category': category,
                'year': year
            })
    
    return articles

def search_articles(search_text):
    """Search articles by text"""
    url = f"https://www.pakistanlawsite.com/Login/ArticlesSearch?text={search_text}"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=60)
        
        if 'HandleError' in resp.text or 'Object moved' in resp.text:
            return None  # Session expired
        
        return extract_articles(resp.text)
    except Exception as e:
        print(f"Error searching '{search_text}': {e}")
        return []

def main():
    print("=== Scraping Articles ===")
    all_articles = {}
    
    # Search by each letter
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        articles = search_articles(letter.lower())
        
        if articles is None:
            print(f"  Session expired at letter {letter}")
            break
        
        for art in articles:
            all_articles[art['article_id']] = art
        
        print(f"  Letter {letter}: {len(articles)} articles (unique total: {len(all_articles)})")
        time.sleep(0.2)
    
    # Also search by years for recent articles
    print("\n  Searching by years...")
    for year in range(2020, 2027):
        articles = search_articles(str(year))
        if articles:
            for art in articles:
                all_articles[art['article_id']] = art
            print(f"  Year {year}: {len(articles)} articles (unique total: {len(all_articles)})")
        time.sleep(0.2)
    
    # Convert to list
    final_articles = list(all_articles.values())
    
    print(f"\n=== RESULTS ===")
    print(f"Total unique Articles: {len(final_articles)}")
    
    # Save
    output = {
        'type': 'articles',
        'total': len(final_articles),
        'articles': final_articles
    }
    
    with open('/app/backend/pls_articles.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Saved to /app/backend/pls_articles.json")
    
    # Sample
    print("\nSample articles:")
    for art in final_articles[:10]:
        print(f"  [{art['article_id']}] {art['title'][:60]}...")
        print(f"      Author: {art['author']}, Year: {art['year']}")

if __name__ == '__main__':
    main()
