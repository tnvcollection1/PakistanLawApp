#!/bin/bash
# Extract book from legal database

INPUT_FILE=$1
OUTPUT_DIR=$2

if [ -z "$INPUT_FILE" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: $0 <input_file> <output_dir>"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "Extracting book from $INPUT_FILE to $OUTPUT_DIR..."
python3 scripts/extract.py "$INPUT_FILE" "$OUTPUT_DIR"

echo "Done."
