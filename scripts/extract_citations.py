"""
Extract Citations - Extract legal citations from text
"""
import re
import json
import sys

CITATION_PATTERNS = [
    r'\b\d{4}\s+PCrLJ\s+\d+\b',
    r'\b\d{4}\s+SCMR\s+\d+\b',
    r'\b\d{4}\s+PLD\s+\d+\b',
    r'\b\d{4}\s+CLC\s+\d+\b',
    r'\b\d{4}\s+MLD\s+\d+\b',
    r'\b\d{4}\s+PMC\s+\d+\b',
    r'\b\d{4}\s+PCrLJ\s+\d+\b',
    r'\b\d{4}\s+PLJ\s+\d+\b',
    r'\b\d{4}\s+SCMR\s+\d+\b',
    r'\b\d{4}\s+PCrLJ\s+\d+\b',
    r'\b\d{4}\s+LC\s+\d+\b',
    r'\b\d{4}\s+YLR\s+\d+\b',
]

def extract_citations(text):
    citations = []
    for pattern in CITATION_PATTERNS:
        matches = re.findall(pattern, text)
        citations.extend(matches)
    return list(set(citations))

def process_file(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
    results = []
    for item in data:
        text = item.get('content', '') or item.get('text', '') or item.get('body', '')
        citations = extract_citations(text)
        results.append({
            'id': item.get('id'),
            'title': item.get('title'),
            'citations': citations,
        })
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Extracted citations from {len(results)} items to {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python extract_citations.py <input.json> <output.json>")
        sys.exit(1)
    process_file(sys.argv[1], sys.argv[2])
