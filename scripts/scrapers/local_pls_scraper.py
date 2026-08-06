import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "instance" / "pakistan_law.db"

def run():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, citation, content FROM cases WHERE content IS NOT NULL LIMIT 10")
    rows = cur.fetchall()
    for row in rows:
        case_id, title, citation, content = row
        print(f"Case {case_id}: {title} ({citation})")
        print(content[:500])
        print("---")
    conn.close()

if __name__ == "__main__":
    run()
