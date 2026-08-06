import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "instance" / "pakistan_law.db"

def batch_update_headnotes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, content FROM cases WHERE headnote IS NULL AND content IS NOT NULL LIMIT 100")
    rows = c.fetchall()
    updated = 0
    for row in rows:
        case_id, content = row
        # Extract first paragraph as headnote
        paragraphs = content.split("\n\n")
        headnote = paragraphs[0][:500] if paragraphs else ""
        c.execute("UPDATE cases SET headnote = ? WHERE id = ?", (headnote, case_id))
        updated += 1
    conn.commit()
    conn.close()
    print(f"Updated {updated} headnotes")

if __name__ == "__main__":
    batch_update_headnotes()
