#!/usr/bin/env python3
"""
Numeric Case ID Collector - Finds all numeric case IDs from various pages
"""
import subprocess
import re
import json
from datetime import datetime

COOKIE = "ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj; __RequestVerificationToken=bC2SxKAWEsfNzmsxm-AYKKZcfTmzOA_A_xKIB10bKcYf6Nl6nplba8FAPIhYoalWIYJvEMksYzj0ukpCReoXe10NiNIfNzhTyDmCl1cMymA1"

# Pages that might have case IDs
PAGES = [
    "/Login/WordsAndPhrases?type=words",
    "/Login/LegalTerms",
    "/Login/Maxim?type=maxim",
    "/Login/HeadNotes",
    "/Login/Topics",
    "/Login/Dictionary",
]

# Alphabet for paginated content
ALPHABETS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

all_numeric_ids = set()
all_alpha_ids = set()


def fetch_page(url):
    """Fetch a page and extract case IDs"""
    try:
        result = subprocess.run([
            'curl', '-s', '--max-time', '30',
            f'https://www.pakistanlawsite.com{url}',
            '-H', f'Cookie: {COOKIE}',
            '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        ], capture_output=True, text=True, timeout=35)
        
        # Find all case type IDs
        ids = re.findall(r'casetypeid="([^"]+)"', result.stdout)
        return ids
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return []


def main():
    global all_numeric_ids, all_alpha_ids
    
    print("=" * 70)
    print("📚 NUMERIC CASE ID COLLECTOR")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Fetch main pages
    for page in PAGES:
        print(f"Fetching {page}...")
        ids = fetch_page(page)
        for id in ids:
            if id.isdigit():
                all_numeric_ids.add(id)
            else:
                all_alpha_ids.add(id)
        print(f"  Found {len(ids)} IDs ({len([i for i in ids if i.isdigit()])} numeric)")
    
    # Try alphabet-based searches for Words & Phrases
    print("\nSearching Words & Phrases by letter...")
    for letter in ALPHABETS:
        url = f"/Login/WordsAndPhrasesSearch?letter={letter}"
        ids = fetch_page(url)
        for id in ids:
            if id.isdigit():
                all_numeric_ids.add(id)
            else:
                all_alpha_ids.add(id)
        if ids:
            print(f"  {letter}: {len(ids)} IDs")
    
    # Try alphabet-based searches for Legal Terms
    print("\nSearching Legal Terms by letter...")
    for letter in ALPHABETS:
        url = f"/Login/LegalTermsSearch?letter={letter}"
        ids = fetch_page(url)
        for id in ids:
            if id.isdigit():
                all_numeric_ids.add(id)
            else:
                all_alpha_ids.add(id)
        if ids:
            print(f"  {letter}: {len(ids)} IDs")
    
    # Summary
    print()
    print("=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"Numeric case IDs found: {len(all_numeric_ids):,}")
    print(f"Alphanumeric case IDs found: {len(all_alpha_ids):,}")
    print(f"Total unique: {len(all_numeric_ids) + len(all_alpha_ids):,}")
    
    # Save results
    with open('/tmp/numeric_case_ids.json', 'w') as f:
        json.dump(list(all_numeric_ids), f)
    with open('/tmp/alpha_case_ids.json', 'w') as f:
        json.dump(list(all_alpha_ids), f)
    
    print(f"\n💾 Saved to /tmp/numeric_case_ids.json and /tmp/alpha_case_ids.json")


if __name__ == "__main__":
    main()
