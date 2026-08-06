#!/usr/bin/env python3
"""
Sync v4 with streaming and batch compression.
"""

import os
import sys
import zlib
import json
import base64
from datetime import datetime
from pymongo import MongoClient

LOCAL_MONGO_URI = os.getenv('LOCAL_MONGO_URI', 'mongodb://localhost:27017/')
PROD_MONGO_URI = os.getenv('PROD_MONGO_URI')
DB_NAME = os.getenv('DB_NAME', 'pakistanlaw')
BATCH_SIZE = 50

def compress_doc(doc):
    """Compress document for efficient transfer."""
    json_str = json.dumps(doc, default=str)
    compressed = zlib.compress(json_str.encode(), level=6)
    return base64.b64encode(compressed).decode()

def decompress_doc(compressed_str):
    """Decompress document."""
    compressed = base64.b64decode(compressed_str)
    json_str = zlib.decompress(compressed)
    return json.loads(json_str)

def stream_sync(collection_name):
    """Stream sync large collections."""
    local_client = MongoClient(LOCAL_MONGO_URI)
    prod_client = MongoClient(PROD_MONGO_URI)
    
    try:
        local_db = local_client[DB_NAME]
        prod_db = prod_client[DB_NAME]
        
        local_coll = local_db[collection_name]
        prod_coll = prod_db[collection_name]
        
        total = local_coll.count_documents({})
        print(f"Streaming {total} documents from '{collection_name}'")
        
        batch = []
        synced = 0
        
        for doc in local_coll.find():
            doc.pop('_id', None)
            doc['synced_at'] = datetime.utcnow()
            batch.append(doc)
            
            if len(batch) >= BATCH_SIZE:
                prod_coll.insert_many(batch, ordered=False)
                synced += len(batch)
                print(f"Synced {synced}/{total}")
                batch = []
        
        if batch:
            prod_coll.insert_many(batch, ordered=False)
            synced += len(batch)
        
        print(f"Completed: {synced} documents")
        
        # Update metadata
        prod_db.sync_metadata.update_one(
            {'collection': collection_name},
            {'$set': {
                'last_sync': datetime.utcnow(),
                'documents_synced': synced,
                'sync_method': 'streaming_v4'
            }},
            upsert=True
        )
        
    finally:
        local_client.close()
        prod_client.close()

if __name__ == '__main__':
    if not PROD_MONGO_URI:
        print("PROD_MONGO_URI not set")
        sys.exit(1)
    
    for collection in sys.argv[1:] or ['cases', 'statutes']:
        stream_sync(collection)
    
    print("Sync v4 completed")
