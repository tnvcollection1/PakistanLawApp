import requests
from bs4 import BeautifulSoup
import json

def scrape_dictionary():
    url = "https://pakistanlawsite.com/dictionary"
    resp = requests.get(url, timeout=30)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    entries = []
    for item in soup.find_all('div', class_='dict-entry'):
        word = item.find('dt').get_text(strip=True) if item.find('dt') else ''
        meaning = item.find('dd').get_text(strip=True) if item.find('dd') else ''
        entries.append({"word": word, "meaning": meaning})
    
    with open('dictionary.json', 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    
    print(f"Scraped {len(entries)} dictionary entries")

if __name__ == '__main__':
    scrape_dictionary()
