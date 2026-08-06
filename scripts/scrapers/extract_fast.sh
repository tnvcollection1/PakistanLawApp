#!/bin/bash
# Fast extraction script

INPUT_FILE=$1
OUTPUT_DIR=$2

if [ -z "$INPUT_FILE" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: $0 <input_file> <output_dir>"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "Fast extracting from $INPUT_FILE..."
python3 scripts/extract_fast.py "$INPUT_FILE" "$OUTPUT_DIR"

echo "Done."
