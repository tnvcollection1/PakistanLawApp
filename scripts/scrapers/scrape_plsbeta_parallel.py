import requests
import concurrent.futures
import os

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def fetch_page(page):
    r = requests.get(f"{BASE}/api/cases?page={page}", headers=HEADERS, timeout=30)
    return r.json()

def run():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_page, p) for p in range(1, 11)]
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                print(f"Fetched {len(data.get('cases', []))} cases")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    run()
