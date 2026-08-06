import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from pathlib import Path

BASE_URL = "https://eastlaw.pk"
DB_PATH = Path(__file__).parent.parent / "instance" / "pakistan_law.db"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def save_case(title, citation, date, court, content, url):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, citation TEXT UNIQUE, date TEXT, court TEXT,
        content TEXT, source TEXT, url TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''INSERT OR IGNORE INTO cases (title, citation, date, court, content, source, url)
        VALUES (?, ?, ?, ?, ?, ?, ?)''', (title, citation, date, court, content, "eastlaw", url))
    conn.commit()
    conn.close()

def scrape_with_retry(url, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            return r.text
        except Exception as e:
            if i == retries - 1:
                raise e
            time.sleep(2 ** i)
    return None

def run():
    for page in range(1, 11):
        html = scrape_with_retry(f"{BASE_URL}/cases?page={page}")
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.select("a[href^='/case/']"):
            case_url = BASE_URL + link["href"]
            case_html = scrape_with_retry(case_url)
            case_soup = BeautifulSoup(case_html, "html.parser")
            title = case_soup.select_one("h1.case-title")
            citation = case_soup.select_one("span.citation")
            date = case_soup.select_one("span.date")
            court = case_soup.select_one("span.court")
            content = case_soup.select_one("div.case-content")
            save_case(
                title.get_text(strip=True) if title else None,
                citation.get_text(strip=True) if citation else None,
                date.get_text(strip=True) if date else None,
                court.get_text(strip=True) if court else None,
                content.get_text("\n", strip=True) if content else None,
                case_url
            )
        time.sleep(1)

if __name__ == "__main__":
    run()
