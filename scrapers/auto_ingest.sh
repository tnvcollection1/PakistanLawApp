#!/bin/bash
cd /var/www/pakistanlawapp
LOG="/var/log/court_ingestion.log"
echo "$(date): Starting auto-ingestion..." >> $LOG
python3 scrapers/ingest_courts.py >> $LOG 2>&1
echo "$(date): Ingestion complete" >> $LOG
