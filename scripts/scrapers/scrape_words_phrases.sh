#!/bin/bash
# Scrape words and phrases from Pakistan Legal System

BASE_URL="https://pakistanlawsite.com"
OUTPUT_DIR="data/words_phrases"

mkdir -p $OUTPUT_DIR

echo "Scraping words and phrases..."
curl -s "$BASE_URL/words-phrases" > $OUTPUT_DIR/words_phrases.html

echo "Done."
