import os
import pymongo
import requests
from bs4 import BeautifulSoup
import json
import time

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = 'pakistanlaw'

def sync_to_production_v2():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print("Syncing to production v2...")
    # Batch sync logic
    batch_size = 100
    offset = 0
    while True:
        batch = list(db.judgments.find().skip(offset).limit(batch_size))
        if not batch:
            break
        print(f"Synced batch at offset {offset}")
        offset += batch_size
        time.sleep(0.5)
    print("Done.")

if __name__ == '__main__':
    sync_to_production_v2()
