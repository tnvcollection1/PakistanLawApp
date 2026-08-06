import requests
from bs4 import BeautifulSoup
import re
import json
import os

def scrape_words_phrases():
    url = "https://pakistanlawsite.com/words-phrases"
    resp = requests.get(url, timeout=30)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    phrases = []
    for item in soup.find_all('div', class_='phrase'):
        phrase = item.find('h3').get_text(strip=True) if item.find('h3') else ''
        meaning = item.find('p').get_text(strip=True) if item.find('p') else ''
        phrases.append({"phrase": phrase, "meaning": meaning})
    
    os.makedirs('data', exist_ok=True)
    with open('data/words_phrases.json', 'w', encoding='utf-8') as f:
        json.dump(phrases, f, ensure_ascii=False, indent=2)
    
    print(f"Scraped {len(phrases)} words and phrases")

if __name__ == '__main__':
    scrape_words_phrases()
