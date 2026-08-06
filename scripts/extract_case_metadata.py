import sqlite3
import json
from pathlib import Path
import re

DB_PATH = Path(__file__).parent.parent / "instance" / "pakistan_law.db"

def extract_year(citation):
    match = re.search(r'\b(\d{4})\b', citation or "")
    return int(match.group(1)) if match else None

def extract_court(citation):
    if "SC" in (citation or ""):
        return "Supreme Court"
    if "HC" in (citation or ""):
        return "High Court"
    return "Unknown"

def run():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, citation, title, content FROM cases WHERE citation IS NOT NULL")
    rows = c.fetchall()
    metadata = []
    for row in rows:
        case_id, citation, title, content = row
        year = extract_year(citation)
        court = extract_court(citation)
        metadata.append({
            "id": case_id,
            "citation": citation,
            "title": title,
            "year": year,
            "court": court,
            "content_length": len(content) if content else 0
        })
    with open("data/case_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Extracted metadata for {len(metadata)} cases")
    conn.close()

if __name__ == "__main__":
    run()
