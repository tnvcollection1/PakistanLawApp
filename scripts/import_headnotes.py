import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "instance" / "pakistan_law.db"

def import_headnotes(headnotes_file):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    with open(headnotes_file, 'r') as f:
        for line in f:
            case_id, headnote = line.strip().split("\t", 1)
            c.execute("UPDATE cases SET headnote = ? WHERE id = ?", (headnote, case_id))
    conn.commit()
    conn.close()
    print("Headnotes imported")

def run():
    import_headnotes("data/headnotes.tsv")

if __name__ == "__main__":
    run()
