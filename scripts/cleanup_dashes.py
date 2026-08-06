#!/usr/bin/env python3
"""
DB-level cleanup: Remove '---' artifacts from full_content and headnotes_text.
Replaces '---' with ' ' (space) to maintain readability.
Runs in batches to avoid memory issues.
"""
import os
import re
import json
import time
from datetime import datetime, timezone
from pymongo import MongoClient, UpdateOne

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://lawapp:VpsMongo2026LawXk9@localhost:27017/pakistanlawsite")
PROGRESS_FILE = "/tmp/dash_cleanup_progress.json"
BATCH_SIZE = 500

def save_progress(stats):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({**stats, "updated_at": datetime.now(timezone.utc).isoformat()}, f, indent=2)

def clean_text(text):
    """Replace --- with a dash and clean up extra whitespace."""
    if not text:
        return text
    # Replace --- with a proper dash
    text = re.sub(r'---', '-', text)
    # Clean up multiple consecutive dashes
    text = re.sub(r'-{3,}', '--', text)
    return text

def main():
    client = MongoClient(MONGO_URL)
    db_name = MONGO_URL.split("/")[-1].split("?")[0]
    db = client[db_name]

    total = db.pls_caselaws.count_documents({
        "$or": [
            {"full_content": {"$regex": "---"}},
            {"headnotes_text": {"$regex": "---"}}
        ]
    })
    print(f"Total cases to clean: {total}")

    stats = {"total": total, "processed": 0, "updated": 0, "errors": 0}
    save_progress(stats)

    skip = 0
    while True:
        # Find batch of cases with ---
        cases = list(db.pls_caselaws.find(
            {"$or": [
                {"full_content": {"$regex": "---"}},
                {"headnotes_text": {"$regex": "---"}}
            ]},
            {"_id": 1, "full_content": 1, "headnotes_text": 1, "headnotes": 1}
        ).limit(BATCH_SIZE))

        if not cases:
            break

        updates = []
        for case in cases:
            update_fields = {}
            if case.get("full_content") and "---" in case["full_content"]:
                update_fields["full_content"] = clean_text(case["full_content"])
            if case.get("headnotes_text") and "---" in case["headnotes_text"]:
                update_fields["headnotes_text"] = clean_text(case["headnotes_text"])
            if case.get("headnotes") and "---" in str(case["headnotes"]):
                if isinstance(case["headnotes"], str):
                    update_fields["headnotes"] = clean_text(case["headnotes"])

            if update_fields:
                updates.append(UpdateOne({"_id": case["_id"]}, {"$set": update_fields}))

        if updates:
            result = db.pls_caselaws.bulk_write(updates, ordered=False)
            stats["updated"] += result.modified_count

        stats["processed"] += len(cases)

        if stats["processed"] % 2000 == 0 or stats["processed"] >= total:
            save_progress(stats)
            print(f"  Progress: {stats['processed']}/{total} ({stats['processed']*100//total}%) | Updated: {stats['updated']}")

        # Small delay to not overwhelm MongoDB
        time.sleep(0.1)

    save_progress(stats)
    print(f"\nDone! Processed: {stats['processed']} | Updated: {stats['updated']} | Errors: {stats['errors']}")

if __name__ == "__main__":
    main()
