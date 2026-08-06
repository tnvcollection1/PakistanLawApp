#!/usr/bin/env python3
"""
Turbo List Scraper - High performance batch scraping with async
"""
import asyncio
import aiohttp
import json
import time
import subprocess
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

COOKIE = 'ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj; __RequestVerificationToken=cgGcIYoNV7nI6OcGKHg1CT9MoWn8iaRUpmxN-4q7PjvEfhtYG78RWELK-UA5wM8CZE0lSLjYOX-EL-aofCi3Zth-khKoUOn8cHY7Pbuzpt01'

# Generate all year-journal combinations
YEARS = list(range(2026, 1945, -1))
JOURNALS = [
    'PLD', 'CLC', 'CLCN', 'MLD', 'YLR', 'YLRN', 'SCMR', 'PCRLJ', 'PCRLJN',
    'PTD', 'PLC', 'PLCN', 'PLC(CS)', 'PLC(CS)N', 'PLJ', 'PSC', 'KLR', 'NLR', 'GBLR', 'BLD',
    'NIRC', 'FTO', 'SCC', 'SAC', 'CEST', 'CST', 'IRAT',
    'LAT-SINDH', 'LAT-PUNJAB', 'LAT-NWFP', 'LAT-BALOCHISTAN', 'LAT-WP',
    'LC-PUNJAB', 'LC-SINDH', 'LC-NWFP', 'LC-BALOCHISTAN', 'LC-WP',
    'BR-PUNJAB', 'BR-SINDH', 'BR-NWFP', 'BR-BALOCHISTAN', 'BR-WP',
    'ET-PUNJAB', 'ET-SINDH', 'ET-NWFP', 'ET-BALOCHISTAN',
    'ST-PUNJAB', 'ST-SINDH', 'ST-NWFP',
    'HCAJK', 'SCAJK', 'SUPAJK',
    'FSC', 'FC',
    'IAT-WP', 'IT-K', 'IT-L',
    'PLAT', 'SLAT', 'BLT', 'EPIC', 'WPIC', 'PCIC',
    'S-INDIA', 'M-INDIA', 'K-INDIA', 'B-INDIA', 'C-INDIA', 'A-INDIA',
    'MP-INDIA', 'PH-INDIA', 'G-INDIA', 'AP-INDIA', 'D-INDIA', 'R-INDIA',
    'PT-INDIA', 'GH-INDIA', 'KR-INDIA', 'MY-INDIA', 'O-INDIA', 'AN-INDIA', 'HP-INDIA'
]

all_case_ids = set()


def fetch_cases_sync(year, journal):
    """Fetch case IDs synchronously using curl"""
    try:
        result = subprocess.run([
            'curl', '-s', '--max-time', '20', '-X', 'POST',
            'https://www.pakistanlawsite.com/Login/IndexSearch',
            '-H', f'Cookie: {COOKIE}',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-H', 'X-Requested-With: XMLHttpRequest',
            '-d', f'year={year}&book={journal}&court='
        ], capture_output=True, text=True, timeout=25)
        
        case_ids = re.findall(r'casetypeid="([^"]+)"', result.stdout)
        return case_ids
    except Exception:
        return []


def process_batch(batch):
    """Process a batch of year-journal combinations"""
    batch_cases = set()
    for year, journal in batch:
        cases = fetch_cases_sync(year, journal)
        if cases:
            batch_cases.update(cases)
    return batch_cases


def main():
    global all_case_ids
    
    # Generate all combinations
    combinations = [(year, journal) for year in YEARS for journal in JOURNALS]
    
    # Split into batches
    batch_size = 50
    batches = [combinations[i:i + batch_size] for i in range(0, len(combinations), batch_size)]
    
    print("=" * 70)
    print("🔥 TURBO LIST SCRAPER - Parallel Batch Processing")
    print("=" * 70)
    print(f"Total combinations: {len(combinations):,}")
    print(f"Batch size: {batch_size}")
    print(f"Number of batches: {len(batches)}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    start_time = time.time()
    completed = 0
    
    # Process batches with thread pool
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_batch, batch): i for i, batch in enumerate(batches)}
        
        for future in as_completed(futures):
            batch_cases = future.result()
            all_case_ids.update(batch_cases)
            
            completed += 1
            if completed % 10 == 0:
                print(f"  Progress: {completed}/{len(batches)} batches | Total unique cases: {len(all_case_ids):,}")
    
    elapsed = time.time() - start_time
    
    print()
    print("=" * 70)
    print("🏁 TURBO SCRAPING COMPLETE!")
    print("=" * 70)
    print(f"Total unique cases found: {len(all_case_ids):,}")
    print(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
    print(f"Rate: {len(all_case_ids)/elapsed:.0f} cases/second")
    
    # Save results
    with open('/tmp/turbo_case_ids.json', 'w') as f:
        json.dump(list(all_case_ids), f)
    print(f"\n💾 Saved to /tmp/turbo_case_ids.json")


if __name__ == "__main__":
    main()
