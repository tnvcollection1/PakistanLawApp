import requests
import json
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_news():
    r = requests.get(f"{BASE}/api/news", headers=HEADERS, timeout=30)
    return r.json()

def fetch_latest():
    r = requests.get(f"{BASE}/api/cases/latest", headers=HEADERS, timeout=30)
    return r.json()

def run():
    news = fetch_news()
    latest = fetch_latest()
    with open("data/news.json", "w") as f:
        json.dump(news, f, indent=2)
    with open("data/latest.json", "w") as f:
        json.dump(latest, f, indent=2)
    print(f"News: {len(news)}, Latest: {len(latest)}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run()
