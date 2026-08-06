#!/usr/bin/env python3
"""
Import CSV data into MongoDB for Pakistan Law App.
"""

import csv
import sys
import os
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'pakistanlaw')

def import_cases(csv_path, collection_name='cases'):
    """Import cases from CSV file into MongoDB."""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[collection_name]
    
    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean and prepare document
            doc = {
                'title': row.get('title', '').strip(),
                'citation': row.get('citation', '').strip(),
                'court': row.get('court', '').strip(),
                'year': int(row.get('year', 0)) if row.get('year') else None,
                'content': row.get('content', '').strip(),
                'url': row.get('url', '').strip(),
                'imported_at': datetime.utcnow(),
            }
            
            # Skip empty titles
            if not doc['title']:
                continue
            
            # Upsert based on citation
            collection.update_one(
                {'citation': doc['citation']},
                {'$set': doc},
                upsert=True
            )
            count += 1
            
            if count % 100 == 0:
                print(f"Imported {count} cases...")
    
    print(f"Total imported: {count} cases")
    client.close()

def import_statutes(csv_path, collection_name='statutes'):
    """Import statutes from CSV file into MongoDB."""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[collection_name]
    
    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc = {
                'title': row.get('title', '').strip(),
                'act_number': row.get('act_number', '').strip(),
                'year': int(row.get('year', 0)) if row.get('year') else None,
                'description': row.get('description', '').strip(),
                'url': row.get('url', '').strip(),
                'imported_at': datetime.utcnow(),
            }
            
            if not doc['title']:
                continue
            
            collection.update_one(
                {'act_number': doc['act_number']},
                {'$set': doc},
                upsert=True
            )
            count += 1
    
    print(f"Total imported: {count} statutes")
    client.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python import_csv_to_mongo.py <csv_file> <type: cases|statutes>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    import_type = sys.argv[2]
    
    if import_type == 'cases':
        import_cases(csv_file)
    elif import_type == 'statutes':
        import_statutes(csv_file)
    else:
        print(f"Unknown import type: {import_type}")
        sys.exit(1)
