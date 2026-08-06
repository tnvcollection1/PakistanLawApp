import requests
import json
import os
import time
from pathlib import Path

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
DATA_DIR = Path("data")

def fetch_all(endpoint, key):
    page = 1
    all_items = []
    while True:
        r = requests.get(f"{BASE}{endpoint}", headers=HEADERS, params={"page": page}, timeout=30)
        data = r.json()
        items = data.get(key, [])
        if not items:
            break
        all_items.extend(items)
        page += 1
        if page > 50:
            break
        time.sleep(0.5)
    return all_items

def run():
    DATA_DIR.mkdir(exist_ok=True)
    endpoints = [
        ("/api/cases", "cases"),
        ("/api/statutes", "statutes"),
        ("/api/courts", "courts"),
        ("/api/judges", "judges"),
    ]
    for endpoint, key in endpoints:
        print(f"Fetching {key}...")
        items = fetch_all(endpoint, key)
        with open(DATA_DIR / f"{key}.json", "w") as f:
            json.dump(items, f, indent=2)
        print(f"  Saved {len(items)} {key}")

if __name__ == "__main__":
    run()
