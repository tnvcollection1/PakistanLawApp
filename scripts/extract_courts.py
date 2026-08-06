import sqlite3
import json
from pathlib import Path
import re

DB_PATH = Path(__file__).parent.parent / "instance" / "pakistan_law.db"

def extract_court_from_citation(citation):
    if not citation:
        return None
    court_patterns = {
        "Supreme Court": [r'\\bSC\\b', r'Supreme'],
        "Lahore High Court": [r'\\bLHC\\b', r'Lahore'],
        "Sindh High Court": [r'\\bSHC\\b', r'Sindh'],
        "Peshawar High Court": [r'\\bPHC\\b', r'Peshawar'],
        "Balochistan High Court": [r'\\bBHC\\b', r'Balochistan'],
        "Islamabad High Court": [r'\\bIHC\\b', r'Islamabad'],
    }
    for court, patterns in court_patterns.items():
        for pattern in patterns:
            if re.search(pattern, citation, re.IGNORECASE):
                return court
    return None

def run():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, citation FROM cases WHERE court IS NULL AND citation IS NOT NULL")
    rows = c.fetchall()
    updated = 0
    for row in rows:
        case_id, citation = row
        court = extract_court_from_citation(citation)
        if court:
            c.execute("UPDATE cases SET court = ? WHERE id = ?", (court, case_id))
            updated += 1
    conn.commit()
    conn.close()
    print(f"Updated {updated} courts")

if __name__ == "__main__":
    run()
