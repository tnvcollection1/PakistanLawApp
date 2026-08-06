"""
Extract Lawyers V3 - Extract lawyer information from legal documents
"""
import json
import re
import sys

def extract_lawyers(text):
    """Extract lawyer names from case text."""
    patterns = [
        r'(?:for\s+)?(?:the\s+)?(?:appellant[s]?|petitioner[s]?|plaintiff[s]?)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'(?:for\s+)?(?:the\s+)?(?:respondent[s]?|defendant[s]?)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'(?:counsel|advocate)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
    ]
    lawyers = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        lawyers.extend(matches)
    return list(set(lawyers))

def process_file(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
    results = []
    for item in data:
        text = item.get('content', '') or item.get('text', '') or item.get('body', '')
        lawyers = extract_lawyers(text)
        results.append({
            'id': item.get('id'),
            'title': item.get('title'),
            'lawyers': lawyers,
        })
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Extracted lawyers from {len(results)} items to {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python extract_lawyers_v3.py <input.json> <output.json>")
        sys.exit(1)
    process_file(sys.argv[1], sys.argv[2])
