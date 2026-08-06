#!/usr/bin/env python3
"""
import_headnotes_v2.py
Improved headnote importer with batch processing and deduplication.
"""

import os, sys, json, re, logging
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'pakistanlawsite')
BATCH_SIZE = 500


def normalize_citation(citation):
    """Normalize citation for matching."""
    if not citation:
        return None
    citation = citation.upper().strip()
    citation = re.sub(r'\s+', ' ', citation)
    return citation


def extract_headnote(text):
    """Extract headnote from case text."""
    if not text:
        return None
    patterns = [
        r'HEADNOTE[:\s]*(.+?)(?=\n\s*\n|\Z)',
        r'SUMMARY[:\s]*(.+?)(?=\n\s*\n|\Z)',
        r'HELD[:\s]*(.+?)(?=\n\s*\n|\Z)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(1).strip()[:2000]
    return None


def process_batch(db, cases, source_label):
    """Process a batch of cases with headnotes."""
    inserted = 0
    updated = 0
    
    for case in cases:
        try:
            citation = normalize_citation(case.get('citation') or case.get('citation_display'))
            case_id = case.get('case_id') or case.get('casename')
            
            headnote = case.get('headnote') or case.get('ai_headnote')
            if not headnote:
                headnote = extract_headnote(case.get('full_text', ''))
            
            if not headnote:
                continue
            
            doc = {
                'citation': citation,
                'case_id': case_id,
                'headnote': headnote,
                'source': source_label,
                'updated_at': datetime.utcnow().isoformat(),
            }
            
            # Upsert by citation or case_id
            result = db.pls_headnotes.update_one(
                {'$or': [
                    {'citation': citation},
                    {'case_id': case_id}
                ]},
                {'$set': doc},
                upsert=True
            )
            
            if result.upserted_id:
                inserted += 1
            elif result.modified_count:
                updated += 1
                
        except Exception as e:
            logger.warning(f"Error processing case: {e}")
    
    return inserted, updated


def import_from_file(db, filepath, source_label):
    """Import headnotes from a JSON file."""
    logger.info(f"Importing from {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict):
        cases = data.get('cases', [data])
    elif isinstance(data, list):
        cases = data
    else:
        logger.warning(f"Unexpected data format in {filepath}")
        return 0, 0
    
    total_inserted = 0
    total_updated = 0
    
    for i in range(0, len(cases), BATCH_SIZE):
        batch = cases[i:i + BATCH_SIZE]
        ins, upd = process_batch(db, batch, source_label)
        total_inserted += ins
        total_updated += upd
        logger.info(f"  Batch {i//BATCH_SIZE + 1}: +{ins} inserted, {upd} updated")
    
    logger.info(f"Total from {filepath}: +{total_inserted} inserted, {total_updated} updated")
    return total_inserted, total_updated


def import_from_directory(db, dirpath, source_label):
    """Import headnotes from all JSON files in a directory."""
    if not os.path.exists(dirpath):
        logger.warning(f"Directory not found: {dirpath}")
        return 0, 0
    
    total_inserted = 0
    total_updated = 0
    
    for filename in os.listdir(dirpath):
        if filename.endswith('.json'):
            filepath = os.path.join(dirpath, filename)
            ins, upd = import_from_file(db, filepath, source_label)
            total_inserted += ins
            total_updated += upd
    
    return total_inserted, total_updated


def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    logger.info("=" * 50)
    logger.info("Headnote Importer v2")
    logger.info("=" * 50)
    
    initial_count = db.pls_headnotes.count_documents({})
    logger.info(f"Initial headnote count: {initial_count}")
    
    total_ins = 0
    total_upd = 0
    
    # Import from various sources
    sources = [
        ('/tmp/eastlaw_data', 'eastlaw'),
        ('/tmp/scraped_cases', 'scraper'),
        ('/tmp/headnotes', 'manual'),
    ]
    
    for dirpath, label in sources:
        if os.path.exists(dirpath):
            ins, upd = import_from_directory(db, dirpath, label)
            total_ins += ins
            total_upd += upd
    
    final_count = db.pls_headnotes.count_documents({})
    
    logger.info("=" * 50)
    logger.info("Import complete")
    logger.info(f"  Initial: {initial_count}")
    logger.info(f"  Inserted: +{total_ins}")
    logger.info(f"  Updated: {total_upd}")
    logger.info(f"  Final: {final_count}")
    logger.info("=" * 50)
    
    client.close()


if __name__ == "__main__":
    main()
