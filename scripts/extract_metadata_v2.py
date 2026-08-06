import sqlite3
import json
from pathlib import Path
import re
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "instance" / "pakistan_law.db"

def extract_year(citation):
    match = re.search(r'\b(\d{4})\b', citation or "")
    return int(match.group(1)) if match else None

def extract_court(citation):
    patterns = {
        "Supreme Court": [r'\bSC\b', r'Supreme'],
        "Lahore High Court": [r'\bLHC\b', r'Lahore'],
        "Sindh High Court": [r'\bSHC\b', r'Sindh'],
        "Peshawar High Court": [r'\bPHC\b', r'Peshawar'],
        "Balochistan High Court": [r'\bBHC\b', r'Balochistan'],
        "Islamabad High Court": [r'\bIHC\b', r'Islamabad'],
    }
    for court, pats in patterns.items():
        for pat in pats:
            if re.search(pat, citation or "", re.IGNORECASE):
                return court
    return None

def extract_topic(content):
    if not content:
        return None
    first = content[:500]
    topics = ["murder", "theft", "fraud", "contract", "property", "divorce", "custody", "bail", "constitutional"]
    found = [t for t in topics if t.lower() in first.lower()]
    return found[0] if found else None

def run():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, citation, title, content, date FROM cases WHERE citation IS NOT NULL")
    rows = c.fetchall()
    metadata = []
    for row in rows:
        case_id, citation, title, content, date = row
        year = extract_year(citation)
        court = extract_court(citation)
        topic = extract_topic(content)
        metadata.append({
            "id": case_id,
            "citation": citation,
            "title": title,
            "year": year,
            "court": court,
            "topic": topic,
            "date": date,
            "content_length": len(content) if content else 0
        })
    with open("data/case_metadata_v2.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Extracted metadata for {len(metadata)} cases")
    conn.close()

if __name__ == "__main__":
    run()
