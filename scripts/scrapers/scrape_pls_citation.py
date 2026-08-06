import requests
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_by_citation(citation):
    r = requests.get(f"{BASE}/api/cases", headers=HEADERS, params={"citation": citation}, timeout=30)
    return r.json()

def run():
    citations = ["2023 SCMR 1", "PLD 2023 SC 1", "2022 YLR 100"]
    for citation in citations:
        result = fetch_by_citation(citation)
        with open(f"data/citation_{citation.replace(' ', '_')}.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"Citation {citation}: {len(result.get('cases', []))} results")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run()
