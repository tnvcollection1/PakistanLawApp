import requests
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_words():
    r = requests.get(f"{BASE}/api/words", headers=HEADERS, timeout=30)
    return r.json()

def fetch_phrases():
    r = requests.get(f"{BASE}/api/phrases", headers=HEADERS, timeout=30)
    return r.json()

def run():
    words = fetch_words()
    phrases = fetch_phrases()
    with open("data/words.json", "w") as f:
        json.dump(words, f, indent=2)
    with open("data/phrases.json", "w") as f:
        json.dump(phrases, f, indent=2)
    print(f"Words: {len(words)}, Phrases: {len(phrases)}")

if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    run()
