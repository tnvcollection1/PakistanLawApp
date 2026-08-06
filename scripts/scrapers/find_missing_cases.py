import requests
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_all_ids():
    r = requests.get(f"{BASE}/api/cases/ids", headers=HEADERS, timeout=30)
    return r.json()

def find_missing(local_ids):
    remote_ids = set(fetch_all_ids())
    local_set = set(local_ids)
    missing = remote_ids - local_set
    return list(missing)

def run():
    with open("data/local_ids.json") as f:
        local_ids = json.load(f)
    missing = find_missing(local_ids)
    with open("data/missing_ids.json", "w") as f:
        json.dump(missing, f, indent=2)
    print(f"Found {len(missing)} missing cases")

if __name__ == "__main__":
    run()
