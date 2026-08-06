#!/usr/bin/env python3
"""Batch process headnotes extraction."""

import json
import os
from pathlib import Path
import re
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from extract_headnotes import extract_headnotes_from_text

DATA_DIR = Path("data")
HEADNOTES_DIR = Path("data/headnotes")
HEADNOTES_DIR.mkdir(parents=True, exist_ok=True)

def batch_process_headnotes():
    cases_dir = DATA_DIR / "cases"
    if not cases_dir.exists():
        print(f"Cases directory not found: {cases_dir}")
        return
    
    case_files = list(cases_dir.glob("*.json"))
    print(f"Found {len(case_files)} case files to process")
    
    for i, case_file in enumerate(case_files):
        print(f"Processing {i+1}/{len(case_files)}: {case_file.name}")
        try:
            with open(case_file, 'r', encoding='utf-8') as f:
                case_data = json.load(f)
            
            content = case_data.get('content', '')
            if not content:
                continue
            
            headnotes = extract_headnotes_from_text(content)
            if headnotes:
                output_file = HEADNOTES_DIR / f"{case_file.stem}_headnotes.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(headnotes, f, indent=2, ensure_ascii=False)
                print(f"  Saved {len(headnotes)} headnotes")
        except Exception as e:
            print(f"  Error processing {case_file.name}: {e}")

def main():
    batch_process_headnotes()

if __name__ == '__main__':
    main()
