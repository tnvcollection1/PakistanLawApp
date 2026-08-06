import requests, time, json, os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.pakistanlawsite.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def scrape_ihc(session, out='data/ihc_cases.json'):
    os.makedirs('data', exist_ok=True)
    results = []
    url = f"{BASE_URL}/ihc/cases"
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
        url = urljoin(BASE_URL, next_link['href']) if next_link else None
        time.sleep(1)
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved {len(results)} IHC cases to {out}")

if __name__ == '__main__':
    s = requests.Session()
    scrape_ihc(s)
