#!/bin/bash

# Script to scrape Pakistan Code content

set -e

BASE_URL="${1:-https://pakistancode.gov.pk}"
OUTPUT_DIR="${2:-./data/pakistan_code}"

mkdir -p "$OUTPUT_DIR"

echo "Scraping Pakistan Code from: $BASE_URL"

# Get main page
curl -s -L "$BASE_URL" -o "$OUTPUT_DIR/main.html"

# Extract links to laws
python3 -c "
import re

with open('$OUTPUT_DIR/main.html', 'r') as f:
    content = f.read()

links = re.findall(r'href=[\"\'](.*?)[\"\']', content)
for link in links:
    if 'act' in link.lower() or 'ordinance' in link.lower():
        print(link)
" | sort -u > "$OUTPUT_DIR/law_links.txt"

echo "Found $(wc -l < '$OUTPUT_DIR/law_links.txt') law links"

# Download each law
while IFS= read -r link; do
    if [[ "$link" != http* ]]; then
        link="${BASE_URL}${link}"
    fi
    
    filename=$(basename "$link" | cut -d'?' -f1)
    if [ -z "$filename" ]; then
        filename=$(echo "$link" | md5sum | cut -d' ' -f1).html
    fi
    
    echo "Downloading: $link -> $OUTPUT_DIR/$filename"
    curl -s -L "$link" -o "$OUTPUT_DIR/$filename" || echo "Failed: $link"
done < "$OUTPUT_DIR/law_links.txt"

echo "Scraping complete. Output: $OUTPUT_DIR"
