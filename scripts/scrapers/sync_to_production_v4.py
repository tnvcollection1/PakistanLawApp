import os
import requests
import json
from pymongo import MongoClient
from datetime import datetime
import time

PRODUCTION_URL = "https://tnv.ae/api/admin/import/caselaws"
SECRET = os.environ.get("ADMIN_SECRET", "")
BATCH_SIZE = 100
LOG_FILE = "/app/backend/sync_progress.log"

def log(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")

# Clear log
with open(LOG_FILE, 'w') as f:
    f.write("")

log("=" * 50)
log("SYNC V4 - RESUMING FROM 56,722")
log("=" * 50)

client = MongoClient('mongodb://localhost:27017')
db = client['test_database']

total = db.pls_caselaws.count_documents({})
already_synced = 56722
skip_count = already_synced

log(f"Total: {total:,} | Already synced: {already_synced:,}")
log(f"Remaining: {total - already_synced:,}")

synced = 0
errors = 0
start = time.time()
cursor = db.pls_caselaws.find({}).skip(skip_count)
batch = []

for doc in cursor:
    doc['_id'] = str(doc['_id'])
    for k, v in doc.items():
        if hasattr(v, 'isoformat'):
            doc[k] = v.isoformat()
    batch.append(doc)
    
    if len(batch) >= BATCH_SIZE:
        success = False
        for retry in range(3):
            try:
                resp = requests.post(PRODUCTION_URL, json={"records": batch, "secret": SECRET}, timeout=120)
                if resp.status_code == 200:
                    synced += len(batch)
                    success = True
                    break
                elif resp.status_code >= 500:
                    log(f"⚠️ Server error {resp.status_code}, waiting 10s...")
                    time.sleep(10)
            except Exception as e:
                log(f"⚠️ Connection error, waiting 10s...")
                time.sleep(10)
        
        if not success:
            errors += 1
            log(f"❌ Failed batch after 3 retries")
        
        if synced % 1000 < BATCH_SIZE:
            total_done = already_synced + synced
            pct = 100 * total_done / total
            elapsed = time.time() - start
            rate = synced / elapsed if elapsed > 0 else 0
            remaining = total - total_done
            eta = remaining / rate / 60 if rate > 0 else 0
            log(f"✅ {total_done:,}/{total:,} ({pct:.1f}%) | {rate:.0f}/s | ETA: {eta:.0f}m")
        
        batch = []
        time.sleep(0.3)  # Gentle delay

if batch:
    try:
        resp = requests.post(PRODUCTION_URL, json={"records": batch, "secret": SECRET}, timeout=120)
        if resp.status_code == 200:
            synced += len(batch)
    except:
        pass

elapsed = time.time() - start
log(f"\n{'='*50}")
log(f"✅ SYNC COMPLETE")
log(f"Synced this session: {synced:,}")
log(f"Total in production: {already_synced + synced:,}")
log(f"Errors: {errors}")
log(f"Time: {elapsed/60:.1f} minutes")
client.close()
