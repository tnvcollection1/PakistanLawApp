"""
Extract headnotes from case content using regex patterns
"""
import re
import json
import sys

def extract_headnotes(text):
    """Extract headnotes from case text."""
    patterns = [
        r'(?i)(?:headnote[s]?|syllabus|summary)[\s:]*(.+?)(?=\n\n|\Z)',
        r'(?i)(?:point[s]?\s+of\s+law|legal\s+principles)[\s:]*(.+?)(?=\n\n|\Z)',
    ]
    headnotes = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        headnotes.extend(matches)
    return headnotes

def process_file(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
    results = []
    for case in data:
        text = case.get('content', '') or case.get('text', '') or case.get('body', '')
        headnotes = extract_headnotes(text)
        results.append({
            'id': case.get('id'),
            'title': case.get('title'),
            'headnotes': headnotes,
        })
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Extracted headnotes from {len(results)} cases to {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python extract_headnotes.py <input.json> <output.json>")
        sys.exit(1)
    process_file(sys.argv[1], sys.argv[2])
