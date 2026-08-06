#!/usr/bin/env python3
"""
Expanded Case Finder - Discovers ALL cases from Pakistan Law Site
Uses multiple methods: IndexSearch, CitationSearch, and various journal codes
"""
import subprocess
import re
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Fresh cookies
COOKIE = "ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj; __RequestVerificationToken=bC2SxKAWEsfNzmsxm-AYKKZcfTmzOA_A_xKIB10bKcYf6Nl6nplba8FAPIhYoalWIYJvEMksYzj0ukpCReoXe10NiNIfNzhTyDmCl1cMymA1"

# Extended journal list (includes all known journals)
JOURNALS = [
    # Primary journals
    'PLD', 'CLC', 'CLCN', 'MLD', 'YLR', 'YLRN', 'SCMR', 'PCRLJ', 'PCRLJN', 
    'PTD', 'PLC', 'PLCN', 'PLC(CS)', 'PLC(CS)N', 'PLJ', 'PSC', 'KLR', 'NLR', 'GBLR', 'BLD',
    # Tribunal journals
    'NIRC', 'FTO', 'SCC', 'SAC', 'CEST', 'CST', 'IRAT',
    # Court specific
    'LAT-SINDH', 'LAT-PUNJAB', 'LAT-NWFP', 'LAT-BALOCHISTAN', 'LAT-WP',
    'LC-PUNJAB', 'LC-SINDH', 'LC-NWFP', 'LC-BALOCHISTAN', 'LC-WP',
    'BR-PUNJAB', 'BR-SINDH', 'BR-NWFP', 'BR-BALOCHISTAN', 'BR-WP',
    'ET-PUNJAB', 'ET-SINDH', 'ET-NWFP', 'ET-BALOCHISTAN',
    'ST-PUNJAB', 'ST-SINDH', 'ST-NWFP',
    # AJK
    'HCAJK', 'SCAJK', 'SUPAJK',
    # Federal courts
    'FSC', 'FC',
    # Tax tribunals
    'IAT-WP', 'IT-K', 'IT-L',
    # Other
    'PLAT', 'SLAT', 'BLT', 'EPIC', 'WPIC', 'PCIC',
    # Indian case references
    'S-INDIA', 'M-INDIA', 'K-INDIA', 'B-INDIA', 'C-INDIA', 'A-INDIA',
    'MP-INDIA', 'PH-INDIA', 'G-INDIA', 'AP-INDIA', 'D-INDIA', 'R-INDIA',
    'PT-INDIA', 'GH-INDIA', 'KR-INDIA', 'MY-INDIA', 'O-INDIA', 'AN-INDIA', 'HP-INDIA'
]

# Year range
YEARS = list(range(2026, 1930, -1))  # Extended range to 1930

all_case_ids = set()
found_by_method = {"index_search": set(), "citation_search": set()}


def fetch_index_search(year, journal):
    """Fetch case IDs using IndexSearch API"""
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
        
        case_ids = re.findall(r'casetypeid="([^"]+)"', result.stdout)
        return case_ids
    except Exception:
        return []


def fetch_citation_search(journal, year, page=1):
    """Fetch case IDs using CitationSearch API"""
    try:
        result = subprocess.run([
            'curl', '-s', '--max-time', '20', '-X', 'POST',
            'https://www.pakistanlawsite.com/Login/CitationSearch',
            '-H', f'Cookie: {COOKIE}',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-H', 'X-Requested-With: XMLHttpRequest',
            '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            '-d', f'citation={journal}&year={year}&page={page}'
        ], capture_output=True, text=True, timeout=25)
        
        case_ids = re.findall(r'casetypeid="([^"]+)"', result.stdout)
        return case_ids
    except Exception:
        return []


def process_year_journal(args):
    """Process a single year-journal combination"""
    year, journal = args
    cases = fetch_index_search(year, journal)
    return (year, journal, cases)


def main():
    global all_case_ids, found_by_method
    
    # Load existing case IDs
    try:
        with open('complete_case_ids.json', 'r') as f:
            existing = set(json.load(f))
        print(f"Loaded {len(existing):,} existing case IDs")
    except:
        existing = set()
    
    print("=" * 70)
    print("🔍 EXPANDED CASE FINDER - Pakistan Law Site")
    print("=" * 70)
    print(f"Scanning {len(YEARS)} years × {len(JOURNALS)} journals = {len(YEARS)*len(JOURNALS):,} combinations")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create all year-journal combinations
    combinations = [(year, journal) for year in YEARS for journal in JOURNALS]
    
    # Process with thread pool
    completed = 0
    batch_size = 100
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(process_year_journal, combo): combo for combo in combinations}
        
        for future in as_completed(futures):
            year, journal, cases = future.result()
            new_cases = set(cases) - all_case_ids - existing
            all_case_ids.update(cases)
            found_by_method["index_search"].update(cases)
            
            completed += 1
            if completed % batch_size == 0:
                total_new = len(all_case_ids - existing)
                print(f"  Progress: {completed:,}/{len(combinations):,} | Found: {len(all_case_ids):,} | New: {total_new:,}")
            
            time.sleep(0.1)  # Small delay
    
    # Calculate statistics
    total_new = len(all_case_ids - existing)
    combined = all_case_ids | existing
    
    print()
    print("=" * 70)
    print("📊 EXPANDED SEARCH COMPLETE!")
    print("=" * 70)
    print(f"Total case IDs in this search: {len(all_case_ids):,}")
    print(f"Previously known IDs: {len(existing):,}")
    print(f"NEW case IDs found: {total_new:,}")
    print(f"COMBINED TOTAL: {len(combined):,}")
    
    # Save expanded list
    with open('/tmp/expanded_case_ids.json', 'w') as f:
        json.dump(list(combined), f)
    print(f"\n💾 Saved combined list to /tmp/expanded_case_ids.json")
    
    # Save just new IDs
    if total_new > 0:
        with open('/tmp/new_case_ids.json', 'w') as f:
            json.dump(list(all_case_ids - existing), f)
        print(f"💾 Saved {total_new:,} new IDs to /tmp/new_case_ids.json")
    
    # Show breakdown by journal prefix
    print("\n📚 New cases by journal prefix (top 20):")
    new_ids = all_case_ids - existing
    prefixes = {}
    for cid in new_ids:
        match = re.match(r'\d{4}([A-Z\-]+)', cid)
        if match:
            p = match.group(1)
            prefixes[p] = prefixes.get(p, 0) + 1
    
    for prefix, count in sorted(prefixes.items(), key=lambda x: -x[1])[:20]:
        print(f"  {prefix}: {count:,}")


if __name__ == "__main__":
    main()
