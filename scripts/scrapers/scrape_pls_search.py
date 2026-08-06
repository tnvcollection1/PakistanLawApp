import requests
import json
import os
import time

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def search_cases(query, filters=None):
    params = {"q": query, "limit": 100}
    if filters:
        params.update(filters)
    r = requests.get(f"{BASE}/api/cases/search", headers=HEADERS, params=params, timeout=30)
    return r.json()

def run():
    queries = ["murder", "contract", "constitutional", "property", "divorce"]
    for q in queries:
        print(f"Searching: {q}")
        results = search_cases(q)
        with open(f"data/search_{q}.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"  Results: {len(results.get('cases', []))}")
        time.sleep(1)

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run()
