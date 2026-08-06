import requests, time, json, os, sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.pakistanlawsite.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def login(session):
    r = session.get(f"{BASE_URL}/login", headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    token = soup.find('input', {'name': '_token'})
    if not token:
        return False
    data = {
        '_token': token['value'],
        'email': os.getenv('PLS_EMAIL'),
        'password': os.getenv('PLS_PASSWORD'),
    }
    r = session.post(f"{BASE_URL}/login", data=data, headers=HEADERS)
    return r.status_code == 200 or 'dashboard' in r.url

def mac_dual_scrape(session, out='data/mac_dual.json'):
    os.makedirs('data', exist_ok=True)
    results = []
    # Scrape both Mac and regular cases
    for mac in [True, False]:
        url = f"{BASE_URL}/{'mac' if mac else ''}/cases"
        while url:
            r = session.get(url, headers=HEADERS)
            soup = BeautifulSoup(r.text, 'html.parser')
            for row in soup.select('table tbody tr'):
                cols = row.find_all('td')
                if len(cols) >= 3:
                    results.append({
                        'title': cols[0].get_text(strip=True),
                        'citation': cols[1].get_text(strip=True),
                        'date': cols[2].get_text(strip=True),
                        'mac': mac,
                    })
            next_link = soup.select_one('a[rel="next"]')
            url = urljoin(BASE_URL, next_link['href']) if next_link else None
            time.sleep(1)
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved {len(results)} dual records to {out}")

if __name__ == '__main__':
    s = requests.Session()
    if login(s):
        mac_dual_scrape(s)
    else:
        print("[-] Login failed")
        sys.exit(1)
