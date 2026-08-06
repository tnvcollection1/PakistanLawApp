#!/bin/bash
# Extract cases from "court" keyword search to find missing cases

COOKIE="__RequestVerificationToken=RZMpX_vriSVp1Le-VI-zWhyBC9jh7e3RISRCVq0LFiixwIka5bWuiH_QX8_LXvddPwdoQKiH_tMACdB9DSE8Tgzfm-vB_tHe6L4MeWO73Xc1; ASP.NET_SessionId=ugjhryc1iem0i2ikezqwv1g2"

OUTFILE="/app/backend/court_keyword_cases.txt"
LOGFILE="/app/backend/court_extraction.log"
> $OUTFILE

log() {
    echo "$(date '+%H:%M:%S') $1" | tee -a $LOGFILE
}

log "Starting 'court' keyword extraction (expected: 194,417 cases)"

row_no=0
total_found=0
consecutive_empty=0
max_rows=200000  # Safety limit

while [ $row_no -lt $max_rows ] && [ $consecutive_empty -lt 5 ]; do
    if [ $row_no -eq 0 ]; then
        URL="https://www.pakistanlawsite.com/Login/AdvanceSearch"
    else
        URL="https://www.pakistanlawsite.com/Login/LoadMoreAdvanceSearch"
    fi
    
    result=$(curl -s -X POST "$URL" \
      -H "Cookie: $COOKIE" \
      -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
      -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
      -H "X-Requested-With: XMLHttpRequest" \
      -d "court=&judge=&lawyer=&appelant=&nd=court&rule=&act=&actSection=&act1=&act1Section=&rowNo=$row_no" \
      --max-time 90 2>&1)
    
    # Check for session expiry
    if echo "$result" | grep -q "HandleError\|Object moved"; then
        log "SESSION EXPIRED at row $row_no (total found: $total_found)"
        break
    fi
    
    # Extract case IDs
    new_cases=$(echo "$result" | grep -oP 'caseName="[^"]+"' | sed 's/caseName="//g;s/"//g')
    count=$(echo "$new_cases" | grep -c . 2>/dev/null || echo 0)
    
    if [ "$count" -eq 0 ] || [ -z "$new_cases" ]; then
        consecutive_empty=$((consecutive_empty + 1))
    else
        consecutive_empty=0
        echo "$new_cases" >> $OUTFILE
        total_found=$((total_found + count))
    fi
    
    # Log progress every 1000 rows
    if [ $((row_no % 1400)) -eq 0 ]; then
        log "Row $row_no: $total_found cases extracted"
    fi
    
    row_no=$((row_no + 70))
    sleep 0.1
done

log "Extraction finished. Total extracted: $total_found"

# Deduplicate
log "Deduplicating..."
sort -u $OUTFILE > /app/backend/court_keyword_unique.txt
unique=$(wc -l < /app/backend/court_keyword_unique.txt)
log "Unique cases: $unique"

# Compare with existing
log "Comparing with IndexSearch list..."
python3 << 'PYTHON'
import json

# Load existing
with open('/app/backend/complete_caselist.json') as f:
    existing = set(json.load(f))
print(f"IndexSearch cases: {len(existing)}")

# Load new
with open('/app/backend/court_keyword_unique.txt') as f:
    court_kw = set(line.strip() for line in f if line.strip())
print(f"Court keyword cases: {len(court_kw)}")

# Find new
new_cases = court_kw - existing
print(f"NEW cases: {len(new_cases)}")

if new_cases:
    with open('/app/backend/new_cases_from_court_kw.json', 'w') as f:
        json.dump(sorted(list(new_cases)), f, indent=2)
    print(f"Saved to new_cases_from_court_kw.json")
    
    # Update master list
    all_cases = existing | court_kw
    with open('/app/backend/complete_caselist_v2.json', 'w') as f:
        json.dump(sorted(list(all_cases)), f)
    print(f"Updated list: {len(all_cases)} total")
    
    print("\nSample new cases:")
    for c in sorted(list(new_cases))[:30]:
        print(f"  {c}")
PYTHON
