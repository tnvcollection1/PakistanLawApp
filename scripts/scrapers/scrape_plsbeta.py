import requests, time, json, sys, os
from bs4 import BeautifulSoup

BASE_URL = "https://www.pakistanlawsite.com"
LOGIN_URL = f"{BASE_URL}/login"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def login(session):
    print("[+] Logging in...")
    r = session.get(LOGIN_URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    token = soup.find('input', {'name': '_token'})
    if not token:
        print("[-] Could not find CSRF token")
        return False
    data = {
        '_token': token['value'],
        'email': os.getenv('PLS_EMAIL', 'user@example.com'),
        'password': os.getenv('PLS_PASSWORD', 'password'),
        'remember': 'on',
    }
    r = session.post(LOGIN_URL, data=data, headers=HEADERS)
    return r.status_code == 200 or 'dashboard' in r.url

def scrape_beta(session, out='data/plsbeta.json'):
    os.makedirs('data', exist_ok=True)
    results = []
    url = f"{BASE_URL}/beta/cases"
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
                })
        next_link = soup.select_one('a[rel="next"]')
        url = next_link['href'] if next_link else None
        time.sleep(1)
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved {len(results)} records to {out}")

if __name__ == '__main__':
    s = requests.Session()
    if login(s):
        scrape_beta(s)
    else:
        print("[-] Login failed")
        sys.exit(1)
