import os
import requests
from pymongo import MongoClient
from datetime import datetime
import time

PRODUCTION_URL = "https://tnv.ae/api/admin/import/caselaws"
SECRET = os.environ.get("ADMIN_SECRET", "")
BATCH_SIZE = 20
LOG_FILE = "/app/backend/sync_progress.log"

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")

with open(LOG_FILE, 'w') as f:
    f.write("")

log("FINAL SYNC - Starting")

client = MongoClient('mongodb://localhost:27017')
db = client['test_database']

# Get current production count
try:
    resp = requests.get("https://tnv.ae/api/pls/stats", timeout=30)
    already = resp.json().get('caselaws', 56762)
except:
    already = 56762

total = db.pls_caselaws.count_documents({})
log(f"Production: {already:,} | Local: {total:,} | To sync: {total-already:,}")

synced = 0
errors = 0
start = time.time()
cursor = db.pls_caselaws.find({}).skip(already)
batch = []

for doc in cursor:
    doc['_id'] = str(doc['_id'])
    for k, v in doc.items():
        if hasattr(v, 'isoformat'):
            doc[k] = v.isoformat()
    batch.append(doc)
    
    if len(batch) >= BATCH_SIZE:
        ok = False
        for _ in range(5):
            try:
                r = requests.post(PRODUCTION_URL, json={"records": batch, "secret": SECRET}, timeout=90)
                if r.status_code == 200:
                    synced += len(batch)
                    ok = True
                    break
                time.sleep(3)
            except:
                time.sleep(3)
        if not ok:
            errors += 1
        
        if synced % 500 < BATCH_SIZE:
            done = already + synced
            pct = 100*done/total
            rate = synced/(time.time()-start) if time.time()-start > 0 else 0
            eta = (total-done)/rate/60 if rate > 0 else 999
            log(f"✅ {done:,}/{total:,} ({pct:.1f}%) | {rate:.1f}/s | ETA:{eta:.0f}m | E:{errors}")
        
        batch = []
        time.sleep(0.3)

if batch:
    try:
        r = requests.post(PRODUCTION_URL, json={"records": batch, "secret": SECRET}, timeout=90)
        if r.status_code == 200:
            synced += len(batch)
    except:
        pass

log(f"DONE: +{synced:,} | Total: {already+synced:,} | Errors: {errors}")
client.close()
