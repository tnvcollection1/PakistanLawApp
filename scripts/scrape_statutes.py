import requests, json, os, re, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.pakistanlawsite.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def scrape_statute(session, statute_url, out_dir='data/statutes'):
    os.makedirs(out_dir, exist_ok=True)
    r = session.get(statute_url, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    content = soup.select_one('.statute-content')
    if not content:
        return None
    text = content.get_text(separator='\n', strip=True)
    statute_id = statute_url.split('/')[-1]
    with open(f"{out_dir}/{statute_id}.txt", 'w', encoding='utf-8') as f:
        f.write(text)
    return text

def scrape_all_statutes(session, out='data/statutes.json'):
    results = []
    url = f"{BASE_URL}/statutes"
    while url:
        r = session.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        for link in soup.select('a[href^="/statute/"]'):
            statute_url = urljoin(BASE_URL, link['href'])
            text = scrape_statute(session, statute_url)
            if text:
                results.append({'url': statute_url, 'content': text[:3000]})
            time.sleep(0.5)
        next_link = soup.select_one('a[rel="next"]')
        url = urljoin(BASE_URL, next_link['href']) if next_link else None
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved {len(results)} statutes to {out}")

if __name__ == '__main__':
    s = requests.Session()
    scrape_all_statutes(s)
