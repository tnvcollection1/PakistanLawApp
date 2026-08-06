#!/usr/bin/env python3
"""
Sync local MongoDB data to production.
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime

LOCAL_MONGO_URI = os.getenv('LOCAL_MONGO_URI', 'mongodb://localhost:27017/')
PROD_MONGO_URI = os.getenv('PROD_MONGO_URI')
DB_NAME = os.getenv('DB_NAME', 'pakistanlaw')

if not PROD_MONGO_URI:
    print("Error: PROD_MONGO_URI environment variable not set")
    sys.exit(1)

def sync_collection(collection_name, batch_size=100):
    """Sync a single collection from local to production."""
    local_client = MongoClient(LOCAL_MONGO_URI)
    prod_client = MongoClient(PROD_MONGO_URI)
    
    local_db = local_client[DB_NAME]
    prod_db = prod_client[DB_NAME]
    
    local_collection = local_db[collection_name]
    prod_collection = prod_db[collection_name]
    
    total = local_collection.count_documents({})
    print(f"Syncing {total} documents from '{collection_name}'...")
    
    synced = 0
    batch = []
    
    for doc in local_collection.find():
        # Remove _id to avoid conflicts
        doc.pop('_id', None)
        batch.append(doc)
        
        if len(batch) >= batch_size:
            prod_collection.insert_many(batch, ordered=False)
            synced += len(batch)
            print(f"Synced {synced}/{total}...")
            batch = []
    
    if batch:
        prod_collection.insert_many(batch, ordered=False)
        synced += len(batch)
    
    print(f"Completed: {synced} documents synced")
    
    local_client.close()
    prod_client.close()

if __name__ == '__main__':
    collections = ['cases', 'statutes', 'search_queries']
    
    for collection in collections:
        try:
            sync_collection(collection)
        except Exception as e:
            print(f"Error syncing {collection}: {e}")
            continue
    
    print("\nSync completed!")
