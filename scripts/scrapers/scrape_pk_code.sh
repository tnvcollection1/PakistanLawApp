#!/bin/bash
# Scrape Pakistan Code

BASE_URL="https://pakistancode.gov.pk"
OUTPUT_DIR="data/pk_code"

mkdir -p $OUTPUT_DIR

echo "Scraping Pakistan Code from $BASE_URL..."
curl -s "$BASE_URL" > $OUTPUT_DIR/index.html

echo "Done."
