#!/usr/bin/env python3
"""
Scrape Dictionary from PakistanLawSite
"""
import requests
import json
import re
import html as html_lib
import time

COOKIE = "ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj; __RequestVerificationToken=cgGcIYoNV7nI6OcGKHg1CT9MoWn8iaRUpmxN-4q7PjvEfhtYG78RWELK-UA5wM8CZE0lSLjYOX-EL-aofCi3Zth-khKoUOn8cHY7Pbuzpt01; x-hng=lang=en-US&domain=www.pakistanlawsite.com"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Cookie': COOKIE,
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.pakistanlawsite.com/Login/DictionaryPage'
}

def extract_dictionary_items(html_content):
    """Extract dictionary items from HTML"""
    items = []
    pattern = r'<tr class="caseType"[^>]*casetypeid="(\d+)"[^>]*>.*?<td>\d+</td>.*?<td[^>]*>([^<]+)</td>.*?<td>([^<]+)</td>'
    matches = re.findall(pattern, html_content, re.DOTALL)
    
    for item_id, word, meaning in matches:
        word = html_lib.unescape(word.strip())
        meaning = html_lib.unescape(meaning.strip())
        if word and meaning:
            items.append({
                'item_id': item_id,
                'word': word,
                'meaning': meaning[:500] + '...' if len(meaning) > 500 else meaning
            })
    
    return items

def search_dictionary(letter):
    """Search dictionary by letter"""
    url = f"https://www.pakistanlawsite.com/Login/DictionarySearch?text={letter}"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=60)
        if 'HandleError' in resp.text:
            return None
        return extract_dictionary_items(resp.text)
    except Exception as e:
        print(f"Error for {letter}: {e}")
        return []

def main():
    print("=== Scraping Dictionary ===")
    all_items = {}
    
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        items = search_dictionary(letter.lower())
        
        if items is None:
            print(f"  Session expired at letter {letter}")
            break
        
        for item in items:
            all_items[item['item_id']] = item
        
        print(f"  Letter {letter}: {len(items)} items (unique total: {len(all_items)})")
        time.sleep(0.2)
    
    final_items = list(all_items.values())
    
    print(f"\n=== RESULTS ===")
    print(f"Total unique Dictionary items: {len(final_items)}")
    
    # Save
    output = {
        'type': 'dictionary',
        'total': len(final_items),
        'items': final_items
    }
    
    with open('/app/backend/pls_dictionary.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Saved to /app/backend/pls_dictionary.json")
    
    # Sample
    print("\nSample items:")
    for item in final_items[:5]:
        print(f"  [{item['item_id']}] {item['word'][:40]}...")
        print(f"      Meaning: {item['meaning'][:60]}...")

if __name__ == '__main__':
    main()
