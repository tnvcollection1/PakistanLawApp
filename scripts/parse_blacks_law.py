"""
Parse Black's Law - Parse Black's Law Dictionary entries
"""
import json
import re
import sys

def parse_blacks_law(text):
    """Parse Black's Law Dictionary text into structured entries."""
    entries = []
    # Pattern: TERM (definition...)
    pattern = r'([A-Z][A-Z\s\-]+)\s+\(([A-Za-z\s\.,;]+)\)'
    matches = re.findall(pattern, text)
    for term, definition in matches:
        entries.append({
            'term': term.strip(),
            'definition': definition.strip(),
        })
    return entries

def process_file(input_file, output_file):
    with open(input_file, 'r') as f:
        text = f.read()
    entries = parse_blacks_law(text)
    with open(output_file, 'w') as f:
        json.dump(entries, f, indent=2)
    print(f"Parsed {len(entries)} entries to {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python parse_blacks_law.py <input.txt> <output.json>")
        sys.exit(1)
    process_file(sys.argv[1], sys.argv[2])
