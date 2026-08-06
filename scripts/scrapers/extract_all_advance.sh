#!/bin/bash

COOKIE="__RequestVerificationToken=RZMpX_vriSVp1Le-VI-zWhyBC9jh7e3RISRCVq0LFiixwIka5bWuiH_QX8_LXvddPwdoQKiH_tMACdB9DSE8Tgzfm-vB_tHe6L4MeWO73Xc1; ASP.NET_SessionId=ugjhryc1iem0i2ikezqwv1g2"

OUTFILE="/app/backend/advance_search_all_cases.txt"
> $OUTFILE

extract_cases() {
    local court="$1"
    local total_expected="$2"
    local row_no=0
    local cases_found=0
    
    echo "Extracting from $court (expected: $total_expected)..."
    
    while [ $row_no -lt $total_expected ] && [ $row_no -lt 50000 ]; do
        # Use LoadMoreAdvanceSearch for pagination
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
          -d "court=$court&judge=&lawyer=&appelant=&nd=&rule=&act=&actSection=&act1=&act1Section=&rowNo=$row_no" \
          --max-time 60 2>&1)
        
        # Extract case IDs
        new_cases=$(echo "$result" | grep -oP 'caseName="[^"]+"' | sed 's/caseName="//g;s/"//g' | sort -u)
        count=$(echo "$new_cases" | grep -c .)
        
        if [ $count -eq 0 ]; then
            echo "  No more cases at row $row_no"
            break
        fi
        
        echo "$new_cases" >> $OUTFILE
        cases_found=$((cases_found + count))
        echo "  Row $row_no: +$count cases (total: $cases_found)"
        
        row_no=$((row_no + 70))
        sleep 0.2
    done
    
    echo "  Finished $court: $cases_found cases extracted"
}

# Extract from major courts
extract_cases "SUPREME-COURT" 99069
extract_cases "LAHORE-HIGH-COURT" 136922
extract_cases "KARACHI" 90464
extract_cases "PESHAWAR-HIGH-COURT" 25777
extract_cases "QUETTA" 10301
extract_cases "ISLAMABAD" 5651
extract_cases "BALOCHISTAN" 10742
extract_cases "FEDERAL-SHARIAT-COURT" 4460
extract_cases "APPELLATE" 22416
extract_cases "TRIBUNAL" 33799

# Deduplicate
echo ""
echo "Deduplicating..."
sort -u $OUTFILE > /app/backend/advance_search_unique.txt
total=$(wc -l < /app/backend/advance_search_unique.txt)
echo "Total unique cases: $total"
