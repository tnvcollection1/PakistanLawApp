import requests
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_maxims():
    r = requests.get(f"{BASE}/api/maxims", headers=HEADERS, timeout=30)
    return r.json()

def fetch_maxim_detail(maxim_id):
    r = requests.get(f"{BASE}/api/maxims/{maxim_id}", headers=HEADERS, timeout=30)
    return r.json()

def run():
    os.makedirs("data", exist_ok=True)
    maxims = fetch_maxims()
    with open("data/maxims.json", "w") as f:
        json.dump(maxims, f, indent=2)
    for maxim in maxims[:10]:
        detail = fetch_maxim_detail(maxim["id"])
        with open(f"data/maxim_{maxim['id']}.json", "w") as f:
            json.dump(detail, f, indent=2)
    print(f"Maxims: {len(maxims)}")

if __name__ == "__main__":
    run()
