import sqlite3
from pathlib import Path
import re

DB_PATH = Path(__file__).parent.parent / "instance" / "pakistan_law.db"

def extract_headnote(content):
    if not content:
        return None
    # Look for patterns like "HEADNOTE:", "HELD:", or first paragraph
    patterns = [
        r'HEADNOTE[S]?[:\s]*(.+?)(?=\n\n|\Z)',
        r'HELD[:\s]*(.+?)(?=\n\n|\Z)',
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    # Fallback to first paragraph
    paragraphs = content.split("\n\n")
    return paragraphs[0][:500] if paragraphs else None

def run():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, content FROM cases WHERE headnote IS NULL AND content IS NOT NULL")
    rows = c.fetchall()
    updated = 0
    for row in rows:
        case_id, content = row
        headnote = extract_headnote(content)
        if headnote:
            c.execute("UPDATE cases SET headnote = ? WHERE id = ?", (headnote, case_id))
            updated += 1
    conn.commit()
    conn.close()
    print(f"Updated {updated} headnotes")

if __name__ == "__main__":
    run()
