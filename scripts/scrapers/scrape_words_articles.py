import requests
import json
import os
import time

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_words():
    r = requests.get(f"{BASE}/api/words", headers=HEADERS, timeout=30)
    return r.json()

def fetch_articles():
    r = requests.get(f"{BASE}/api/articles", headers=HEADERS, timeout=30)
    return r.json()

def fetch_word_detail(word_id):
    r = requests.get(f"{BASE}/api/words/{word_id}", headers=HEADERS, timeout=30)
    return r.json()

def run():
    os.makedirs("data", exist_ok=True)
    words = fetch_words()
    articles = fetch_articles()
    with open("data/words.json", "w") as f:
        json.dump(words, f, indent=2)
    with open("data/articles.json", "w") as f:
        json.dump(articles, f, indent=2)
    for word in words[:10]:
        detail = fetch_word_detail(word["id"])
        with open(f"data/word_{word['id']}.json", "w") as f:
            json.dump(detail, f, indent=2)
        time.sleep(0.5)
    print(f"Words: {len(words)}, Articles: {len(articles)}")

if __name__ == "__main__":
    run()
