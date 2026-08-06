import requests
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_categories():
    r = requests.get(f"{BASE}/api/categories", headers=HEADERS, timeout=30)
    return r.json()

def fetch_category_cases(cat_id):
    r = requests.get(f"{BASE}/api/categories/{cat_id}/cases", headers=HEADERS, timeout=30)
    return r.json()

def run():
    os.makedirs("data", exist_ok=True)
    categories = fetch_categories()
    with open("data/categories.json", "w") as f:
        json.dump(categories, f, indent=2)
    for cat in categories:
        cases = fetch_category_cases(cat["id"])
        with open(f"data/category_{cat['id']}.json", "w") as f:
            json.dump(cases, f, indent=2)
        print(f"Category {cat['name']}: {len(cases)} cases")

if __name__ == "__main__":
    run()
