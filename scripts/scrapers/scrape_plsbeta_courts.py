import requests
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_courts():
    r = requests.get(f"{BASE}/api/courts", headers=HEADERS, timeout=30)
    return r.json()

def fetch_court_cases(court_id):
    r = requests.get(f"{BASE}/api/courts/{court_id}/cases", headers=HEADERS, timeout=30)
    return r.json()

def run():
    courts = fetch_courts()
    for court in courts:
        cases = fetch_court_cases(court["id"])
        with open(f"data/court_{court['id']}.json", "w") as f:
            json.dump(cases, f, indent=2)
        print(f"Court {court['name']}: {len(cases)} cases")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run()
