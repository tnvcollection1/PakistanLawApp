import subprocess
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")

def curl_fetch(endpoint):
    cmd = [
        "curl", "-s", "-H", f"Authorization: Bearer {TOKEN}",
        f"{BASE}{endpoint}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def run():
    data = curl_fetch("/api/cases")
    with open("data/cases_curl.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Fetched {len(data.get('cases', []))} cases")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run()
