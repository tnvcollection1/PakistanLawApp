#!/bin/bash

# Script to extract book content from Pakistan Legal Sources

set -e

URL="${1:-}"
OUTPUT_DIR="${2:-./data/books}"

if [ -z "$URL" ]; then
    echo "Usage: $0 <url> [output_dir]"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "Extracting book from: $URL"

# Fetch the page content
curl -s -L "$URL" -o /tmp/book_page.html

# Extract title
TITLE=$(grep -oP '(?<=<title>).*?(?=</title>)' /tmp/book_page.html || echo "unknown")

# Extract content
python3 -c "
import sys
from bs4 import BeautifulSoup

with open('/tmp/book_page.html', 'r') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

# Remove script and style elements
for script in soup(['script', 'style']):
    script.decompose()

# Extract text
text = soup.get_text()
lines = (line.strip() for line in text.splitlines())
chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
text = '\n'.join(chunk for chunk in chunks if chunk)

print(text)
" > "$OUTPUT_DIR/${TITLE}.txt"

echo "Extraction complete. Output: $OUTPUT_DIR/${TITLE}.txt"
