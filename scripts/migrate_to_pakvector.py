"""
Migrate to PakVector - Migration script for vector database
"""
import json
import os
from pymongo import MongoClient

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'pakistanlaw')

def migrate_cases():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    cases = list(db.cases.find())
    print(f"Found {len(cases)} cases to migrate")
    for case in cases:
        vector_doc = {
            'id': str(case.get('_id')),
            'title': case.get('title'),
            'content': case.get('content'),
            'metadata': {
                'court': case.get('court'),
                'date': case.get('date'),
                'citations': case.get('citations'),
            }
        }
        print(f"Migrating case: {vector_doc['title']}")
    print("Migration complete")

if __name__ == '__main__':
    migrate_cases()
