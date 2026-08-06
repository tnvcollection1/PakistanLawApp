#!/usr/bin/env python3
"""
Enhanced sync script with conflict resolution and incremental updates.
"""

import os
import sys
import hashlib
from datetime import datetime
from pymongo import MongoClient, UpdateOne

LOCAL_MONGO_URI = os.getenv('LOCAL_MONGO_URI', 'mongodb://localhost:27017/')
PROD_MONGO_URI = os.getenv('PROD_MONGO_URI')
DB_NAME = os.getenv('DB_NAME', 'pakistanlaw')

if not PROD_MONGO_URI:
    print("Error: PROD_MONGO_URI not set")
    sys.exit(1)

def compute_hash(doc):
    """Compute hash of document for change detection."""
    # Remove internal fields
    clean_doc = {k: v for k, v in doc.items() if k not in ('_id', 'synced_at', 'hash')}
    return hashlib.md5(str(clean_doc).encode()).hexdigest()

def sync_with_conflict_resolution(collection_name, batch_size=100):
    """Sync with conflict resolution based on updated_at timestamps."""
    local_client = MongoClient(LOCAL_MONGO_URI)
    prod_client = MongoClient(PROD_MONGO_URI)
    
    local_db = local_client[DB_NAME]
    prod_db = prod_client[DB_NAME]
    
    local_coll = local_db[collection_name]
    prod_coll = prod_db[collection_name]
    
    # Get last sync timestamp
    last_sync = None
    sync_meta = prod_db.sync_metadata.find_one({'collection': collection_name})
    if sync_meta:
        last_sync = sync_meta.get('last_sync')
    
    # Query for new/modified documents
    query = {}
    if last_sync:
        query['updated_at'] = {'$gt': last_sync}
    
    docs = list(local_coll.find(query))
    print(f"Found {len(docs)} documents to sync in '{collection_name}'")
    
    if not docs:
        print("Nothing to sync")
        return
    
    operations = []
    for doc in docs:
        doc_id = doc.get('citation') or doc.get('act_number') or doc.get('_id')
        
        # Remove _id for upsert
        update_doc = {k: v for k, v in doc.items() if k != '_id'}
        update_doc['synced_at'] = datetime.utcnow()
        update_doc['hash'] = compute_hash(doc)
        
        operations.append(UpdateOne(
            {'_id': doc_id},
            {'$set': update_doc},
            upsert=True
        ))
    
    # Bulk write
    for i in range(0, len(operations), batch_size):
        batch = operations[i:i+batch_size]
        result = prod_coll.bulk_write(batch)
        print(f"Batch {i//batch_size + 1}: {result.upserted_count} inserted, {result.modified_count} updated")
    
    # Update sync metadata
    prod_db.sync_metadata.update_one(
        {'collection': collection_name},
        {'$set': {'last_sync': datetime.utcnow(), 'collection': collection_name}},
        upsert=True
    )
    
    local_client.close()
    prod_client.close()
    print(f"Sync completed for {collection_name}")

if __name__ == '__main__':
    collections = sys.argv[1:] or ['cases', 'statutes']
    
    for collection in collections:
        try:
            sync_with_conflict_resolution(collection)
        except Exception as e:
            print(f"Error syncing {collection}: {e}")
            continue
