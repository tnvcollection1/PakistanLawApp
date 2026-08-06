#!/bin/bash
# Fetch content from legal databases

BASE_URL="https://pakistanlawsite.com"
OUTPUT_DIR="data/content"

mkdir -p $OUTPUT_DIR

echo "Fetching content..."
curl -s "$BASE_URL/content" > $OUTPUT_DIR/content.html

echo "Done."
