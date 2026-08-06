import requests
from bs4 import BeautifulSoup
import time
import random
import json

def scrape_pls_stealth():
    base_url = "https://pakistanlawsite.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    resp = requests.get(base_url, headers=headers, timeout=30)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    data = []
    for link in soup.find_all('a', href=True)[:50]:
        data.append({"url": link['href'], "text": link.get_text(strip=True)})
    
    with open('pls_stealth.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Stealth scraped {len(data)} links")

if __name__ == '__main__':
    scrape_pls_stealth()
