#!/bin/bash

# Script to fetch content from a URL using curl with retries

set -e

URL="${1:-}"
OUTPUT="${2:-/tmp/fetched_content.html}"
MAX_RETRIES=3
RETRY_DELAY=5

if [ -z "$URL" ]; then
    echo "Usage: $0 <url> [output_file]"
    exit 1
fi

fetch_with_retries() {
    local attempt=1
    
    while [ $attempt -le $MAX_RETRIES ]; do
        echo "Attempt $attempt of $MAX_RETRIES..."
        
        if curl -s -L \
            --connect-timeout 10 \
            --max-time 30 \
            -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" \
            "$URL" -o "$OUTPUT"; then
            
            # Check if output has content
            if [ -s "$OUTPUT" ]; then
                echo "Success! Content saved to $OUTPUT"
                return 0
            fi
        fi
        
        echo "Attempt $attempt failed. Retrying in ${RETRY_DELAY}s..."
        sleep $RETRY_DELAY
        attempt=$((attempt + 1))
    done
    
    echo "Failed to fetch $URL after $MAX_RETRIES attempts"
    return 1
}

# Main execution
echo "Fetching: $URL"
fetch_with_retries
