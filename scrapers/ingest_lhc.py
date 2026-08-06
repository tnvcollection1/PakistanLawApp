#!/usr/bin/env python3
"""
Ingest LHC scraped data into MongoDB
Run this on VPS after uploading lhc_data folder to /tmp/lhc_data/
"""

import json
import os
import glob
from datetime import datetime
from pymongo import MongoClient, UpdateOne

# MongoDB connection
MONGO_URI = 'mongodb://lawapp:VpsMongo2026LawXk9@localhost:27017/pakistanlawsite?authSource=pakistanlawsite'
DB_NAME = 'pakistanlawsite'
COLLECTION = 'pls_caselaws'

# Data directory
DATA_DIR = '/tmp/lhc_data'

def log(msg):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {msg}')

def main():
    log('=' * 60)
    log('LHC DATA INGESTION')
    log('=' * 60)
    
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION]
    
    # Find batch files
    batch_files = sorted(glob.glob(f'{DATA_DIR}/lhc_batch_*.json'))
    log(f'Found {len(batch_files)} batch files')
    
    if not batch_files:
        log('No batch files found!')
        return
    
    total_new = 0
    total_updated = 0
    
    for batch_file in batch_files:
        log(f'Processing {os.path.basename(batch_file)}...')
        
        with open(batch_file, 'r', encoding='utf-8') as f:
            judgments = json.load(f)
        
        operations = []
        for j in judgments:
            # Create unique ID from URL
            lhc_id = j.get('url', '').split('/')[-1] or j.get('title', '')[:50]
            
            doc = {
                'lhc_id': lhc_id,
                'source': 'lhc',
                'title': j.get('title', ''),
                'judgment_text': j.get('judgment_text', ''),
                'court': 'Lahore High Court',
                'url': j.get('url', ''),
                'scraped_at': j.get('scraped_at', datetime.now().isoformat()),
                'updated_at': datetime.now().isoformat(),
            }
            
            # Add any extracted metadata
            for field in ['case_number', 'date', 'judge', 'parties']:
                if field in j:
                    doc[field] = j[field]
            
            operations.append(UpdateOne(
                {'lhc_id': lhc_id},
                {'': doc},
                upsert=True
            ))
        
        if operations:
            result = collection.bulk_write(operations)
            total_new += result.upserted_count
            total_updated += result.modified_count
            log(f'  -> New: {result.upserted_count}, Updated: {result.modified_count}')
    
    # Final count
    lhc_count = collection.count_documents({'source': 'lhc'})
    total_count = collection.count_documents({})
    
    log('\n' + '=' * 60)
    log('INGESTION COMPLETE')
    log(f'  New documents: {total_new}')
    log(f'  Updated: {total_updated}')
    log(f'  Total LHC cases: {lhc_count}')
    log(f'  Total all cases: {total_count}')
    log('=' * 60)
    log('\nRun incremental_update.py to generate FAISS embeddings')

if __name__ == '__main__':
    main()
