import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from pathlib import Path

BASE_URL = "https://shc.gov.pk"
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

def scrape_shc():
    url = f"{BASE_URL}/judgments"
    r = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    cases = []
    for link in soup.select("a[href*='judgment']"):
        cases.append({
            "title": link.get_text(strip=True),
            "url": BASE_URL + link["href"] if link["href"].startswith("/") else link["href"]
        })
    return cases

def ingest():
    conn = get_db()
    c = conn.cursor()
    cases = scrape_shc()
    for case in cases[:20]:
        try:
            r = requests.get(case["url"], headers=HEADERS, timeout=30)
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.select_one("h1, .title")
            content = soup.select_one(".content, .judgment-content")
            c.execute('''INSERT OR IGNORE INTO cases (title, citation, date, court, content, source, url)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (title.get_text(strip=True) if title else case["title"],
                 None, None, "Sindh High Court",
                 content.get_text("\n", strip=True) if content else None,
                 "shc", case["url"]))
            conn.commit()
            print(f"Ingested: {case['title'][:60]}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)
    conn.close()

def run():
    ingest()

if __name__ == "__main__":
    run()
