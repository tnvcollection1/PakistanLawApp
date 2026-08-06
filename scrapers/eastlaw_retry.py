import requests, time, json, os, sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://eastlaw.pk"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def eastlaw_retry(url, retries=3, out='data/eastlaw_retry.json'):
    os.makedirs('data', exist_ok=True)
    results = []
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            for row in soup.select('table tbody tr'):
                cols = row.find_all('td')
                if len(cols) >= 3:
                    results.append({
                        'title': cols[0].get_text(strip=True),
                        'citation': cols[1].get_text(strip=True),
                        'date': cols[2].get_text(strip=True),
                    })
            break
        except Exception as e:
            print(f"[-] Attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved {len(results)} records from Eastlaw to {out}")

if __name__ == '__main__':
    eastlaw_retry(sys.argv[1] if len(sys.argv) > 1 else f"{BASE_URL}/cases")
