import requests
import sqlite3
from pathlib import Path

BASE_URL = "https://ihc.gov.pk/api"
DB_PATH = Path(__file__).parent.parent / "instance" / "pakistan_law.db"
HEADERS = {"User-Agent": "Mozilla/5.0"}

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

def fetch_judgments():
    r = requests.get(f"{BASE_URL}/judgments", headers=HEADERS, timeout=30)
    return r.json()

def ingest():
    conn = get_db()
    c = conn.cursor()
    judgments = fetch_judgments()
    for j in judgments:
        c.execute('''INSERT OR IGNORE INTO cases (title, citation, date, court, content, source, url)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (j.get("title"), j.get("citation"), j.get("date"), "Islamabad High Court",
             j.get("content"), "ihc_api", j.get("url")))
    conn.commit()
    conn.close()
    print(f"Ingested {len(judgments)} judgments")

def run():
    ingest()

if __name__ == "__main__":
    run()
