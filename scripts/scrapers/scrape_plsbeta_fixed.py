import requests
import json
import os
import time

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_with_retry(endpoint, retries=3):
    for i in range(retries):
        try:
            r = requests.get(f"{BASE}{endpoint}", headers=HEADERS, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(2 ** i)
    return None

def run():
    data = fetch_with_retry("/api/cases")
    with open("data/cases_fixed.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Fetched {len(data.get('cases', []))} cases")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run()
