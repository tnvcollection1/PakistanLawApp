import os
import pymongo
import requests
from bs4 import BeautifulSoup
import json

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = 'pakistanlaw'

def sync_to_production_v3():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print("Syncing to production v3...")
    # Enhanced sync logic with JSON export
    data = list(db.judgments.find().limit(100))
    with open('sync_data.json', 'w') as f:
        json.dump(data, f, default=str)
    print("Done.")

if __name__ == '__main__':
    sync_to_production_v3()
