#!/usr/bin/env python3
"""
EastLaw.pk Full Case Scraper (curl-based)
Uses curl subprocess to avoid Python requests CDN issues.
"""

import subprocess
import json
import time
import os
import sys
from datetime import datetime

# === CONFIG ===
EMAIL = "tnvcollection1@gmail.com"
PASSWORD = "Sunny123!"
BASE_URL = "https://www.eastlaw.pk/api"
OUTPUT_DIR = "/root/eastlaw_data"
BATCH_SIZE = 500
PAGE_SIZE = 100
DETAIL_DELAY = 0.2
LIST_DELAY = 0.5
MAX_RETRIES = 3

jwt_token = None
token_time = 0


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def curl_get(url, params=None):
    """Make GET request using curl."""
    global jwt_token
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"
    cmd = [
        "curl", "-s", "--connect-timeout", "15", "--max-time", "90",
        "-H", f"Cookie: jwt={jwt_token}",
        "-H", f"Authorization: Bearer {jwt_token}",
        "-H", "Accept: application/json",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/146.0.0.0",
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode == 0 and result.stdout:
        return json.loads(result.stdout)
    return None


def curl_post(url, data):
    """Make POST request using curl."""
    global jwt_token
    cmd = [
        "curl", "-s", "--connect-timeout", "15", "--max-time", "60",
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-H", "Accept: application/json",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/146.0.0.0",
        "-d", json.dumps(data),
        url
    ]
    if jwt_token:
        cmd.extend(["-H", f"Cookie: jwt={jwt_token}", "-H", f"Authorization: Bearer {jwt_token}"])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if result.returncode == 0 and result.stdout:
        return json.loads(result.stdout)
    return None


def login():
    global jwt_token, token_time
    log("Logging in...")
    data = curl_post(f"{BASE_URL}/auth/signin", {"email": EMAIL, "password": PASSWORD})
    if data and data.get("token"):
        jwt_token = data["token"]
        token_time = time.time()
        log(f"Login OK - verified: {data['user'].get('emailVerified')}")
        return True
    log(f"Login FAILED: {data}")
    return False


def ensure_token():
    if time.time() - token_time > 18000:
        login()


def get_case_list(page_no):
    ensure_token()
    for attempt in range(MAX_RETRIES):
        try:
            data = curl_get(f"{BASE_URL}/case-search/advance-search",
                          {"pageNo": str(page_no), "pageSize": str(PAGE_SIZE)})
            if data and "data" in data:
                return data
            if data and data.get("statusCode") == 429:
                wait = 60 * (attempt + 1)
                log(f"Rate limited page {page_no}. Waiting {wait}s...")
                time.sleep(wait)
            else:
                log(f"List page {page_no} bad response: {str(data)[:200]}")
                time.sleep(5)
        except Exception as e:
            log(f"List page {page_no} error: {e}")
            time.sleep(10)
    return None


def get_case_detail(case_id):
    ensure_token()
    for attempt in range(MAX_RETRIES):
        try:
            data = curl_get(f"{BASE_URL}/case-search/search-by-id/{case_id}")
            if data and data.get("id"):
                return data
            if data and data.get("statusCode") == 429:
                wait = 30 * (attempt + 1)
                log(f"Rate limited case {case_id}. Waiting {wait}s...")
                time.sleep(wait)
            elif data and data.get("statusCode") == 401:
                login()
            else:
                time.sleep(2)
        except Exception as e:
            log(f"Case {case_id} error: {e}")
            time.sleep(5)
    return None


def save_batch(cases, batch_num):
    filename = os.path.join(OUTPUT_DIR, f"eastlaw_batch_{batch_num:05d}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False)
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    log(f"Saved batch {batch_num}: {len(cases)} cases ({size_mb:.1f} MB)")


def save_progress(stats):
    with open(os.path.join(OUTPUT_DIR, "progress.json"), 'w') as f:
        json.dump(stats, f, indent=2, default=str)


def get_existing_ids():
    ids = set()
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if f.startswith("eastlaw_batch_") and f.endswith(".json"):
            try:
                with open(os.path.join(OUTPUT_DIR, f)) as fp:
                    for c in json.load(fp):
                        cid = c.get("id", "")
                        if cid:
                            ids.add(cid)
            except:
                pass
    return ids


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not login():
        sys.exit(1)

    existing_ids = get_existing_ids()
    if existing_ids:
        log(f"Resuming: {len(existing_ids)} already scraped")

    first_page = get_case_list(1)
    if not first_page:
        log("Failed to get first page!")
        sys.exit(1)

    total = first_page.get("totalRecords", 0)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    log(f"Total: {total:,} cases | {total_pages:,} pages")

    batch_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("eastlaw_batch_")]
    batch_num = len(batch_files) + 1
    current_batch = []
    fetched = 0
    errors = 0
    skipped = len(existing_ids)
    start = time.time()

    for page_no in range(1, total_pages + 1):
        page_data = get_case_list(page_no) if page_no > 1 else first_page

        if not page_data or not page_data.get("data"):
            log(f"Empty page {page_no}")
            errors += 1
            continue

        for case_meta in page_data["data"]:
            oid = case_meta.get("_id", {})
            case_id = oid.get("$oid", "") if isinstance(oid, dict) else str(oid)
            if not case_id:
                continue

            if case_id in existing_ids:
                continue

            detail = get_case_detail(case_id)
            if detail:
                current_batch.append(detail)
                fetched += 1
                existing_ids.add(case_id)
            else:
                errors += 1

            time.sleep(DETAIL_DELAY)

            if len(current_batch) >= BATCH_SIZE:
                save_batch(current_batch, batch_num)
                batch_num += 1
                current_batch = []

        # Log progress
        elapsed = time.time() - start
        rate = fetched / max(elapsed, 1) * 3600
        log(f"Page {page_no}/{total_pages} | fetched: {fetched:,} | errors: {errors} | "
            f"skipped: {skipped} | rate: {rate:.0f}/hr | "
            f"ETA: {(total - fetched - skipped) / max(rate, 1):.1f}h")

        save_progress({
            "page": page_no, "total_pages": total_pages,
            "fetched": fetched, "errors": errors, "skipped": skipped,
            "rate_per_hour": round(rate), "total": total
        })
        time.sleep(LIST_DELAY)

    if current_batch:
        save_batch(current_batch, batch_num)

    log(f"COMPLETE! Fetched: {fetched:,} | Errors: {errors} | Total time: {(time.time()-start)/3600:.1f}h")


if __name__ == "__main__":
    main()
