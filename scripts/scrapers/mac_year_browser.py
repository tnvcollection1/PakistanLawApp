import requests
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_by_year(year):
    r = requests.get(f"{BASE}/api/cases", headers=HEADERS, params={"year": year}, timeout=30)
    return r.json()

def fetch_by_mac(mac):
    r = requests.get(f"{BASE}/api/cases", headers=HEADERS, params={"mac": mac}, timeout=30)
    return r.json()

def run():
    for year in range(2020, 2024):
        cases = fetch_by_year(year)
        with open(f"data/year_{year}.json", "w") as f:
            json.dump(cases, f, indent=2)
        print(f"Year {year}: {len(cases.get('cases', []))} cases")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run()
