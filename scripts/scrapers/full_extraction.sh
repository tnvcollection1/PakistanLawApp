#!/bin/bash
# Comprehensive extraction with correct headers

COOKIE="ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj; __RequestVerificationToken=cgGcIYoNV7nI6OcGKHg1CT9MoWn8iaRUpmxN-4q7PjvEfhtYG78RWELK-UA5wM8CZE0lSLjYOX-EL-aofCi3Zth-khKoUOn8cHY7Pbuzpt01; x-hng=lang=en-US&domain=www.pakistanlawsite.com"

UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"

OUTFILE="/app/backend/full_extraction.txt"
LOGFILE="/app/backend/full_extraction.log"
> $OUTFILE

log() {
    echo "$(date '+%H:%M:%S') $1" | tee -a $LOGFILE
}

extract_page() {
    local row=$1
    local keyword="$2"
    
    if [ $row -eq 0 ]; then
        URL="https://www.pakistanlawsite.com/Login/AdvanceSearch"
    else
        URL="https://www.pakistanlawsite.com/Login/LoadMoreAdvanceSearch"
    fi
    
    curl -s -X POST "$URL" \
      -H "Cookie: $COOKIE" \
      -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
      -H "User-Agent: $UA" \
      -H "X-Requested-With: XMLHttpRequest" \
      -H "Origin: https://www.pakistanlawsite.com" \
      -H "Referer: https://www.pakistanlawsite.com/Login/Check" \
      -H "sec-ch-ua-platform: \"macOS\"" \
      -d "court=&judge=&lawyer=&appelant=&nd=$keyword&rule=&act=&actSection=&act1=&act1Section=&rowNo=$row" \
      --max-time 60 2>&1
}

log "Starting 'court' keyword extraction (194,417 expected)..."

row=0
total=0
empty_streak=0

while [ $row -lt 200000 ] && [ $empty_streak -lt 5 ]; do
    result=$(extract_page $row "court")
    
    # Check for session expiry
    if echo "$result" | grep -q "HandleError\|Object moved"; then
        log "SESSION EXPIRED at row $row"
        break
    fi
    
    # Extract cases
    cases=$(echo "$result" | grep -oP 'caseName="[^"]+"' | sed 's/caseName="//g;s/"//g')
    count=$(echo "$cases" | grep -c . 2>/dev/null || echo 0)
    
    if [ "$count" -eq 0 ]; then
        empty_streak=$((empty_streak + 1))
    else
        empty_streak=0
        echo "$cases" >> $OUTFILE
        total=$((total + count))
    fi
    
    # Progress every 20 pages
    if [ $((row % 1400)) -eq 0 ]; then
        log "Row $row: $total cases extracted"
    fi
    
    row=$((row + 70))
    sleep 0.05
done

log "Extraction done. Total: $total"

# Deduplicate
log "Deduplicating..."
sort -u $OUTFILE > /app/backend/full_unique.txt
unique=$(wc -l < /app/backend/full_unique.txt)
log "Unique cases: $unique"

# Compare
log "Comparing with IndexSearch..."
python3 << 'PYTHON'
import json

with open('/app/backend/complete_caselist.json') as f:
    existing = set(json.load(f))

with open('/app/backend/full_unique.txt') as f:
    extracted = set(line.strip() for line in f if line.strip())

new_cases = extracted - existing
in_both = extracted & existing

print(f"IndexSearch: {len(existing)}")
print(f"Extracted: {len(extracted)}")
print(f"Overlap: {len(in_both)}")
print(f"NEW cases: {len(new_cases)}")

if new_cases:
    with open('/app/backend/new_cases_final.json', 'w') as f:
        json.dump(sorted(list(new_cases)), f, indent=2)
    print("Saved to new_cases_final.json")
    
    # Update master list
    all_cases = existing | extracted
    with open('/app/backend/complete_caselist_v2.json', 'w') as f:
        json.dump(sorted(list(all_cases)), f)
    print(f"Updated list: {len(all_cases)} total")
    
    print("\nNew cases sample:")
    for c in sorted(list(new_cases))[:30]:
        print(f"  {c}")
PYTHON
