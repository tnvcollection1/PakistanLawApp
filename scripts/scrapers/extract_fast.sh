#!/bin/bash

# Fast extraction script using parallel processing

set -e

INPUT_FILE="${1:-}"
OUTPUT_DIR="${2:-./data/fast_extract}"
CONCURRENT="${3:-5}"

if [ -z "$INPUT_FILE" ]; then
    echo "Usage: $0 <urls_file> [output_dir] [concurrent]"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "Fast extraction: $INPUT_FILE -> $OUTPUT_DIR"
echo "Concurrent connections: $CONCURRENT"

# Create a temp directory for parallel processing
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# Function to extract a single URL
extract_url() {
    local url="$1"
    local idx="$2"
    local output="$OUTPUT_DIR/$(printf '%06d' $idx).html"
    
    curl -s -L \
        --connect-timeout 5 \
        --max-time 15 \
        -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
        "$url" -o "$output" 2>/dev/null
    
    if [ -s "$output" ]; then
        echo "OK: $url -> $output"
    else
        echo "FAIL: $url"
        rm -f "$output"
    fi
}

export -f extract_url
export OUTPUT_DIR

# Use xargs for parallel processing
cat "$INPUT_FILE" | nl -n rz | xargs -P "$CONCURRENT" -I {} bash -c '
    read -r idx url <<< "{}"
    extract_url "$url" "$idx"
'

echo "Extraction complete. Check $OUTPUT_DIR for results."
