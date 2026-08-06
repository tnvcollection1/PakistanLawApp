#!/bin/bash
# Fast 387k list extractor using bash + curl

COOKIE="__RequestVerificationToken=auAnT41Ci5CAu44LxcWEzzCQk4sugOPht7YpE6Eccmkk_esV056Bp8vYd00CpHT6Ec6aBHZZsRJQzJcq8u1Gp-28aZv4aBkcQos8U5-ATUo1; ASP.NET_SessionId=qafzv44ctxplfcbzy5qaxtgj"
OUTPUT="/app/backend/all_cases_387k.csv"

echo "case_id,casename,title,parties,citation,year,court,date" > $OUTPUT

BOOKS="a b c d e f g h i j k l"
TOTAL=0

for BOOK in $BOOKS; do
    echo "[$(date '+%H:%M:%S')] Processing book=$BOOK"
    
    for YEAR in $(seq 2026 -1 1950); do
        # Fetch page
        HTML=$(curl -s -X POST "https://www.pakistanlawsite.com/Login/SearchCaseLaw" \
            -H "Cookie: $COOKIE" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "year=$YEAR&book=$BOOK&searchType=caselaw" \
            --max-time 30 2>/dev/null)
        
        # Check session
        if echo "$HTML" | grep -q "Login.*Password"; then
            echo "SESSION EXPIRED!"
            exit 1
        fi
        
        # Extract casenames
        CASES=$(echo "$HTML" | grep -oP 'caseName="[^"]+"' | sed 's/caseName="//g' | sed 's/"//g' | sort -u)
        
        for CASE in $CASES; do
            echo "$CASE,$CASE,,,,$YEAR,,$(/bin/date '+%Y-%m-%d')" >> $OUTPUT
            TOTAL=$((TOTAL + 1))
        done
        
        # Get total for this year
        PAGE_TOTAL=$(echo "$HTML" | grep -oP 'total <span[^>]*>\K\d+' | head -1)
        
        # Fetch more pages if needed
        ROW=50
        while [ -n "$PAGE_TOTAL" ] && [ "$ROW" -lt "$PAGE_TOTAL" ]; do
            HTML=$(curl -s -X POST "https://www.pakistanlawsite.com/Login/SearchCaseLaw" \
                -H "Cookie: $COOKIE" \
                -H "Content-Type: application/x-www-form-urlencoded" \
                -d "year=$YEAR&book=$BOOK&searchType=caselaw&rowNo=$ROW" \
                --max-time 30 2>/dev/null)
            
            CASES=$(echo "$HTML" | grep -oP 'caseName="[^"]+"' | sed 's/caseName="//g' | sed 's/"//g' | sort -u)
            
            for CASE in $CASES; do
                echo "$CASE,$CASE,,,,$YEAR,,$(/bin/date '+%Y-%m-%d')" >> $OUTPUT
                TOTAL=$((TOTAL + 1))
            done
            
            ROW=$((ROW + 50))
            sleep 0.05
        done
        
        sleep 0.05
    done
    
    echo "[$(date '+%H:%M:%S')] Book $BOOK done | Total: $TOTAL"
done

echo "[$(date '+%H:%M:%S')] COMPLETE: $TOTAL cases"
