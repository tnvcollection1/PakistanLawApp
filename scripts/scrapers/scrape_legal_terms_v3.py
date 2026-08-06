import requests
from bs4 import BeautifulSoup
import re
import json
import time

def scrape_legal_terms_v3():
    base_url = "https://pakistanlawsite.com/legal-terms"
    terms = []
    page = 1
    
    while True:
        url = f"{base_url}?page={page}"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        items = soup.find_all('div', class_='term')
        if not items:
            break
        
        for item in items:
            term = item.find('h3').get_text(strip=True) if item.find('h3') else ''
            definition = item.find('p').get_text(strip=True) if item.find('p') else ''
            terms.append({"term": term, "definition": definition})
        
        page += 1
        time.sleep(1)
    
    with open('legal_terms_v3.json', 'w', encoding='utf-8') as f:
        json.dump(terms, f, ensure_ascii=False, indent=2)
    
    print(f"Scraped {len(terms)} legal terms (v3)")

if __name__ == '__main__':
    scrape_legal_terms_v3()
