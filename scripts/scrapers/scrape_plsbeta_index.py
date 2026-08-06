import requests
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_index():
    r = requests.get(f"{BASE}/api/index", headers=HEADERS, timeout=30)
    return r.json()

def fetch_alphabetical_index(letter):
    r = requests.get(f"{BASE}/api/index/{letter}", headers=HEADERS, timeout=30)
    return r.json()

def run():
    os.makedirs("data", exist_ok=True)
    index = fetch_index()
    with open("data/index.json", "w") as f:
        json.dump(index, f, indent=2)
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        alpha = fetch_alphabetical_index(letter)
        with open(f"data/index_{letter}.json", "w") as f:
            json.dump(alpha, f, indent=2)
        print(f"Index {letter}: {len(alpha)} entries")

if __name__ == "__main__":
    run()
