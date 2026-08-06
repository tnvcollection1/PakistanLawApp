import asyncio
from playwright.async_api import async_playwright
import sqlite3
from pathlib import Path

BASE_URL = "https://ihc.gov.pk"
DB_PATH = Path(__file__).parent.parent / "instance" / "pakistan_law.db"

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

async def scrape_ihc():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"{BASE_URL}/judgments")
        links = await page.query_selector_all("a[href*='judgment']")
        cases = []
        for link in links[:20]:
            href = await link.get_attribute("href")
            title = await link.inner_text()
            cases.append({"title": title.strip(), "url": BASE_URL + href if href.startswith("/") else href})
        await browser.close()
        return cases

async def ingest():
    conn = get_db()
    c = conn.cursor()
    cases = await scrape_ihc()
    for case in cases:
        c.execute('''INSERT OR IGNORE INTO cases (title, citation, date, court, content, source, url)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (case["title"], None, None, "Islamabad High Court", None, "ihc", case["url"]))
    conn.commit()
    conn.close()
    print(f"Ingested {len(cases)} cases")

def run():
    asyncio.run(ingest())

if __name__ == "__main__":
    run()
