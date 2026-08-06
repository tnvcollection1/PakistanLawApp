#!/bin/bash
# Run Advance Extraction - Batch script for advanced case extraction

echo "Starting advance extraction..."

# Extract cases
python scripts/scrapers/extract_all_cases.py

# Fetch missing content
python scripts/scrapers/fetch_missing_content.py

# Enrich data
python scripts/scrapers/enrich_caselaw_data.py data/cases.json data/cases_enriched.json

# Index in Meilisearch
python scrapers/index_meilisearch.py data/cases_enriched.json

echo "Advance extraction complete!"
