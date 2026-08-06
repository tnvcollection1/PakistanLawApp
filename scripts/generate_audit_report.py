#!/usr/bin/env python3
"""
Generate Audit Report for PakistanLawApp data.
Produces a comprehensive markdown report covering:
- Data completeness (judges, parties, citations, content)
- Quality metrics (duplicate cases, malformed citations, empty content)
- Court coverage
- Year distribution
- FAISS index status
- EastLaw comparison benchmark
- Recommendations for improvement

Usage:
    python3 scripts/generate_audit_report.py [--output report.md] [--mongo-url mongodb://...]
"""
import os
import sys
import re
import json
import argparse
from datetime import datetime, timezone
from collections import Counter, defaultdict
from pymongo import MongoClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017/pakistanlawsite")
DB_NAME = os.environ.get("DB_NAME", "pakistanlawsite")
OUTPUT_PATH = "/tmp/audit_report.md"


def connect():
    client = MongoClient(MONGO_URL, maxPoolSize=10)
    db = client[DB_NAME]
    return db


def audit_data(db):
    collection = db.pls_caselaws
    report = []
    report.append("# PakistanLawApp Data Audit Report")
    report.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append(f"Database: `{DB_NAME}`")
    report.append("")

    # --- Totals ---
    total = collection.count_documents({})
    report.append(f"## Overview")
    report.append(f"- **Total cases**: {total:,}")
    report.append("")

    # --- Data Completeness ---
    report.append("## Data Completeness")
    fields = {
        "judge": "Judge name",
        "parties": "Parties (Petitioner vs Respondent)",
        "petitioner": "Petitioner",
        "respondent": "Respondent",
        "citation": "Citation",
        "year": "Year",
        "court": "Court",
        "full_content": "Full case text",
        "headnotes_text": "Headnotes",
        "case_id": "Case ID",
    }
    for field, label in fields.items():
        present = collection.count_documents({field: {"$exists": True, "$ne": None, "$ne": ""}})
        pct = (present / total * 100) if total else 0
        report.append(f"- **{label}**: {present:,} / {total:,} ({pct:.1f}%)")
    report.append("")

    # --- Quality Issues ---
    report.append("## Quality Issues")
    # Duplicates by citation
    dup_pipeline = [
        {"$match": {"citation": {"$exists": True, "$ne": None, "$ne": ""}}},
        {"$group": {"_id": "$citation", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
        {"$count": "duplicate_citations"}
    ]
    dup_result = list(collection.aggregate(dup_pipeline))
    dup_citations = dup_result[0]["duplicate_citations"] if dup_result else 0
    report.append(f"- **Duplicate citations**: {dup_citations:,}")

    # Empty content
    empty_content = collection.count_documents({
        "$or": [
            {"full_content": {"$exists": False}},
            {"full_content": None},
            {"full_content": ""},
        ]
    })
    report.append(f"- **Cases without full text**: {empty_content:,} ({(empty_content/total*100) if total else 0:.1f}%)")

    # Malformed citations (missing year/journal/page)
    malformed = collection.count_documents({
        "citation": {"$exists": True, "$ne": None, "$ne": ""},
        "$or": [
            {"citation": {"$not": re.compile(r"\d{4}")}},
        ]
    })
    report.append(f"- **Citations missing year**: {malformed:,}")
    report.append("")

    # --- Court Coverage ---
    report.append("## Court Coverage")
    court_pipeline = [
        {"$group": {"_id": "$court", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    courts = list(collection.aggregate(court_pipeline))
    for c in courts:
        name = c["_id"] or "Unknown"
        report.append(f"- {name}: {c['count']:,}")
    report.append("")

    # --- Year Distribution ---
    report.append("## Year Distribution (Top 20)")
    year_pipeline = [
        {"$match": {"year": {"$exists": True, "$ne": None, "$type": "int"}}},
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    years = list(collection.aggregate(year_pipeline))
    for y in years:
        report.append(f"- {y['_id']}: {y['count']:,}")
    report.append("")

    # --- FAISS Index Status ---
    report.append("## FAISS Index Status")
    try:
        import faiss
        # Check for index files
        index_dir = "/app/backend/faiss_indexes"
        if os.path.exists(index_dir):
            index_files = [f for f in os.listdir(index_dir) if f.endswith(".faiss") or f.endswith(".index")]
            report.append(f"- **Index files**: {len(index_files)}")
            for f in index_files:
                size_mb = os.path.getsize(os.path.join(index_dir, f)) / (1024 * 1024)
                report.append(f"  - `{f}`: {size_mb:.1f} MB")
        else:
            report.append("- No FAISS index directory found")
    except ImportError:
        report.append("- FAISS not installed, cannot check index status")
    report.append("")

    # --- EastLaw Comparison ---
    report.append("## EastLaw Comparison Benchmark")
    eastlaw_total = 231475  # Known EastLaw total
    report.append(f"- **EastLaw total cases**: {eastlaw_total:,}")
    report.append(f"- **Our total cases**: {total:,}")
    gap = eastlaw_total - total
    report.append(f"- **Gap**: {gap:,} ({(total/eastlaw_total*100):.1f}% coverage)")
    report.append("")

    # --- Recommendations ---
    report.append("## Recommendations")
    if empty_content > total * 0.3:
        report.append("- **PRIORITY**: Over 30% of cases lack full text. Run content extraction pipeline.")
    if dup_citations > 1000:
        report.append(f"- **PRIORITY**: {dup_citations:,} duplicate citations detected. Run deduplication.")
    if malformed > 10000:
        report.append(f"- **PRIORITY**: {malformed:,} citations missing year. Run citation repair.")
    report.append("- Continue EastLaw spider to close the gap.")
    report.append("- Normalize court names using scripts/normalize_courts.py.")
    report.append("- Extract missing judge names and parties using batch_metadata_extract.py.")
    report.append("")

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Generate data audit report")
    parser.add_argument("--output", type=str, default=OUTPUT_PATH, help="Output file path")
    parser.add_argument("--mongo-url", type=str, default=MONGO_URL, help="MongoDB connection URL")
    args = parser.parse_args()

    db = connect()
    report = audit_data(db)
    with open(args.output, "w") as f:
        f.write(report)
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
