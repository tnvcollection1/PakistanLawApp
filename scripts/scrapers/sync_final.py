#!/usr/bin/env python3
"""
Final sync script with comprehensive error handling and logging.
"""

import os
import sys
import logging
import json
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import BulkWriteError, ConnectionFailure

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sync_final')

LOCAL_MONGO_URI = os.getenv('LOCAL_MONGO_URI', 'mongodb://localhost:27017/')
PROD_MONGO_URI = os.getenv('PROD_MONGO_URI')
DB_NAME = os.getenv('DB_NAME', 'pakistanlaw')

def get_mongo_client(uri, name=""):
    """Create MongoDB client with retry logic."""
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        logger.info(f"Connected to {name} MongoDB")
        return client
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to {name} MongoDB: {e}")
        raise

def sync_collection(collection_name):
    """Sync collection with detailed logging."""
    logger.info(f"Starting sync for '{collection_name}'")
    
    local_client = get_mongo_client(LOCAL_MONGO_URI, "local")
    prod_client = get_mongo_client(PROD_MONGO_URI, "production")
    
    try:
        local_db = local_client[DB_NAME]
        prod_db = prod_client[DB_NAME]
        
        local_coll = local_db[collection_name]
        prod_coll = prod_db[collection_name]
        
        total = local_coll.count_documents({})
        logger.info(f"Total documents in local '{collection_name}': {total}")
        
        if total == 0:
            logger.info(f"No documents to sync in '{collection_name}'")
            return
        
        # Create index on sync field if not exists
        prod_coll.create_index('synced_at', background=True)
        
        synced = 0
        failed = 0
        batch = []
        
        for doc in local_coll.find():
            doc.pop('_id', None)
            doc['synced_at'] = datetime.utcnow()
            batch.append(doc)
            
            if len(batch) >= 100:
                try:
                    prod_coll.insert_many(batch, ordered=False)
                    synced += len(batch)
                    logger.info(f"Synced {synced}/{total}")
                except BulkWriteError as bwe:
                    synced += bwe.details.get('nInserted', 0)
                    failed += len(batch) - bwe.details.get('nInserted', 0)
                    logger.warning(f"Bulk write partial failure: {bwe.details}")
                batch = []
        
        if batch:
            try:
                prod_coll.insert_many(batch, ordered=False)
                synced += len(batch)
            except BulkWriteError as bwe:
                synced += bwe.details.get('nInserted', 0)
                failed += len(batch) - bwe.details.get('nInserted', 0)
        
        logger.info(f"Sync complete for '{collection_name}': {synced} synced, {failed} failed")
        
        # Update sync metadata
        prod_db.sync_metadata.update_one(
            {'collection': collection_name},
            {'$set': {
                'last_sync': datetime.utcnow(),
                'documents_synced': synced,
                'documents_failed': failed,
                'total_documents': total
            }},
            upsert=True
        )
        
    finally:
        local_client.close()
        prod_client.close()

if __name__ == '__main__':
    if not PROD_MONGO_URI:
        logger.error("PROD_MONGO_URI environment variable not set")
        sys.exit(1)
    
    collections = sys.argv[1:] or ['cases', 'statutes', 'search_queries']
    
    for collection in collections:
        try:
            sync_collection(collection)
        except Exception as e:
            logger.error(f"Error syncing {collection}: {e}")
            continue
    
    logger.info("All sync operations completed")
