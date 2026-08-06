import os
import requests
from pymongo import MongoClient
from datetime import datetime
import time

PRODUCTION_URL = "https://tnv.ae/api/admin/import/caselaws"
SECRET = os.environ.get("ADMIN_SECRET", "")
BATCH_SIZE = 25  # Very small
LOG_FILE = "/app/backend/sync_progress.log"

def log(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")

with open(LOG_FILE, 'w') as f:
    f.write("")

log("=" * 50)
log("SYNC V5 - TINY BATCHES (25)")
log("=" * 50)

client = MongoClient('mongodb://localhost:27017')
db = client['test_database']

# Check current production count
resp = requests.get("https://tnv.ae/api/admin/import/status", timeout=30)
already_synced = resp.json().get('pls_caselaws', 56722)

total = db.pls_caselaws.count_documents({})
log(f"Production: {already_synced:,} | Target: {total:,}")
log(f"Remaining: {total - already_synced:,}")

synced = 0
errors = 0
start = time.time()
cursor = db.pls_caselaws.find({}).skip(already_synced)
batch = []

for doc in cursor:
    doc['_id'] = str(doc['_id'])
    for k, v in doc.items():
        if hasattr(v, 'isoformat'):
            doc[k] = v.isoformat()
    batch.append(doc)
    
    if len(batch) >= BATCH_SIZE:
        for retry in range(5):
            try:
                resp = requests.post(PRODUCTION_URL, json={"records": batch, "secret": SECRET}, timeout=60)
                if resp.status_code == 200:
                    synced += len(batch)
                    break
                else:
                    time.sleep(5)
            except:
                time.sleep(5)
        else:
            errors += 1
        
        if synced % 500 < BATCH_SIZE:
            total_done = already_synced + synced
            pct = 100 * total_done / total
            elapsed = time.time() - start
            rate = synced / elapsed if elapsed > 0 else 0
            eta = (total - total_done) / rate / 60 if rate > 0 else 0
            log(f"✅ {total_done:,}/{total:,} ({pct:.1f}%) | {rate:.0f}/s | ETA: {eta:.0f}m | Err: {errors}")
        
        batch = []
        time.sleep(0.5)

if batch:
    try:
        resp = requests.post(PRODUCTION_URL, json={"records": batch, "secret": SECRET}, timeout=60)
        if resp.status_code == 200:
            synced += len(batch)
    except:
        pass

log(f"\n✅ DONE: +{synced:,} synced | {errors} errors")
client.close()
