import requests
import json
import os
from pathlib import Path

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
DATA_DIR = Path("data")

def fetch_case(case_id):
    r = requests.get(f"{BASE}/api/cases/{case_id}", headers=HEADERS, timeout=30)
    return r.json()

def fetch_case_content(case_id):
    r = requests.get(f"{BASE}/api/cases/{case_id}/content", headers=HEADERS, timeout=30)
    return r.json()

def run():
    DATA_DIR.mkdir(exist_ok=True)
    case_ids = [1, 2, 3, 4, 5]  # Example IDs
    for case_id in case_ids:
        case = fetch_case(case_id)
        content = fetch_case_content(case_id)
        with open(DATA_DIR / f"case_{case_id}.json", "w") as f:
            json.dump({"meta": case, "content": content}, f, indent=2)
        print(f"Fetched case {case_id}")

if __name__ == "__main__":
    run()
