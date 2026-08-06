#!/usr/bin/env python3
"""Extract case metadata from case files."""

import json
import re
from pathlib import Path
import sys

DATA_DIR = Path("data")
OUTPUT_DIR = Path("data/metadata")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_parties(title):
    """Extract parties from case title."""
    patterns = [
        r'(.+?)\s+v(?:s)?\.?\s+(.+)',
        r'(.+?)\s+versus\s+(.+)',
    ]
    for pattern in patterns:
        match = re.match(pattern, title, re.IGNORECASE)
        if match:
            return {'appellant': match.group(1).strip(), 'respondent': match.group(2).strip()}
    return {'appellant': title, 'respondent': ''}

def extract_date(content):
    """Extract date from case content."""
    patterns = [
        r'(?:dated|date)[:\s]+(\d{1,2}[\s/-]\w+[\s/-]\d{4})',
        r'(?:decided on|pronounced on)[:\s]+(\d{1,2}[\s/-]\w+[\s/-]\d{4})',
        r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def extract_bench(content):
    """Extract bench information from case content."""
    patterns = [
        r'(?:Bench|Coram|Before)[:\s]+([^.]+)',
        r'(?:Single Bench|Division Bench|Full Bench)',
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(0)
    return None

def extract_metadata(case_data):
    """Extract metadata from case data."""
    title = case_data.get('title', '')
    content = case_data.get('content', '')
    
    metadata = {
        'parties': extract_parties(title),
        'date': extract_date(content),
        'bench': extract_bench(content),
        'year': case_data.get('year'),
        'court': case_data.get('court'),
        'citation': case_data.get('citation'),
        'case_number': case_data.get('case_number'),
    }
    return metadata

def process_all_cases():
    cases_dir = DATA_DIR / "cases"
    if not cases_dir.exists():
        print(f"Cases directory not found: {cases_dir}")
        return
    
    all_metadata = []
    for case_file in cases_dir.glob("*.json"):
        try:
            with open(case_file, 'r', encoding='utf-8') as f:
                case_data = json.load(f)
            metadata = extract_metadata(case_data)
            metadata['case_id'] = case_file.stem
            all_metadata.append(metadata)
        except Exception as e:
            print(f"Error processing {case_file.name}: {e}")
    
    output_file = OUTPUT_DIR / "all_metadata.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_metadata, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(all_metadata)} metadata entries to {output_file}")

def main():
    process_all_cases()

if __name__ == '__main__':
    main()
