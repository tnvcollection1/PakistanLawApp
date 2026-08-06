import requests
import json
import os
import time
from pathlib import Path

BASE = "https://plsbeta.com"
TOKEN = os.getenv("PLSBETA_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
DATA_DIR = Path("data")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_case_content(case_id):
    r = requests.get(f"{BASE}/api/cases/{case_id}/content", headers=HEADERS, timeout=30)
    if r.status_code == 200:
        return r.json()
    return None

def run():
    DATA_DIR.mkdir(exist_ok=True)
    with open(DATA_DIR / "case_ids.json") as f:
        case_ids = json.load(f)
    for case_id in case_ids:
        content = fetch_case_content(case_id)
        if content:
            with open(DATA_DIR / f"case_{case_id}.json", "w") as f:
                json.dump(content, f, indent=2)
            logger.info(f"Saved case {case_id}")
        time.sleep(0.5)

if __name__ == "__main__":
    import logging
    run()
