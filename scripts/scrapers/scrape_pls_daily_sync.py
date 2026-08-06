import requests
import json
import os
import time
from datetime import datetime
from pathlib import Path

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
DATA_DIR = Path("data")

def fetch_today():
    today = datetime.now().strftime("%Y-%m-%d")
    r = requests.get(f"{BASE}/api/cases/date/{today}", headers=HEADERS, timeout=30)
    return r.json()

def fetch_recent():
    r = requests.get(f"{BASE}/api/cases/recent", headers=HEADERS, timeout=30)
    return r.json()

def run():
    DATA_DIR.mkdir(exist_ok=True)
    today_cases = fetch_today()
    recent_cases = fetch_recent()
    with open(DATA_DIR / "today.json", "w") as f:
        json.dump(today_cases, f, indent=2)
    with open(DATA_DIR / "recent.json", "w") as f:
        json.dump(recent_cases, f, indent=2)
    print(f"Today: {len(today_cases)}, Recent: {len(recent_cases)}")

if __name__ == "__main__":
    run()
