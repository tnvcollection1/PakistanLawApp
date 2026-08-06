import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://eastlaw.pk"
DB_PATH = Path(__file__).parent.parent / "instance" / "pakistan_law.db"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_links(page=1):
    url = f"{BASE_URL}/cases?page={page}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    return [BASE_URL + a["href"] for a in soup.select("a[href^='/case/']")]

def parse_case(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    return {
        "title": soup.select_one("h1.case-title"),
        "citation": soup.select_one("span.citation"),
        "date": soup.select_one("span.date"),
        "court": soup.select_one("span.court"),
        "content": soup.select_one("div.case-content"),
        "url": url
    }

def save_case(case):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, citation TEXT UNIQUE, date TEXT, court TEXT,
        content TEXT, source TEXT, url TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''INSERT OR IGNORE INTO cases (title, citation, date, court, content, source, url)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (case["title"], case["citation"], case["date"], case["court"], case["content"], "eastlaw", case["url"]))
    conn.commit()
    conn.close()

def run():
    links = get_links(1)
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(parse_case, url) for url in links[:20]]
        for future in futures:
            case = future.result()
            if case:
                save_case(case)
    print("Done")

if __name__ == "__main__":
    run()
