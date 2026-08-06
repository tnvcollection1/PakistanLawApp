"""
Ingest to MongoDB - Script to ingest scraped data into MongoDB
"""
import json
import os
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'pakistanlaw')

def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def ingest_cases(cases_file):
    db = get_db()
    with open(cases_file, 'r') as f:
        cases = json.load(f)
    for case in cases:
        case['ingested_at'] = datetime.utcnow()
        db.cases.update_one(
            {'id': case.get('id')},
            {'$set': case},
            upsert=True
        )
    print(f"Ingested {len(cases)} cases")

def ingest_statutes(statutes_file):
    db = get_db()
    with open(statutes_file, 'r') as f:
        statutes = json.load(f)
    for statute in statutes:
        statute['ingested_at'] = datetime.utcnow()
        db.statutes.update_one(
            {'id': statute.get('id')},
            {'$set': statute},
            upsert=True
        )
    print(f"Ingested {len(statutes)} statutes")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ingest_to_mongodb.py <cases.json> [statutes.json]")
        sys.exit(1)
    ingest_cases(sys.argv[1])
    if len(sys.argv) > 2:
        ingest_statutes(sys.argv[2])
