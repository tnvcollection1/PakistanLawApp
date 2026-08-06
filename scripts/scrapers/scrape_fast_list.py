import requests
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_list_fast():
    r = requests.get(f"{BASE}/api/cases/list", headers=HEADERS, timeout=30)
    return r.json()

def run():
    cases = fetch_list_fast()
    with open("data/fast_list.json", "w") as f:
        json.dump(cases, f, indent=2)
    print(f"Fetched {len(cases)} cases")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run()
