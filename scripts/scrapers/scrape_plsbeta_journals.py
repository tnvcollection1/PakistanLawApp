import requests
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_journals():
    r = requests.get(f"{BASE}/api/journals", headers=HEADERS, timeout=30)
    return r.json()

def fetch_journal_articles(journal_id):
    r = requests.get(f"{BASE}/api/journals/{journal_id}/articles", headers=HEADERS, timeout=30)
    return r.json()

def run():
    os.makedirs("data", exist_ok=True)
    journals = fetch_journals()
    with open("data/journals.json", "w") as f:
        json.dump(journals, f, indent=2)
    for journal in journals:
        articles = fetch_journal_articles(journal["id"])
        with open(f"data/journal_{journal['id']}.json", "w") as f:
            json.dump(articles, f, indent=2)
        print(f"Journal {journal['name']}: {len(articles)} articles")

if __name__ == "__main__":
    run()
