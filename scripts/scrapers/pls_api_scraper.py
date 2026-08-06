import requests, time, json, os, sys
from urllib.parse import urljoin

BASE_URL = "https://api.pakistanlawsite.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Authorization": f"Bearer {os.getenv('PLS_API_TOKEN', '')}",
}

def scrape_api(endpoint='/cases', out='data/pls_api.json'):
    os.makedirs('data', exist_ok=True)
    results = []
    url = f"{BASE_URL}{endpoint}"
    while url:
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            print(f"[-] API error: {r.status_code}")
            break
        data = r.json()
        results.extend(data.get('results', []))
        url = data.get('next')
        time.sleep(1)
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved {len(results)} API records to {out}")

if __name__ == '__main__':
    scrape_api(sys.argv[1] if len(sys.argv) > 1 else '/cases')
