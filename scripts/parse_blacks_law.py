#!/usr/bin/env python3
"""Parser for Black's Law Dictionary entries"""

import re
import json

def parse_blacks_law(text):
    """Parse Black's Law Dictionary text format"""
    entries = {}
    
    # Split by entries (each entry starts with a term in uppercase)
    pattern = r'([A-Z][A-Z\s\-,]+)\s*\n(.*?)(?=\n[A-Z][A-Z\s\-,]+\n|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    for term, definition in matches:
        term = term.strip()
        definition = definition.strip()
        if term and definition:
            entries[term] = definition
    
    return entries

def load_and_parse(filename):
    """Load file and parse Black's Law entries"""
    with open(filename, 'r') as f:
        text = f.read()
    return parse_blacks_law(text)

def save_entries(entries, output_file='blacks_law.json'):
    """Save parsed entries to JSON"""
    with open(output_file, 'w') as f:
        json.dump(entries, f, indent=2)
    print(f"Saved {len(entries)} entries to {output_file}")

def main():
    entries = load_and_parse('blacks_law.txt')
    save_entries(entries)

if __name__ == '__main__':
    main()
