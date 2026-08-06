#!/usr/bin/env python3
"""
Find Missing Case Laws - Comprehensive search across all journals and years
Uses fresh cookies to find cases not already in the database
"""
import subprocess
import re
import json
import time
from datetime import datetime
import pymongo
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('/app/backend/.env')

# Fresh cookies
COOKIE = 'ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj; __RequestVerificationToken=cgGcIYoNV7nI6OcGKHg1CT9MoWn8iaRUpmxN-4q7PjvEfhtYG78RWELK-UA5wM8CZE0lSLjYOX-EL-aofCi3Zth-khKoUOn8cHY7Pbuzpt01; x-hng=lang=en-US&domain=www.pakistanlawsite.com'

# All known journals
JOURNALS = [
    'PLD', 'CLC', 'CLCN', 'MLD', 'YLR', 'YLRN', 'SCMR', 'PCRLJ', 'PCRLJN',
    'PTD', 'PLC', 'PLCN', 'PLJ', 'PSC', 'KLR', 'NLR', 'GBLR', 'BLD',
    'CLD', 'PTR', 'PTCL', 'ITR', 'STR', 'PLS', 'PLSJ', 'PSLR', 'BLR', 'PLB',
    'SLR', 'PLR', 'ALR', 'DLR', 'BLT', 'NIRC', 'FTO', 'SCC', 'SAC',
]

YEARS = list(range(2026, 1946, -1))

LOG_FILE = "/app/backend/missing_cases_search.log"
PROGRESS_FILE = "/app/backend/missing_cases_progress.json"
RESULT_FILE = "/app/backend/new_cases_found.json"

def log(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")

def get_existing_case_ids():
    """Get all case IDs already in the database"""
    client = pymongo.MongoClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    
    existing = set()
    
    # From caselaws collection
    for doc in db.caselaws.find({}, {'CaseId': 1, '_id': 0}):
        if 'CaseId' in doc and doc['CaseId']:
            existing.add(str(doc['CaseId']))
    
    # From pls_caselaws collection
    for doc in db.pls_caselaws.find({}, {'casename': 1, 'case_id': 1, '_id': 0}):
        if doc.get('casename'):
            existing.add(str(doc['casename']))
        if doc.get('case_id'):
            existing.add(str(doc['case_id']))
    
    client.close()
    return existing

def fetch_cases(year, journal):
    """Fetch case IDs for a year-journal combination"""
    try:
        result = subprocess.run([
            'curl', '-s', '--max-time', '20', '-X', 'POST',
            'https://www.pakistanlawsite.com/Login/IndexSearch',
            '-H', f'Cookie: {COOKIE}',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-H', 'X-Requested-With: XMLHttpRequest',
            '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            '-d', f'year={year}&book={journal}&court='
        ], capture_output=True, text=True, timeout=25)
        
        if 'Runtime Error' in result.stdout:
            return None  # Session expired
        
        case_ids = set(re.findall(r'casetypeid="([^"]+)"', result.stdout))
        return case_ids
    except Exception as e:
        return set()

def save_progress(new_cases, stats):
    """Save progress to file"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({
            'new_case_ids': list(new_cases),
            'count': len(new_cases),
            'stats': stats,
            'updated_at': datetime.now().isoformat()
        }, f, indent=2)

def main():
    # Clear log
    with open(LOG_FILE, 'w') as f:
        f.write("")
    
    log("=" * 70)
    log("FINDING MISSING CASE LAWS")
    log("=" * 70)
    log(f"Journals: {len(JOURNALS)}")
    log(f"Years: {YEARS[0]} to {YEARS[-1]} ({len(YEARS)} years)")
    log(f"Total combinations: {len(JOURNALS) * len(YEARS):,}")
    log("")
    
    # Get existing cases
    log("Loading existing case IDs from database...")
    existing = get_existing_case_ids()
    log(f"Found {len(existing):,} existing case IDs")
    log("")
    
    # Track new cases
    new_cases = set()
    all_found = set()
    stats = {'by_year': {}, 'by_journal': {}}
    session_valid = True
    
    start_time = time.time()
    
    for year in YEARS:
        if not session_valid:
            break
        
        year_cases = set()
        year_new = set()
        
        for journal in JOURNALS:
            cases = fetch_cases(year, journal)
            
            if cases is None:
                log(f"⚠️ Session expired at {year} {journal}")
                session_valid = False
                break
            
            if cases:
                year_cases.update(cases)
                new = cases - existing - new_cases
                if new:
                    year_new.update(new)
                    new_cases.update(new)
                    
                    if journal not in stats['by_journal']:
                        stats['by_journal'][journal] = 0
                    stats['by_journal'][journal] += len(new)
            
            time.sleep(0.1)  # Rate limiting
        
        all_found.update(year_cases)
        
        if year_cases:
            stats['by_year'][str(year)] = len(year_cases)
            log(f"  {year}: {len(year_cases):,} cases (+{len(year_new):,} new) | Total new: {len(new_cases):,}")
        
        # Save progress every 5 years
        if len(YEARS) - YEARS.index(year) % 5 == 0:
            save_progress(new_cases, stats)
    
    elapsed = time.time() - start_time
    
    log("")
    log("=" * 70)
    log("RESULTS")
    log("=" * 70)
    log(f"Existing in database: {len(existing):,}")
    log(f"Found in this scan: {len(all_found):,}")
    log(f"NEW cases discovered: {len(new_cases):,}")
    log(f"Time: {elapsed/60:.1f} minutes")
    log(f"Session valid: {session_valid}")
    
    if new_cases:
        log(f"\nTop journals with new cases:")
        sorted_journals = sorted(stats['by_journal'].items(), key=lambda x: -x[1])[:10]
        for j, c in sorted_journals:
            log(f"  {j}: {c:,}")
    
    # Save final results
    with open(RESULT_FILE, 'w') as f:
        json.dump({
            'new_case_ids': list(new_cases),
            'count': len(new_cases),
            'existing_count': len(existing),
            'total_found': len(all_found),
            'stats': stats,
            'session_valid': session_valid,
            'completed_at': datetime.now().isoformat()
        }, f, indent=2)
    
    log(f"\n💾 Results saved to {RESULT_FILE}")
    
    return len(new_cases)

if __name__ == "__main__":
    main()
