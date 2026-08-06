#!/bin/bash
# Run advanced extraction scripts

echo "Starting advanced extraction..."

# Create output directory
mkdir -p output

# Run extractors
echo "Running case list extraction..."
python3 scripts/scrapers/case_list_scraper.py

echo "Running content extraction..."
python3 scripts/scrapers/mass_content_scraper.py

echo "Running statute extraction..."
python3 scripts/scrapers/scrape_plsbeta_statute_sections.py

echo "Running legal terms extraction..."
python3 scripts/scrapers/scrape_legal_terms_complete.py

echo "All extractions complete!"
echo "Results saved to output/ directory"
