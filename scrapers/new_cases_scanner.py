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

def scan_new_cases(session, known_cases='data/known_cases.json', out='data/new_cases.json'):
    os.makedirs('data', exist_ok=True)
    known = []
    if os.path.exists(known_cases):
        with open(known_cases, 'r') as f:
            known = json.load(f)
    known_titles = set(k['title'] for k in known)
    results = []
    url = f"{BASE_URL}/cases"
    while url:
        r = session.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        for row in soup.select('table tbody tr'):
            cols = row.find_all('td')
            if len(cols) >= 3:
                title = cols[0].get_text(strip=True)
                citation = cols[1].get_text(strip=True)
                date = cols[2].get_text(strip=True)
                is_new = title not in known_titles
                results.append({
                    'title': title,
                    'citation': citation,
                    'date': date,
                    'is_new': is_new,
                })
                if is_new:
                    known.append({'title': title, 'citation': citation, 'date': date})
        next_link = soup.select_one('a[rel="next"]')
        url = urljoin(BASE_URL, next_link['href']) if next_link else None
        time.sleep(1)
    with open(known_cases, 'w') as f:
        json.dump(known, f, indent=2)
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    new_count = sum(1 for r in results if r['is_new'])
    print(f"[+] Found {new_count} new cases out of {len(results)} total")

if __name__ == '__main__':
    s = requests.Session()
    if login(s):
        scan_new_cases(s)
    else:
        print("[-] Login failed")
        sys.exit(1)
