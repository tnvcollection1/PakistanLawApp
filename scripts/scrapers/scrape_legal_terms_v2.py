#!/usr/bin/env python3
"""
Properly scrape all Legal Terms from PakistanLawSite
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

def extract_terms_proper(html):
    """Extract unique terms with their casetypeids"""
    terms = []
    # Find all table rows with searchCase class
    pattern = r'<tr class="searchCase"[^>]*casetypeid="(\d+)"[^>]*>.*?<td>\d+</td>.*?<td>[^<]*</td>.*?<td>\s*([^<]+)</td>'
    matches = re.findall(pattern, html, re.DOTALL)
    
    for cid, name in matches:
        name = name.strip()
        if name and not name.startswith('CaseLaw'):
            terms.append({
                'casetypeid': cid,
                'name': name
            })
    
    return terms

def scrape_by_letter(letter):
    """Get all terms for a letter using WordsAndPhrasesCharSearch"""
    url = "https://www.pakistanlawsite.com/Login/WordsAndPhrasesCharSearch"
    data = f"char={letter}&type=term"
    
    try:
        resp = requests.post(url, data=data, headers=HEADERS, timeout=60)
        return extract_terms_proper(resp.text)
    except Exception as e:
        print(f"Error for letter {letter}: {e}")
        return []

def main():
    print("=== Scraping Legal Terms (Proper Method) ===")
    all_terms = {}  # Use dict to dedupe by casetypeid
    
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        terms = scrape_by_letter(letter)
        for t in terms:
            all_terms[t['casetypeid']] = t
        print(f"Letter {letter}: {len(terms)} terms (unique total: {len(all_terms)})")
        time.sleep(0.3)
    
    # Convert to list
    final_terms = list(all_terms.values())
    
    print(f"\n=== RESULTS ===")
    print(f"Total unique Legal Terms: {len(final_terms)}")
    
    # Save
    with open('/app/backend/legal_terms_complete.json', 'w') as f:
        json.dump({
            'total': len(final_terms),
            'terms': final_terms
        }, f, indent=2)
    
    print(f"Saved to /app/backend/legal_terms_complete.json")
    
    # Sample
    print("\nSample terms:")
    for t in final_terms[:15]:
        print(f"  [{t['casetypeid']}] {t['name']}")

if __name__ == '__main__':
    main()
