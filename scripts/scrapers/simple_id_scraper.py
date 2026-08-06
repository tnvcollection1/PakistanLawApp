#!/usr/bin/env python3
"""
SIMPLE ID Pattern Scraper - Just checks IDs directly on PLS
No index search - pure ID generation and checking
"""
import subprocess
import sys
import time
from datetime import datetime
from pymongo import MongoClient

INSTANCE = int(sys.argv[1]) if len(sys.argv) > 1 else 1
TOTAL_INSTANCES = int(sys.argv[2]) if len(sys.argv) > 2 else 1

COOKIE = "ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj; __RequestVerificationToken=bC2SxKAWEsfNzmsxm-AYKKZcfTmzOA_A_xKIB10bKcYf6Nl6nplba8FAPIhYoalWIYJvEMksYzj0ukpCReoXe10NiNIfNzhTyDmCl1cMymA1"

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

# Courts and their likely max case numbers per year
COURTS = ['S', 'L', 'K', 'P', 'Q', 'I', 'C', 'F']
MAX_NUM = 5000  # Check up to 5000 per year/court


def check_pls(case_id):
    """Check if case exists on PLS - returns content or None"""
    try:
        result = subprocess.run([
            'curl', '-s', '--max-time', '8', '-X', 'POST',
            'https://www.pakistanlawsite.com/Login/GetCaseFile',
            '-H', f'Cookie: {COOKIE}',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-d', f'caseName={case_id}&headNotes=0'
        ], capture_output=True, text=True, timeout=12)
        
        r = result.stdout.strip()
        
        # Session expired
        if 'Login' in r and 'Password' in r:
            return "EXPIRED"
        
        # "1" = doesn't exist
        if r == '"1"' or r == '1' or len(r) < 50:
            return None
        
        # Has content = exists
        return r if len(r) > 100 else None
    except:
        return None


def main():
    print(f"[{INSTANCE}/{TOTAL_INSTANCES}] Simple ID Scraper", flush=True)
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    col = db['pls_caselaws']
    
    # Distribute years
    years = list(range(2026, 1946, -1))
    my_years = [y for i, y in enumerate(years) if i % TOTAL_INSTANCES == (INSTANCE - 1)]
    
    print(f"[{INSTANCE}] Years: {my_years[:3]}...{my_years[-2:]}", flush=True)
    
    found = 0
    checked = 0
    
    for year in my_years:
        for court in COURTS:
            misses = 0
            
            for num in range(1, MAX_NUM + 1):
                case_id = f"{year}{court}{num}"
                
                # Skip if in DB
                if col.find_one({"case_id": case_id}):
                    misses = 0
                    continue
                
                checked += 1
                content = check_pls(case_id)
                
                if content == "EXPIRED":
                    print(f"[{INSTANCE}] ⚠️ SESSION EXPIRED! Found {found} new", flush=True)
                    client.close()
                    return
                
                if content:
                    col.insert_one({
                        "case_id": case_id,
                        "year": str(year),
                        "court_code": court,
                        "full_content": content,
                        "source": "id_pattern_scraper",
                        "scraped_at": datetime.utcnow().isoformat()
                    })
                    found += 1
                    misses = 0
                    print(f"[{INSTANCE}] ✅ {case_id} | NEW: {found}", flush=True)
                else:
                    misses += 1
                
                # Skip to next court after 50 misses
                if misses >= 50:
                    break
                
                time.sleep(0.2)
            
            if found > 0 or checked % 500 == 0:
                print(f"[{INSTANCE}] {year}{court} checked | Found: {found} | Checked: {checked}", flush=True)
    
    print(f"\n[{INSTANCE}] DONE! Found {found} new cases", flush=True)
    client.close()


if __name__ == "__main__":
    main()
