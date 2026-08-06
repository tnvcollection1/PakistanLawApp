#!/usr/bin/env python3
"""
EastLaw Retry Script - Recovers failed cases from the main spider run.

The spider completed but had 155,912 errors due to:
- Cloudflare rate limits (429)
- Connection timeouts
- 403 forbidden responses

This script:
1. Identifies all discovered IDs that weren't successfully fetched
2. Retries them with exponential backoff and longer delays
3. Uses multiple strategies to bypass rate limits
4. Stores successfully fetched cases for ingestion

Run after the main spider completes.
"""

import subprocess
import json
import time
import os
import sys
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# === CONFIG ===
EMAIL = "tnvcollection1@gmail.com"
PASSWORD = "Sunny123!"
BASE_URL = "https://www.eastlaw.pk/api"

# Retry-specific settings
OUTPUT_DIR = "/tmp/eastlaw_retry"
BATCH_SIZE = 200
CONCURRENT = 3  # Lower concurrency for retries
BASE_DELAY = 2.0  # Higher base delay
MAX_RETRIES = 5
BACKOFF_MULTIPLIER = 2
JITTER = 1.5  # Random jitter range

# MongoDB connection
MONGO_URI = "mongodb://lawapp:VpsMongo2026LawXk9@localhost:27017/pakistanlawsite?authSource=pakistanlawsite"

jwt_token = None
token_time = 0
retry_count = {}
fetched_ids = set()
failed_ids = set()


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def curl_json(url, method="GET", data=None, timeout=60):
    """Make a curl request with retry-friendly settings."""
    cmd = [
        "curl", "-s",
        "--connect-timeout", "20",
        "--max-time", str(timeout),
        "-H", "Accept: application/json",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    ]
    
    if method == "POST":
        cmd.extend(["-X", "POST"])
    if data:
        cmd.extend(["-H", "Content-Type: application/json", "-d", json.dumps(data)])
    if jwt_token:
        cmd.extend([
            "-H", f"Cookie: jwt={jwt_token}",
            "-H", f"Authorization: Bearer {jwt_token}"
        ])
    
    cmd.append(url)
    
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
    except Exception as e:
        pass
    return None


def login():
    """Authenticate with EastLaw."""
    global jwt_token, token_time
    log("Logging in to EastLaw...")
    
    data = curl_json(f"{BASE_URL}/auth/signin", "POST", {
        "email": EMAIL,
        "password": PASSWORD
    })
    
    if data and data.get("token"):
        jwt_token = data["token"]
        token_time = time.time()
        log("Login successful")
        return True
    
    log("Login FAILED")
    return False


def ensure_token():
    """Refresh token if expired."""
    global jwt_token, token_time
    # Refresh every 5 hours (token likely expires in 6-12h)
    if time.time() - token_time > 18000:
        login()


def get_delay_for_id(case_id):
    """Calculate delay based on retry count with exponential backoff."""
    retries = retry_count.get(case_id, 0)
    delay = BASE_DELAY * (BACKOFF_MULTIPLIER ** retries)
    jitter = random.uniform(0, JITTER)
    return min(delay + jitter, 60)  # Cap at 60 seconds


def fetch_case_with_retry(case_id):
    """Fetch a case with exponential backoff."""
    ensure_token()
    
    retries = retry_count.get(case_id, 0)
    if retries >= MAX_RETRIES:
        return None
    
    for attempt in range(MAX_RETRIES - retries):
        delay = get_delay_for_id(case_id)
        time.sleep(delay)
        
        data = curl_json(f"{BASE_URL}/case-search/search-by-id/{case_id}")
        
        if data:
            if data.get("id"):
                return data
            
            # Check for rate limit or auth errors
            status = data.get("statusCode", 0)
            if status == 401:
                ensure_token()
            elif status == 429:
                # Rate limited - increase delay significantly
                retry_count[case_id] = retry_count.get(case_id, 0) + 2
                log(f"Rate limited for {case_id}, backing off...")
                time.sleep(30 + random.uniform(0, 30))
            elif status == 403:
                # Forbidden - likely Cloudflare
                retry_count[case_id] = retry_count.get(case_id, 0) + 1
                time.sleep(10 + random.uniform(0, 10))
        
        retry_count[case_id] = retry_count.get(case_id, 0) + 1
    
    return None


def get_ids_to_retry():
    """Get list of IDs that need to be retried."""
    log("Collecting IDs to retry...")
    
    ids_to_retry = set()
    
    # Strategy 1: Load from spider state files
    spider_dirs = [
        "/tmp/eastlaw_data",
        "/root/eastlaw_data",
        "/var/www/pakistanlawapp/eastlaw_data"
    ]
    
    for spider_dir in spider_dirs:
        # Load remaining IDs from spider
        remaining_file = os.path.join(spider_dir, "remaining_ids.json")
        if os.path.exists(remaining_file):
            with open(remaining_file) as f:
                remaining = set(json.load(f))
            log(f"Loaded {len(remaining)} remaining IDs from {remaining_file}")
            ids_to_retry.update(remaining)
        
        # Load spider state
        state_file = os.path.join(spider_dir, "spider_state.json")
        if os.path.exists(state_file):
            with open(state_file) as f:
                state = json.load(f)
            log(f"Spider state: {state}")
    
    # Strategy 2: Compare with MongoDB
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI)
        db = client.pakistanlawsite
        
        # Get all ingested EastLaw IDs
        ingested = set()
        for doc in db.pls_caselaws.find(
            {"source": "eastlaw"},
            {"eastlaw_id": 1}
        ):
            if doc.get("eastlaw_id"):
                ingested.add(doc["eastlaw_id"])
        
        log(f"Found {len(ingested)} already ingested EastLaw cases in MongoDB")
        
        # Get discovered IDs from batch files
        for spider_dir in spider_dirs:
            if os.path.exists(spider_dir):
                for f in os.listdir(spider_dir):
                    if f.startswith("eastlaw_batch_") and f.endswith(".json"):
                        try:
                            with open(os.path.join(spider_dir, f)) as fp:
                                batch = json.load(fp)
                            for case in batch:
                                if case.get("id") and case["id"] not in ingested:
                                    # This was fetched but not ingested yet
                                    pass
                                # Extract referenced IDs that might not have been fetched
                                for ref in case.get("hyperlinking", []):
                                    ref_id = ref.get("judgment_id", {})
                                    if isinstance(ref_id, dict):
                                        oid = ref_id.get("$oid", "")
                                    else:
                                        oid = str(ref_id)
                                    if oid and len(oid) == 24 and oid not in ingested:
                                        ids_to_retry.add(oid)
                        except:
                            pass
        
        client.close()
    except Exception as e:
        log(f"MongoDB comparison failed: {e}")
    
    # Strategy 3: Load from previous retry attempts
    retry_dir = OUTPUT_DIR
    if os.path.exists(retry_dir):
        fetched_file = os.path.join(retry_dir, "fetched_ids.json")
        if os.path.exists(fetched_file):
            with open(fetched_file) as f:
                already_retried = set(json.load(f))
            ids_to_retry -= already_retried
            log(f"Excluded {len(already_retried)} already retried IDs")
    
    log(f"Total IDs to retry: {len(ids_to_retry)}")
    return list(ids_to_retry)


def save_batch(cases, batch_num):
    """Save a batch of successfully fetched cases."""
    filename = os.path.join(OUTPUT_DIR, f"retry_batch_{batch_num:05d}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False)
    log(f"SAVED retry batch {batch_num}: {len(cases)} cases")


def save_state():
    """Save retry state."""
    state = {
        "fetched": len(fetched_ids),
        "failed": len(failed_ids),
        "timestamp": datetime.now().isoformat(),
    }
    with open(os.path.join(OUTPUT_DIR, "retry_state.json"), 'w') as f:
        json.dump(state, f, indent=2)
    
    with open(os.path.join(OUTPUT_DIR, "fetched_ids.json"), 'w') as f:
        json.dump(list(fetched_ids), f)
    
    with open(os.path.join(OUTPUT_DIR, "still_failed_ids.json"), 'w') as f:
        json.dump(list(failed_ids), f)


def load_state():
    """Load previous retry state."""
    global fetched_ids
    
    fetched_file = os.path.join(OUTPUT_DIR, "fetched_ids.json")
    if os.path.exists(fetched_file):
        with open(fetched_file) as f:
            fetched_ids = set(json.load(f))
        log(f"Loaded {len(fetched_ids)} previously retried IDs")


def main():
    global fetched_ids, failed_ids
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    load_state()
    
    log("=" * 60)
    log("EastLaw Retry Script")
    log("Recovering failed cases from spider run")
    log("=" * 60)
    
    if not login():
        log("Cannot proceed without authentication")
        sys.exit(1)
    
    # Get IDs to retry
    ids_to_retry = get_ids_to_retry()
    if not ids_to_retry:
        log("No IDs to retry!")
        return
    
    # Shuffle for better distribution
    random.shuffle(ids_to_retry)
    
    log(f"Starting retry for {len(ids_to_retry)} cases")
    log(f"Concurrency: {CONCURRENT}, Base delay: {BASE_DELAY}s")
    
    batch_num = 1
    current_batch = []
    start_time = time.time()
    
    # Process sequentially to avoid rate limits
    for i, case_id in enumerate(ids_to_retry):
        if case_id in fetched_ids:
            continue
        
        case = fetch_case_with_retry(case_id)
        
        if case:
            current_batch.append(case)
            fetched_ids.add(case_id)
        else:
            failed_ids.add(case_id)
        
        # Save batch
        if len(current_batch) >= BATCH_SIZE:
            save_batch(current_batch, batch_num)
            batch_num += 1
            current_batch = []
            save_state()
        
        # Progress
        if (i + 1) % 20 == 0:
            elapsed = time.time() - start_time
            rate = len(fetched_ids) / max(elapsed, 1) * 3600
            success_rate = len(fetched_ids) / max(i + 1, 1) * 100
            log(f"Progress: {i+1}/{len(ids_to_retry)} | "
                f"Recovered: {len(fetched_ids)} | "
                f"Failed: {len(failed_ids)} | "
                f"Rate: {rate:.0f}/hr | "
                f"Success: {success_rate:.1f}%")
    
    # Save remaining
    if current_batch:
        save_batch(current_batch, batch_num)
    
    save_state()
    
    elapsed = (time.time() - start_time) / 3600
    recovery_rate = len(fetched_ids) / max(len(ids_to_retry), 1) * 100
    
    log("=" * 60)
    log("RETRY COMPLETE")
    log(f"  Attempted: {len(ids_to_retry)}")
    log(f"  Recovered: {len(fetched_ids)}")
    log(f"  Still Failed: {len(failed_ids)}")
    log(f"  Recovery Rate: {recovery_rate:.1f}%")
    log(f"  Time: {elapsed:.2f} hours")
    log("=" * 60)
    log(f"Recovered cases saved to: {OUTPUT_DIR}")
    log("Run ingest_eastlaw.py to import them to MongoDB")


if __name__ == "__main__":
    main()
