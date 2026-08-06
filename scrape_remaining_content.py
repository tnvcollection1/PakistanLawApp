import requests, time, json, os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.pakistanlawsite.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def scrape_remaining(session, known_file='data/pls_main.json', out='data/remaining.json'):
    os.makedirs('data', exist_ok=True)
    known = []
    if os.path.exists(known_file):
        with open(known_file, 'r') as f:
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
                if title not in known_titles:
                    results.append({
                        'title': title,
                        'citation': cols[1].get_text(strip=True),
                        'date': cols[2].get_text(strip=True),
                    })
        next_link = soup.select_one('a[rel="next"]')
        url = urljoin(BASE_URL, next_link['href']) if next_link else None
        time.sleep(1)
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved {len(results)} remaining records to {out}")

if __name__ == '__main__':
    s = requests.Session()
    scrape_remaining(s)
