import requests
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_high_court_cases(court):
    r = requests.get(f"{BASE}/api/courts/{court}/cases", headers=HEADERS, timeout=30)
    return r.json()

def run():
    courts = ["supreme-court", "lahore-high-court", "sindh-high-court", "peshawar-high-court", "balochistan-high-court", "islamabad-high-court"]
    for court in courts:
        print(f"Fetching {court}...")
        cases = fetch_high_court_cases(court)
        with open(f"data/{court}.json", "w") as f:
            json.dump(cases, f, indent=2)
        print(f"  Saved {len(cases)} cases")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run()
