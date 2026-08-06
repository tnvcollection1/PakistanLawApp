import requests, time, json, sys, os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.pakistanlawsite.com"
LOGIN_URL = f"{BASE_URL}/login"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def login(session):
    print("[+] Logging in to PLS...")
    r = session.get(LOGIN_URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    token = soup.find('input', {'name': '_token'})
    if not token:
        print("[-] No CSRF token found")
        return False
    data = {
        '_token': token['value'],
        'email': os.getenv('PLS_EMAIL'),
        'password': os.getenv('PLS_PASSWORD'),
        'remember': 'on',
    }
    r = session.post(LOGIN_URL, data=data, headers=HEADERS)
    return r.status_code == 200 or 'dashboard' in r.url

def scrape_full_content(session, case_url, out_dir='data/cases'):
    os.makedirs(out_dir, exist_ok=True)
    r = session.get(case_url, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    content = soup.select_one('.case-content')
    if not content:
        return None
    text = content.get_text(separator='\n', strip=True)
    case_id = case_url.split('/')[-1]
    with open(f"{out_dir}/{case_id}.txt", 'w', encoding='utf-8') as f:
        f.write(text)
    return text

def scrape_all_cases(session, start=1, end=500, out='data/pls_full_content.json'):
    results = []
    for i in range(start, end+1):
        url = f"{BASE_URL}/case/{i}"
        text = scrape_full_content(session, url)
        if text:
            results.append({'id': i, 'content': text[:5000]})
        time.sleep(0.5)
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved {len(results)} cases to {out}")

if __name__ == '__main__':
    s = requests.Session()
    if login(s):
        scrape_all_cases(s)
    else:
        print("[-] Login failed")
        sys.exit(1)
