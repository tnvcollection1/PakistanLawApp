import requests
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_endpoint(endpoint):
    r = requests.get(f"{BASE}{endpoint}", headers=HEADERS, timeout=30)
    return r.json()

def run():
    endpoints = ["/api/cases", "/api/statutes", "/api/courts", "/api/judges"]
    for endpoint in endpoints:
        print(f"Fetching {endpoint}...")
        data = fetch_endpoint(endpoint)
        with open(f"data/{endpoint.replace('/', '_')}.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"  Saved")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run()
