import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import time
from pathlib import Path

BASE_URL = "https://eastlaw.pk"
DB_PATH = Path(__file__).parent.parent / "instance" / "pakistan_law.db"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, citation TEXT UNIQUE, date TEXT, court TEXT,
        content TEXT, source TEXT, url TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    return conn

def fetch_case_list(page=1):
    url = f"{BASE_URL}/cases?page={page}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    links = []
    for a in soup.select("a[href^='/case/']"):
        links.append({
            "title": a.get_text(strip=True),
            "url": BASE_URL + a["href"]
        })
    return links

def fetch_case_detail(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.select_one("h1.case-title")
    citation = soup.select_one("span.citation")
    date = soup.select_one("span.date")
    court = soup.select_one("span.court")
    content = soup.select_one("div.case-content")
    return {
        "title": title.get_text(strip=True) if title else None,
        "citation": citation.get_text(strip=True) if citation else None,
        "date": date.get_text(strip=True) if date else None,
        "court": court.get_text(strip=True) if court else None,
        "content": content.get_text("\n", strip=True) if content else None,
        "url": url
    }

def save_case(case):
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO cases (title, citation, date, court, content, source, url)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (case["title"], case["citation"], case["date"], case["court"], case["content"], "eastlaw", case["url"]))
    conn.commit()
    conn.close()

def run():
    for page in range(1, 6):
        print(f"Fetching page {page}...")
        cases = fetch_case_list(page)
        for case in cases[:10]:
            try:
                detail = fetch_case_detail(case["url"])
                save_case(detail)
                print(f"  Saved: {detail['title'][:50]}...")
            except Exception as e:
                print(f"  Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    run()
