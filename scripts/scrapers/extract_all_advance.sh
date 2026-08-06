#!/bin/bash
# Extract all advance sheets

INPUT_DIR=$1
OUTPUT_DIR=$2

if [ -z "$INPUT_DIR" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: $0 <input_dir> <output_dir>"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "Extracting all advance sheets from $INPUT_DIR to $OUTPUT_DIR..."
for file in "$INPUT_DIR"/*.pdf; do
    echo "Processing: $file"
    python3 scripts/extract.py "$file" "$OUTPUT_DIR"
done

echo "Done."
