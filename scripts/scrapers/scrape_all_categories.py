import requests
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

CATEGORIES = ["criminal", "civil", "constitutional", "family", "corporate", "tax", "property"]

def scrape_category(category):
    page = 1
    all_cases = []
    while True:
        r = requests.get(f"{BASE}/api/cases", headers=HEADERS, params={"category": category, "page": page}, timeout=30)
        data = r.json()
        cases = data.get("cases", [])
        if not cases:
            break
        all_cases.extend(cases)
        page += 1
        if page > 10:
            break
    return all_cases

def run():
    for cat in CATEGORIES:
        print(f"Scraping {cat}...")
        cases = scrape_category(cat)
        with open(f"data/{cat}_cases.json", "w") as f:
            json.dump(cases, f, indent=2)
        print(f"  Saved {len(cases)} cases")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run()
