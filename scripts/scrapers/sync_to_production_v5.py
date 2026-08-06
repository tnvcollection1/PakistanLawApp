#!/usr/bin/env python3
"""
Production sync v5 with differential sync and conflict resolution.
"""

import os
import sys
import hashlib
import logging
from datetime import datetime
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('sync_v5')

LOCAL_MONGO_URI = os.getenv('LOCAL_MONGO_URI', 'mongodb://localhost:27017/')
PROD_MONGO_URI = os.getenv('PROD_MONGO_URI')
DB_NAME = os.getenv('DB_NAME', 'pakistanlaw')

def compute_doc_hash(doc):
    """Compute hash for change detection."""
    clean = {k: v for k, v in doc.items() if k not in ('_id', 'synced_at', 'hash', 'updated_at')}
    return hashlib.sha256(str(sorted(clean.items())).encode()).hexdigest()

def get_doc_id(doc):
    """Extract document identifier."""
    return doc.get('citation') or doc.get('act_number') or str(doc.get('_id'))

def sync_collection_diff(collection_name):
    """Differential sync - only sync changed documents."""
    logger.info(f"Starting differential sync for '{collection_name}'")
    
    local_client = MongoClient(LOCAL_MONGO_URI)
    prod_client = MongoClient(PROD_MONGO_URI)
    
    try:
        local_db = local_client[DB_NAME]
        prod_db = prod_client[DB_NAME]
        
        local_coll = local_db[collection_name]
        prod_coll = prod_db[collection_name]
        
        # Get existing hashes from production
        prod_hashes = {}
        for doc in prod_coll.find({}, {'citation': 1, 'act_number': 1, 'hash': 1}):
            doc_id = get_doc_id(doc)
            if doc_id:
                prod_hashes[doc_id] = doc.get('hash', '')
        
        logger.info(f"Found {len(prod_hashes)} existing documents in production")
        
        to_sync = []
        for doc in local_coll.find():
            doc_id = get_doc_id(doc)
            if not doc_id:
                continue
            
            current_hash = compute_doc_hash(doc)
            
            if prod_hashes.get(doc_id) != current_hash:
                update_doc = {k: v for k, v in doc.items() if k != '_id'}
                update_doc['hash'] = current_hash
                update_doc['synced_at'] = datetime.utcnow()
                
                to_sync.append(UpdateOne(
                    {'_id': doc_id},
                    {'$set': update_doc},
                    upsert=True
                ))
        
        logger.info(f"Found {len(to_sync)} documents to sync")
        
        if not to_sync:
            logger.info("No changes detected")
            return
        
        # Batch write
        batch_size = 100
        synced = 0
        for i in range(0, len(to_sync), batch_size):
            batch = to_sync[i:i+batch_size]
            result = prod_coll.bulk_write(batch)
            synced += result.upserted_count + result.modified_count
            logger.info(f"Batch {i//batch_size + 1}: {result.upserted_count} upserted, {result.modified_count} updated")
        
        logger.info(f"Total synced: {synced}")
        
        # Update metadata
        prod_db.sync_metadata.update_one(
            {'collection': collection_name},
            {'$set': {
                'last_sync': datetime.utcnow(),
                'sync_type': 'differential',
                'documents_synced': synced
            }},
            upsert=True
        )
        
    finally:
        local_client.close()
        prod_client.close()

if __name__ == '__main__':
    if not PROD_MONGO_URI:
        logger.error("PROD_MONGO_URI not set")
        sys.exit(1)
    
    collections = sys.argv[1:] or ['cases', 'statutes']
    
    for collection in collections:
        try:
            sync_collection_diff(collection)
        except Exception as e:
            logger.error(f"Error syncing {collection}: {e}")
            continue
    
    logger.info("Sync v5 completed")
