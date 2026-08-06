import os
import requests
import json
from pymongo import MongoClient
from datetime import datetime
import time

PRODUCTION_URL = "https://tnv.ae/api/admin/import/caselaws"
SECRET = os.environ.get("ADMIN_SECRET", "")
BATCH_SIZE = 100  # Smaller batches to avoid 500 errors
LOG_FILE = "/app/backend/sync_progress.log"

def log(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")

log("\n" + "=" * 50)
log("RESUMING SYNC (smaller batches)")
log("=" * 50)

client = MongoClient('mongodb://localhost:27017')
db = client['test_database']

# Get IDs already synced to production
log("Checking production for existing IDs...")
resp = requests.get("https://tnv.ae/api/admin/import/status", timeout=30)
prod_count = resp.json().get('pls_caselaws', 0)
log(f"Production has: {prod_count:,} records")

total = db.pls_caselaws.count_documents({})
log(f"Local has: {total:,} records")
log(f"Will sync all and upsert (skip duplicates)")

synced = 0
errors = 0
consecutive_errors = 0
start = time.time()
cursor = db.pls_caselaws.find({})
batch = []

for doc in cursor:
    doc['_id'] = str(doc['_id'])
    for k, v in doc.items():
        if hasattr(v, 'isoformat'):
            doc[k] = v.isoformat()
    batch.append(doc)
    
    if len(batch) >= BATCH_SIZE:
        try:
            resp = requests.post(PRODUCTION_URL, json={"records": batch, "secret": SECRET}, timeout=180)
            if resp.status_code == 200:
                synced += len(batch)
                consecutive_errors = 0
                pct = 100*synced/total
                elapsed = time.time() - start
                rate = synced/elapsed if elapsed > 0 else 0
                eta = (total-synced)/rate/60 if rate > 0 else 0
                if synced % 1000 < BATCH_SIZE:
                    log(f"✅ {synced:,}/{total:,} ({pct:.1f}%) | {rate:.0f}/s | ETA: {eta:.0f}m")
            else:
                errors += 1
                consecutive_errors += 1
                if consecutive_errors >= 5:
                    log(f"⚠️ Too many errors, pausing 30s...")
                    time.sleep(30)
                    consecutive_errors = 0
        except Exception as e:
            errors += 1
            consecutive_errors += 1
            if consecutive_errors >= 5:
                log(f"⚠️ Connection issues, pausing 30s...")
                time.sleep(30)
                consecutive_errors = 0
        batch = []
        time.sleep(0.1)  # Small delay between batches

if batch:
    try:
        resp = requests.post(PRODUCTION_URL, json={"records": batch, "secret": SECRET}, timeout=180)
        if resp.status_code == 200:
            synced += len(batch)
    except:
        pass

elapsed = time.time() - start
log(f"\n✅ DONE: {synced:,} synced, {errors} errors, {elapsed/60:.1f}m")
client.close()
