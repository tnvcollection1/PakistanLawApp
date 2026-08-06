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

def scrape_advanced(session, query, out='data/plsbeta_advanced.json'):
    os.makedirs('data', exist_ok=True)
    results = []
    url = f"{BASE_URL}/beta/search?q={query}"
    while url:
        r = session.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('.search-result'):
            results.append({
                'title': item.select_one('.title').get_text(strip=True) if item.select_one('.title') else '',
                'citation': item.select_one('.citation').get_text(strip=True) if item.select_one('.citation') else '',
                'date': item.select_one('.date').get_text(strip=True) if item.select_one('.date') else '',
                'snippet': item.select_one('.snippet').get_text(strip=True) if item.select_one('.snippet') else '',
            })
        next_link = soup.select_one('a[rel="next"]')
        url = urljoin(BASE_URL, next_link['href']) if next_link else None
        time.sleep(1)
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved {len(results)} advanced results to {out}")

if __name__ == '__main__':
    s = requests.Session()
    if login(s):
        scrape_advanced(s, sys.argv[1] if len(sys.argv) > 1 else '')
    else:
        print("[-] Login failed")
        sys.exit(1)
