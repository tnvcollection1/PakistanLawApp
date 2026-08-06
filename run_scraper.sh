#!/bin/bash
# run_scraper.sh — Run case law scrapers

cd /var/www/pakistanlawapp/scripts/scrapers

# Run all scrapers
for scraper in *.py; do
    echo "Running $scraper..."
    python3 "$scraper"
done

echo "All scrapers completed."
