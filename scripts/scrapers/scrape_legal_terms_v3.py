#!/usr/bin/env python3
"""
Scrape all Legal Terms from PakistanLawSite using GET method
"""
import requests
import json
import re
import time

COOKIE = "ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj; __RequestVerificationToken=cgGcIYoNV7nI6OcGKHg1CT9MoWn8iaRUpmxN-4q7PjvEfhtYG78RWELK-UA5wM8CZE0lSLjYOX-EL-aofCi3Zth-khKoUOn8cHY7Pbuzpt01; x-hng=lang=en-US&domain=www.pakistanlawsite.com"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Cookie': COOKIE,
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.pakistanlawsite.com/Login/LegalTerms'
}

def extract_terms(html):
    """Extract terms from HTML"""
    terms = []
    # Pattern to match: casetypeid="X" ... <td>name</td>
    rows = re.findall(r'<tr[^>]*casetypeid="(\d+)"[^>]*>.*?</tr>', html, re.DOTALL)
    
    for row in rows:
        # Find the term name (usually 3rd td)
        tds = re.findall(r'<td>([^<]+)</td>', row)
        if len(tds) >= 3:
            name = tds[2].strip()
            if name and not name.startswith('CaseLaw') and len(name) > 1:
                cid = re.search(r'casetypeid="(\d+)"', row)
                if cid:
                    terms.append({
                        'casetypeid': cid.group(1),
                        'name': name
                    })
    
    return terms

def scrape_all_terms():
    """Scrape all legal terms"""
    all_terms = {}
    
    # Use search with each letter
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        url = f"https://www.pakistanlawsite.com/Login/SearchWordAndPhrases?text={letter.lower()}&type=term"
        
        try:
            resp = requests.get(url, headers=HEADERS, timeout=60)
            html = resp.text
            
            if 'HandleError' in html:
                print(f"Session expired at letter {letter}")
                break
            
            terms = extract_terms(html)
            for t in terms:
                all_terms[t['casetypeid']] = t
            
            print(f"Letter {letter}: {len(terms)} terms (unique total: {len(all_terms)})")
            time.sleep(0.3)
            
        except Exception as e:
            print(f"Error for {letter}: {e}")
    
    return list(all_terms.values())

def main():
    print("=== Scraping Legal Terms ===")
    terms = scrape_all_terms()
    
    print(f"\n=== RESULTS ===")
    print(f"Total unique Legal Terms: {len(terms)}")
    
    # Save
    output = {
        'type': 'legal_terms',
        'total': len(terms),
        'terms': terms
    }
    
    with open('/app/backend/legal_terms_final.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Saved to /app/backend/legal_terms_final.json")
    
    # Sample
    print("\nSample terms:")
    for t in terms[:15]:
        print(f"  [{t['casetypeid']}] {t['name']}")

if __name__ == '__main__':
    main()
