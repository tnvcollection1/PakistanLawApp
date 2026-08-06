#!/usr/bin/env python3
"""
Metadata Extraction Script for PakistanLawApp
Parses judgment_text to extract missing judge names, party names, and lawyer names.
Run on production VPS: python3 extract_metadata_v2.py
"""
import re
import sys
from pymongo import MongoClient, UpdateOne

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"
BATCH_SIZE = 500

client = MongoClient(MONGO_URL)
db = client[DB_NAME]


def extract_judges(text):
    """Extract judge names from judgment text."""
    if not text:
        return []
    patterns = [
        r"(?:Before|BEFORE)[:\s]*((?:[A-Z][a-z]+\.?\s+)*[A-Z][a-z]+,?\s*(?:J\.?|CJ|Chief Justice|Justice)[,\s]*)+",
        r"((?:[A-Z][a-z]+\.?\s+)*[A-Z][a-z]+,?\s*(?:J\.?|CJ|Chief Justice|Justice))[\s,;]",
        r"(?:Coram|CORAM)[:\s]*((?:[A-Z][a-z]+\.?\s+)*[A-Z][a-z]+[,\s]*)+",
    ]
    judges = []
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            judges.extend([j.strip() for j in match.group(1).split(",") if j.strip()])
    return list(set(judges))


def extract_parties(text):
    """Extract petitioner and respondent names from judgment text."""
    if not text:
        return {"petitioner": None, "respondent": None}
    petitioner = None
    respondent = None
    patterns = [
        r"(?:petitioner[s]?|appellant[s]?)[:\s]*([^\n;]+)",
        r"(?:respondent[s]?|defendant[s]?)[:\s]*([^\n;]+)",
    ]
    for match in re.finditer(patterns[0], text, re.IGNORECASE):
        petitioner = match.group(1).strip()
        break
    for match in re.finditer(patterns[1], text, re.IGNORECASE):
        respondent = match.group(1).strip()
        break
    return {"petitioner": petitioner, "respondent": respondent}


def extract_lawyers(text):
    """Extract lawyer names from judgment text."""
    if not text:
        return []
    patterns = [
        r"(?:for\s+the\s+petitioner[s]?)[:\s]*([^\n;]+)",
        r"(?:for\s+the\s+respondent[s]?)[:\s]*([^\n;]+)",
        r"(?:counsel\s+for)[:\s]*([^\n;]+)",
        r"(?:learned\s+counsel)[:\s]*([^\n;]+)",
    ]
    lawyers = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            lawyers.extend([l.strip() for l in match.group(1).split(",") if l.strip()])
    return list(set(lawyers))


def process_batch(batch):
    """Process a batch of cases and return update operations."""
    operations = []
    for case in batch:
        case_id = case["_id"]
        text = case.get("judgment_text", "")
        updates = {}
        if not case.get("judges"):
            judges = extract_judges(text)
            if judges:
                updates["judges"] = judges
        if not case.get("petitioner") or not case.get("respondent"):
            parties = extract_parties(text)
            if parties["petitioner"]:
                updates["petitioner"] = parties["petitioner"]
            if parties["respondent"]:
                updates["respondent"] = parties["respondent"]
        if not case.get("lawyers"):
            lawyers = extract_lawyers(text)
            if lawyers:
                updates["lawyers"] = lawyers
        if updates:
            operations.append(UpdateOne({"_id": case_id}, {"$set": updates}))
    return operations


def run_extraction():
    collection = db["cases"]
    total = collection.count_documents({})
    print(f"Processing {total:,} cases for metadata extraction...")
    processed = 0
    updated = 0
    new_missing_judges = 0
    new_missing_lawyers = 0
    new_missing_petitioner = 0
    new_missing_respondent = 0
    cursor = collection.find({}, {"_id": 1, "judgment_text": 1, "judges": 1, "lawyers": 1, "petitioner": 1, "respondent": 1})
    batch = []
    for case in cursor:
        batch.append(case)
        if len(batch) >= BATCH_SIZE:
            ops = process_batch(batch)
            if ops:
                result = collection.bulk_write(ops, ordered=False)
                updated += result.modified_count
            for case in batch:
                if not case.get("judges"):
                    new_missing_judges += 1
                if not case.get("lawyers"):
                    new_missing_lawyers += 1
                if not case.get("petitioner"):
                    new_missing_petitioner += 1
                if not case.get("respondent"):
                    new_missing_respondent += 1
            processed += len(batch)
            print(f"  Processed {processed:,}/{total:,} | Updated {updated:,} | Missing: judges={new_missing_judges}, lawyers={new_missing_lawyers}, petitioner={new_missing_petitioner}, respondent={new_missing_respondent}")
            batch = []
    if batch:
        ops = process_batch(batch)
        if ops:
            result = collection.bulk_write(ops, ordered=False)
            updated += result.modified_count
        for case in batch:
            if not case.get("judges"):
                new_missing_judges += 1
            if not case.get("lawyers"):
                new_missing_lawyers += 1
            if not case.get("petitioner"):
                new_missing_petitioner += 1
            if not case.get("respondent"):
                new_missing_respondent += 1
        processed += len(batch)
    print(f"Done! Updated {updated:,} of {total:,} cases.")
    print(f"Judge coverage: {(total - new_missing_judges) / total * 100:.1f}% ({total - new_missing_judges:,}/{total:,})")
    print(f"Lawyer coverage: {(total - new_missing_lawyers) / total * 100:.1f}% ({total - new_missing_lawyers:,}/{total:,})")
    print(f"Petitioner coverage: {(total - new_missing_petitioner) / total * 100:.1f}% ({total - new_missing_petitioner:,}/{total:,})")
    print(f"Respondent coverage: {(total - new_missing_respondent) / total * 100:.1f}% ({total - new_missing_respondent:,}/{total:,})")


if __name__ == "__main__":
    run_extraction()
