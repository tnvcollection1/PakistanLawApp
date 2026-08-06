#!/usr/bin/env python3
"""
DigiLawyer content extractor - fetches full case judgments and legislation
from DigiLawyer API and converts to structured format.

Run: python3 scripts/scrapers/digilawyer_extract.py [--case-id ID] [--output OUTPUT.json]
"""

import argparse
import json
import os
import re
import sys
import requests
from typing import Dict, List, Optional

BASE_URL = os.environ.get("DIGILAWYER_URL", "https://api.digilawyer.pk")
API_KEY = os.environ.get("DIGILAWYER_KEY", "")


def get_headers():
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "PakistanLawApp/1.0",
    }
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers


def fetch_case(case_id: str) -> Optional[Dict]:
    """Fetch a single case by ID."""
    try:
        url = f"{BASE_URL}/v1/cases/{case_id}"
        resp = requests.get(url, headers=get_headers(), timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data") or data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching case {case_id}: {e}", file=sys.stderr)
        return None


def fetch_cases(limit: int = 100, offset: int = 0) -> List[Dict]:
    """Fetch a batch of cases."""
    try:
        url = f"{BASE_URL}/v1/cases"
        params = {"limit": limit, "offset": offset}
        resp = requests.get(url, params=params, headers=get_headers(), timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", []) or data if isinstance(data, list) else []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching cases: {e}", file=sys.stderr)
        return []


def normalize_case(raw: Dict) -> Dict:
    """Convert raw DigiLawyer case to normalized format."""
    parties = raw.get("parties", "")
    if " vs " in parties:
        petitioner, respondent = parties.split(" vs ", 1)
    elif " VS " in parties:
        petitioner, respondent = parties.split(" VS ", 1)
    else:
        petitioner, respondent = parties, ""

    return {
        "source": "digilawyer",
        "case_id": raw.get("id", ""),
        "title": raw.get("title", ""),
        "citation": raw.get("citation", ""),
        "year": raw.get("year", ""),
        "court": raw.get("court", ""),
        "judge": raw.get("judge", ""),
        "date": raw.get("date", ""),
        "petitioner": petitioner.strip(),
        "respondent": respondent.strip(),
        "parties": parties,
        "headnotes": raw.get("headnotes", ""),
        "judgment_text": raw.get("judgment", raw.get("text", "")),
        "status": raw.get("status", "undecided"),
        "topic": raw.get("topic", ""),
        "subtopic": raw.get("subtopic", ""),
        "scraped_at": None,
        "url": raw.get("url", ""),
    }


def extract_headnotes(text: str) -> str:
    """Extract headnotes from judgment text if available."""
    if not text:
        return ""
    patterns = [
        r'(?i)head[\s-]?notes?[.:]\s*([\s\S]*?)(?=\n\s*(?:held|decision|judgment))',
        r'(?i)head[\s-]?notes?[.:]\s*([\s\S]*?)(?=\n\s*[A-Z])',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m.group(1).strip()[:2000]
    return ""


def save_to_file(data: List[Dict], output_path: str):
    """Save normalized cases to JSON file."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} cases to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Extract case data from DigiLawyer")
    parser.add_argument("--case-id", type=str, help="Fetch a single case by ID")
    parser.add_argument("--limit", type=int, default=100, help="Batch limit for multi-case fetch")
    parser.add_argument("--output", type=str, default="/tmp/digilawyer_cases.json", help="Output file path")
    args = parser.parse_args()

    if args.case_id:
        case = fetch_case(args.case_id)
        if case:
            normalized = normalize_case(case)
            save_to_file([normalized], args.output)
        else:
            print("Failed to fetch case", file=sys.stderr)
            return 1
    else:
        cases = fetch_cases(limit=args.limit)
        normalized = [normalize_case(c) for c in cases]
        save_to_file(normalized, args.output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
