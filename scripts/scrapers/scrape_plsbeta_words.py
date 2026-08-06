#!/usr/bin/env python3
"""Scrape legal words/phrases from PLS Beta."""

import requests
import json
import time
from pathlib import Path

BASE_URL = "https://beta.pakistanlawsite.com"
OUTPUT_DIR = Path("data/words_phrases")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://beta.pakistanlawsite.com/",
}

session = requests.Session()

def fetch_words(alphabet='A', page=1):
    url = f"{BASE_URL}/api/words?alphabet={alphabet}&page={page}"
    try:
        resp = session.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching words {alphabet} page {page}: {e}")
        return None

def scrape_all_words():
    all_words = []
    for alphabet in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        print(f"Scraping words for alphabet {alphabet}...")
        page = 1
        while True:
            data = fetch_words(alphabet, page)
            if not data:
                break
            words = data.get('words', [])
            if not words:
                break
            all_words.extend(words)
            print(f"  Page {page}: {len(words)} words")
            if not data.get('has_more', False):
                break
            page += 1
            time.sleep(0.5)
    
    output_file = OUTPUT_DIR / "all_words.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_words, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(all_words)} words to {output_file}")
    return all_words

def fetch_word_detail(word_id):
    url = f"{BASE_URL}/api/words/{word_id}"
    try:
        resp = session.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching word {word_id}: {e}")
        return None

def scrape_word_details(words):
    details = []
    for i, word in enumerate(words):
        print(f"Scraping detail {i+1}/{len(words)}: {word.get('word', '')}...")
        detail = fetch_word_detail(word['id'])
        if detail:
            details.append(detail)
        time.sleep(0.3)
    
    output_file = OUTPUT_DIR / "word_details.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(details, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(details)} word details to {output_file}")
    return details

def main():
    words = scrape_all_words()
    if words:
        scrape_word_details(words[:100])  # First 100 only

if __name__ == '__main__':
    main()
