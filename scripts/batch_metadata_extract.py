"""
Batch Metadata Extraction Script
Extracts missing judges and parties from case text using:
  Pass 1: Regex patterns (fast, free)
  Pass 2: GPT-5.2 via Emergent LLM Key (for remaining)

Usage: python3 -u scripts/batch_metadata_extract.py [--mode regex|llm|both] [--limit N]
"""
import os
import re
import sys
import json
import time
import asyncio
import argparse
from datetime import datetime, timezone
from pymongo import MongoClient

# --- Config ---
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://lawapp:VpsMongo2026LawXk9@localhost:27017/pakistanlawsite")
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
PROGRESS_FILE = "/tmp/metadata_extract_progress.json"
LOG_FILE = "/tmp/metadata_extract.log"
BATCH_SIZE = 100
LLM_RATE_LIMIT = 0.2  # seconds between LLM calls

client = MongoClient(MONGO_URL)
db_name = MONGO_URL.split("/")[-1].split("?")[0]
db = client[db_name]
collection = db["pls_caselaws"]


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ===== REGEX PATTERNS =====

JUDGE_PATTERNS = [
    # "Present: Mr. Justice Name, Mr. Justice Name2" (multi-line capture up to 200 chars)
    re.compile(r"Present\s*:\s*(.{3,200}?)(?:\n\s*\n|\nAppeal|\nPetition|\nSuit|\nCase|\nWrit|\n[A-Z]{2,}[a-z])", re.IGNORECASE | re.DOTALL),
    # Simpler fallback: grab the whole line + next line
    re.compile(r"Present\s*:\s*(.+(?:\n.+)?)", re.IGNORECASE),
    # "Before Mr. Justice Name"
    re.compile(r"Before\s+(?:the\s+)?(?:Hon(?:'|o)(?:u)?rable\s+)?(.{3,200}?)(?:\n\s*\n|\n[A-Z])", re.IGNORECASE | re.DOTALL),
    # "CORAM: Judge names"
    re.compile(r"CORAM\s*:\s*(.{3,200}?)(?:\n\s*\n|\n[A-Z])", re.IGNORECASE | re.DOTALL),
]

PARTY_PATTERNS = [
    # "Name Vs Name" across possible line breaks (DOTALL not needed, just allow \n in names)
    re.compile(r"^(.{5,120}?)\s*\n?\s*(?:Vs\.?|VS\.?|versus|VERSUS|v\.)\s*\n?\s*(.{5,120}?)$", re.MULTILINE),
    # Simpler single-line pattern
    re.compile(r"([A-Z][A-Z\s.,]+?)\s+(?:Vs\.?|VS\.?|versus|VERSUS)\s+([A-Z][A-Z\s.,]+?)(?:\n|$)", re.MULTILINE),
]


def clean_judge_text(text):
    """Clean extracted judge name"""
    text = text.strip()
    # Rejoin broken lines
    text = re.sub(r"\n\s*", " ", text)
    # Remove common prefixes/suffixes
    text = re.sub(r"^(Mr\.\s*|Mrs\.\s*|Ms\.\s*)", "", text, flags=re.IGNORECASE)
    text = re.sub(r",?\s*JJ?\.?\s*$", "", text)  # Remove trailing J/JJ
    text = re.sub(r"\s+", " ", text).strip()
    # Remove "Appellate Tribunal" etc from end
    text = re.sub(r",?\s*(Appellate\s+Tribunal|Chairman|Member).*$", "", text, flags=re.IGNORECASE).strip()
    # Skip if too short or too long or has garbage
    if len(text) < 3 or len(text) > 200:
        return None
    if any(c in text for c in ["<", ">", "{", "}", "http"]):
        return None
    return text


def extract_judge_regex(text):
    """Try to extract judge name from text using regex"""
    if not text:
        return None
    # Check first 3000 chars only
    snippet = text[:3000]
    for pattern in JUDGE_PATTERNS:
        match = pattern.search(snippet)
        if match:
            raw = match.group(1)
            cleaned = clean_judge_text(raw)
            if cleaned:
                return cleaned
    return None


def extract_parties_regex(text):
    """Try to extract parties from text using regex"""
    if not text:
        return None
    snippet = text[:2000]
    for pattern in PARTY_PATTERNS:
        match = pattern.search(snippet)
        if match:
            petitioner = match.group(1).strip()
            respondent = match.group(2).strip()
            # Basic validation
            if 3 < len(petitioner) < 150 and 3 < len(respondent) < 150:
                parties = f"{petitioner} VS {respondent}"
                return {"parties": parties, "petitioner": petitioner, "respondent": respondent}
    return None


# ===== REGEX PASS =====

def run_regex_pass(field="both", limit=0):
    """Extract metadata using regex patterns"""
    progress = {
        "mode": "regex",
        "field": field,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "judges_found": 0,
        "parties_found": 0,
        "processed": 0,
        "total": 0,
        "errors": 0,
    }

    # Build query for missing metadata
    or_conditions = []
    if field in ("judge", "both"):
        or_conditions.append({"$or": [
            {"judge": {"$exists": False}},
            {"judge": None},
            {"judge": ""},
            {"judge": "N/A"},
        ]})
    if field in ("parties", "both"):
        or_conditions.append({"$or": [
            {"parties": {"$exists": False}},
            {"parties": None},
            {"parties": ""},
            {"parties": "---"},
        ]})

    if not or_conditions:
        log("No fields to extract")
        return

    query = {"$or": or_conditions} if len(or_conditions) > 1 else or_conditions[0]

    total = collection.count_documents(query)
    progress["total"] = total
    log(f"REGEX PASS: Found {total} cases with missing metadata (field={field})")

    if limit:
        log(f"  Limiting to {limit} cases")

    cursor = collection.find(
        query,
        {"case_id": 1, "full_content": 1, "headnotes_text": 1, "judge": 1, "parties": 1, "petitioner": 1, "respondent": 1},
    )
    if limit:
        cursor = cursor.limit(limit)

    batch_updates = []
    for i, doc in enumerate(cursor):
        text = doc.get("full_content") or doc.get("headnotes_text") or ""
        update_fields = {}

        # Extract judge if missing
        current_judge = doc.get("judge", "")
        if field in ("judge", "both") and (not current_judge or current_judge in ("N/A", "")):
            judge = extract_judge_regex(text)
            if judge:
                update_fields["judge"] = judge
                progress["judges_found"] += 1

        # Extract parties if missing
        current_parties = doc.get("parties", "")
        if field in ("parties", "both") and (not current_parties or current_parties in ("---", "")):
            result = extract_parties_regex(text)
            if result:
                update_fields["parties"] = result["parties"]
                if not doc.get("petitioner"):
                    update_fields["petitioner"] = result["petitioner"]
                if not doc.get("respondent"):
                    update_fields["respondent"] = result["respondent"]
                progress["parties_found"] += 1

        if update_fields:
            batch_updates.append({
                "filter": {"_id": doc["_id"]},
                "update": {"$set": update_fields},
            })

        # Flush batch
        if len(batch_updates) >= BATCH_SIZE:
            for bu in batch_updates:
                collection.update_one(bu["filter"], bu["update"])
            batch_updates = []

        progress["processed"] = i + 1
        if (i + 1) % 2000 == 0:
            save_progress(progress)
            log(f"  Progress: {i+1}/{total} | Judges: {progress['judges_found']} | Parties: {progress['parties_found']}")

    # Flush remaining
    for bu in batch_updates:
        collection.update_one(bu["filter"], bu["update"])

    progress["completed_at"] = datetime.now(timezone.utc).isoformat()
    save_progress(progress)
    log(f"REGEX PASS COMPLETE: Processed {progress['processed']}, Judges found: {progress['judges_found']}, Parties found: {progress['parties_found']}")
    return progress


# ===== LLM PASS =====

async def extract_metadata_llm(text_snippet, missing_fields):
    """Use GPT-5.2 to extract metadata from case text"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    import uuid

    fields_str = ", ".join(missing_fields)
    prompt = f"""Extract the following metadata from this Pakistani court case text: {fields_str}

Text (first 2000 chars):
---
{text_snippet[:2000]}
---

Return ONLY valid JSON with these fields (use null if not found):
{{
  "judge": "Full name of the judge(s)",
  "parties": "Petitioner VS Respondent",
  "petitioner": "Name of petitioner/appellant",
  "respondent": "Name of respondent"
}}"""

    llm = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=str(uuid.uuid4()),
        system_message="You extract metadata from legal case text. Always respond with valid JSON only.",
    ).with_model("openai", "gpt-5.2")

    response = await llm.send_message(UserMessage(text=prompt))
    # Response may be a string directly or have a .text attribute
    resp_text = response.text if hasattr(response, 'text') else str(response)
    resp_text = resp_text.strip()
    # Remove markdown code blocks if present
    if resp_text.startswith("```"):
        resp_text = re.sub(r"```(?:json)?\n?", "", resp_text).strip()
    return json.loads(resp_text)


async def run_llm_pass(field="both", limit=0):
    """Extract metadata using LLM for cases where regex failed"""
    if not EMERGENT_KEY:
        log("ERROR: EMERGENT_LLM_KEY not set. Cannot run LLM pass.")
        return

    progress = {
        "mode": "llm",
        "field": field,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "judges_found": 0,
        "parties_found": 0,
        "processed": 0,
        "total": 0,
        "errors": 0,
        "llm_calls": 0,
    }

    # Build query for STILL missing metadata (after regex pass)
    or_conditions = []
    if field in ("judge", "both"):
        or_conditions.append({"$or": [
            {"judge": {"$exists": False}},
            {"judge": None},
            {"judge": ""},
            {"judge": "N/A"},
        ]})
    if field in ("parties", "both"):
        or_conditions.append({"$or": [
            {"parties": {"$exists": False}},
            {"parties": None},
            {"parties": ""},
            {"parties": "---"},
        ]})

    query = {"$or": or_conditions} if len(or_conditions) > 1 else or_conditions[0]
    # Combine with text-content filter: only cases that have some text
    all_missing_conditions = []
    for oc in or_conditions:
        all_missing_conditions.extend(oc.get("$or", [oc]))
    query = {"$and": [
        {"$or": all_missing_conditions},
        {"$or": [
            {"full_content": {"$exists": True, "$ne": None, "$ne": ""}},
            {"headnotes_text": {"$exists": True, "$ne": None, "$ne": ""}},
        ]}
    ]}

    total = collection.count_documents(query)
    progress["total"] = total
    log(f"LLM PASS: Found {total} cases still missing metadata (field={field})")

    if limit:
        total = min(total, limit)
        log(f"  Limiting to {limit} cases")

    # Pre-fetch all document IDs to avoid cursor timeout during slow LLM calls
    log("  Pre-fetching document IDs...")
    id_cursor = collection.find(query, {"_id": 1})
    if limit:
        id_cursor = id_cursor.limit(limit)
    doc_ids = [d["_id"] for d in id_cursor]
    log(f"  Fetched {len(doc_ids)} IDs. Starting LLM extraction...")

    for i, doc_id in enumerate(doc_ids):
        # Fetch each doc individually (avoids cursor timeout)
        doc = collection.find_one(
            {"_id": doc_id},
            {"case_id": 1, "full_content": 1, "headnotes_text": 1, "judge": 1, "parties": 1, "petitioner": 1, "respondent": 1},
        )
        if not doc:
            progress["processed"] = i + 1
            continue
        text = doc.get("full_content") or doc.get("headnotes_text") or ""
        if len(text) < 50:
            progress["processed"] += 1
            continue

        missing_fields = []
        if field in ("judge", "both") and not doc.get("judge"):
            missing_fields.append("judge")
        if field in ("parties", "both") and (not doc.get("parties") or doc.get("parties") == "---"):
            missing_fields.append("parties")

        if not missing_fields:
            progress["processed"] += 1
            continue

        try:
            result = await extract_metadata_llm(text, missing_fields)
            progress["llm_calls"] += 1
            update_fields = {}

            if "judge" in missing_fields and result.get("judge"):
                judge_val = result["judge"]
                if isinstance(judge_val, str) and len(judge_val) > 2 and judge_val.lower() != "null":
                    update_fields["judge"] = judge_val
                    progress["judges_found"] += 1

            if "parties" in missing_fields:
                if result.get("parties") and isinstance(result["parties"], str) and len(result["parties"]) > 5:
                    update_fields["parties"] = result["parties"]
                    progress["parties_found"] += 1
                if result.get("petitioner") and not doc.get("petitioner"):
                    update_fields["petitioner"] = result["petitioner"]
                if result.get("respondent") and not doc.get("respondent"):
                    update_fields["respondent"] = result["respondent"]

            if update_fields:
                collection.update_one({"_id": doc["_id"]}, {"$set": update_fields})

        except json.JSONDecodeError:
            progress["errors"] += 1
        except Exception as e:
            progress["errors"] += 1
            if progress["errors"] <= 5:
                log(f"  LLM error on case {doc.get('case_id', '?')}: {str(e)[:100]}")

        progress["processed"] = i + 1
        if (i + 1) % 50 == 0:
            save_progress(progress)
            log(f"  Progress: {i+1}/{total} | Judges: {progress['judges_found']} | Parties: {progress['parties_found']} | LLM calls: {progress['llm_calls']} | Errors: {progress['errors']}")

        # Rate limit
        await asyncio.sleep(LLM_RATE_LIMIT)

    progress["completed_at"] = datetime.now(timezone.utc).isoformat()
    save_progress(progress)
    log(f"LLM PASS COMPLETE: Processed {progress['processed']}, Judges: {progress['judges_found']}, Parties: {progress['parties_found']}, LLM calls: {progress['llm_calls']}, Errors: {progress['errors']}")
    return progress


# ===== MAIN =====

def main():
    parser = argparse.ArgumentParser(description="Batch metadata extraction")
    parser.add_argument("--mode", choices=["regex", "llm", "both"], default="both", help="Extraction mode")
    parser.add_argument("--field", choices=["judge", "parties", "both"], default="both", help="Which field to extract")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of cases (0=all)")
    args = parser.parse_args()

    log(f"=== Batch Metadata Extraction Started ===")
    log(f"Mode: {args.mode}, Field: {args.field}, Limit: {args.limit or 'ALL'}")

    # Count current missing metadata
    missing_judges = collection.count_documents({"$or": [
        {"judge": {"$exists": False}}, {"judge": None}, {"judge": ""}, {"judge": "N/A"}
    ]})
    missing_parties = collection.count_documents({"$or": [
        {"parties": {"$exists": False}}, {"parties": None}, {"parties": ""}, {"parties": "---"}
    ]})
    log(f"Current missing: Judges={missing_judges}, Parties={missing_parties}")

    if args.mode in ("regex", "both"):
        run_regex_pass(field=args.field, limit=args.limit)

    if args.mode in ("llm", "both"):
        asyncio.run(run_llm_pass(field=args.field, limit=args.limit))

    # Final counts
    still_missing_judges = collection.count_documents({"$or": [
        {"judge": {"$exists": False}}, {"judge": None}, {"judge": ""}, {"judge": "N/A"}
    ]})
    still_missing_parties = collection.count_documents({"$or": [
        {"parties": {"$exists": False}}, {"parties": None}, {"parties": ""}, {"parties": "---"}
    ]})
    log(f"=== DONE === Still missing: Judges={still_missing_judges}, Parties={still_missing_parties}")


if __name__ == "__main__":
    main()
