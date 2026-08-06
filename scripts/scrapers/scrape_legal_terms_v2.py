import requests
from bs4 import BeautifulSoup
import re
import json

def scrape_legal_terms_v2():
    url = "https://pakistanlawsite.com/legal-terms"
    resp = requests.get(url, timeout=30)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    terms = []
    for item in soup.find_all('div', class_='term'):
        term = item.find('h3').get_text(strip=True) if item.find('h3') else ''
        definition = item.find('p').get_text(strip=True) if item.find('p') else ''
        terms.append({"term": term, "definition": definition})
    
    with open('legal_terms_v2.json', 'w', encoding='utf-8') as f:
        json.dump(terms, f, ensure_ascii=False, indent=2)
    
    print(f"Scraped {len(terms)} legal terms (v2)")

if __name__ == '__main__':
    scrape_legal_terms_v2()
