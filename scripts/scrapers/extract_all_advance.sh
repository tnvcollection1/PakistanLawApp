#!/bin/bash

# Comprehensive extraction script for all advance search results

set -e

BASE_URL="https://www.pakistanlawsite.com"
OUTPUT_DIR="${1:-./data/advance_search}"
MAX_PAGES="${2:-100}"
COOKIE_JAR="/tmp/pls_cookies.txt"

mkdir -p "$OUTPUT_DIR"

echo "Starting comprehensive advance search extraction"
echo "Output directory: $OUTPUT_DIR"
echo "Max pages: $MAX_PAGES"

# Function to fetch a page
fetch_page() {
    local url="$1"
    local output="$2"
    
    curl -s -L \
        --cookie-jar "$COOKIE_JAR" \
        --cookie "$COOKIE_JAR" \
        -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
        --connect-timeout 10 \
        --max-time 30 \
        "$url" -o "$output"
    
    if [ -s "$output" ]; then
        return 0
    else
        return 1
    fi
}

# Extract case links from search results
extract_links() {
    local html_file="$1"
    
    python3 -c "
import re
import sys

with open('$html_file', 'r') as f:
    content = f.read()

# Find case detail links
links = re.findall(r'href=[\"\'](Case[^\"\']*|[0-9]+[^\"\']*))[\"\']', content)
for link in links:
    if 'case' in link.lower():
        print(link)
" | sort -u
}

# Main extraction
page=1
while [ $page -le $MAX_PAGES ]; do
    echo "Processing page $page..."
    
    # Fetch search results page
    search_url="${BASE_URL}/AdvanceSearch.aspx?page=${page}"
    html_file="$OUTPUT_DIR/page_${page}.html"
    
    if fetch_page "$search_url" "$html_file"; then
        # Extract links
        links_file="$OUTPUT_DIR/links_page_${page}.txt"
        extract_links "$html_file" > "$links_file"
        
        count=$(wc -l < "$links_file" | tr -d ' ')
        echo "Found $count links on page $page"
        
        # If no links found, might be last page
        if [ "$count" -eq 0 ]; then
            echo "No more links found. Stopping."
            break
        fi
        
        # Fetch each case
        while IFS= read -r link; do
            case_url="${BASE_URL}/${link}"
            case_id=$(echo "$link" | md5sum | cut -d' ' -f1)
            case_file="$OUTPUT_DIR/case_${case_id}.html"
            
            if [ ! -f "$case_file" ]; then
                fetch_page "$case_url" "$case_file"
                sleep 2
            fi
        done < "$links_file"
    else
        echo "Failed to fetch page $page"
    fi
    
    page=$((page + 1))
    sleep 3
done

echo "Extraction complete. Results in $OUTPUT_DIR"
