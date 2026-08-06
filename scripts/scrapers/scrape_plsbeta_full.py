import requests
import json
import os
import time

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_all_cases():
    page = 1
    all_cases = []
    while True:
        r = requests.get(f"{BASE}/api/cases", headers=HEADERS, params={"page": page, "per_page": 100}, timeout=30)
        data = r.json()
        cases = data.get("cases", [])
        if not cases:
            break
        all_cases.extend(cases)
        page += 1
        if page > 100:
            break
        time.sleep(0.5)
    return all_cases

def run():
    cases = fetch_all_cases()
    with open("data/all_cases_full.json", "w") as f:
        json.dump(cases, f, indent=2)
    print(f"Fetched {len(cases)} cases")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run()
