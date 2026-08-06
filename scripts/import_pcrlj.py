#!/usr/bin/env python3
"""
Import PCRLJ (Pakistan Criminal Law Journal) data into MongoDB.
This script processes CSV exports from PCRLJ and imports them
to the caselaws collection with normalization.

Usage: python3 scripts/import_pcrlj.py --csv /path/to/pcrlj_export.csv [--db DATABASE]
"""

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional

from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError

MONGO_URI = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DEFAULT_DB = os.environ.get("DB_NAME", "test_database")


def parse_date(date_str: str) -> Optional[str]:
    """Parse various date formats to ISO string."""
    if not date_str:
        return None
    patterns = [
        (r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})', lambda m: f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"),
        (r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"),
    ]
    for pat, fmt in patterns:
        m = re.match(pat, date_str.strip())
        if m:
            return fmt(m)
    year_match = re.search(r'\b(\d{4})\b', date_str)
    if year_match:
        return f"{year_match.group(1)}-01-01"
    return None


def normalize_pcrlj_row(row: Dict) -> Dict:
    """Convert a PCRLJ CSV row to normalized case format."""
    parties = row.get("parties", row.get("title", ""))
    petitioner, respondent = "", ""
    if " vs " in parties:
        petitioner, respondent = parties.split(" vs ", 1)
    elif " VS " in parties:
        petitioner, respondent = parties.split(" VS ", 1)

    return {
        "source": "pcrlj",
        "case_id": row.get("case_id", row.get("citation", "")).replace(" ", "_"),
        "citation": row.get("citation", ""),
        "title": row.get("title", ""),
        "year": int(row.get("year", 0)) if row.get("year", "").isdigit() else None,
        "court": row.get("court", ""),
        "judge": row.get("judge", ""),
        "date": parse_date(row.get("date", "")),
        "petitioner": petitioner.strip(),
        "respondent": respondent.strip(),
        "parties": parties,
        "headnotes": row.get("headnotes", row.get("head_notes", ""))[:2000],
        "judgment_text": row.get("judgment", row.get("text", ""))[:50000],
        "status": row.get("status", "undecided"),
        "topic": row.get("topic", ""),
        "subtopic": row.get("subtopic", ""),
        "imported_at": datetime.now().isoformat(),
        "url": row.get("url", ""),
    }


def import_csv(csv_path: str, db_name: str) -> Dict:
    """Import PCRLJ CSV into MongoDB."""
    client = MongoClient(MONGO_URI)
    db = client[db_name]
    collection = db["caselaws"]

    imported = 0
    updated = 0
    errors = 0
    skipped = 0

    operations = []

    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                normalized = normalize_pcrlj_row(row)
                case_id = normalized["case_id"]
                if not case_id:
                    skipped += 1
                    continue

                operations.append(
                    UpdateOne(
                        {"case_id": case_id},
                        {"$set": normalized},
                        upsert=True,
                    )
                )

                if len(operations) >= 1000:
                    result = collection.bulk_write(operations)
                    imported += result.upserted_count
                    updated += result.modified_count
                    operations = []

            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"Error processing row: {e}", file=sys.stderr)

    if operations:
        try:
            result = collection.bulk_write(operations)
            imported += result.upserted_count
            updated += result.modified_count
        except BulkWriteError as e:
            errors += len(e.details.get("writeErrors", []))
            print(f"Bulk write error: {e}", file=sys.stderr)

    client.close()

    return {
        "imported": imported,
        "updated": updated,
        "errors": errors,
        "skipped": skipped,
        "total": imported + updated + skipped,
    }


def main():
    parser = argparse.ArgumentParser(description="Import PCRLJ data to MongoDB")
    parser.add_argument("--csv", required=True, help="Path to PCRLJ CSV export")
    parser.add_argument("--db", default=DEFAULT_DB, help="MongoDB database name")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"File not found: {args.csv}", file=sys.stderr)
        return 1

    print(f"Importing from {args.csv} to database '{args.db}'...")
    stats = import_csv(args.csv, args.db)
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
