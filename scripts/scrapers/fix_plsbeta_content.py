"""
Fix PLS Beta Content - Fix and normalize content from PLS Beta
"""
import json
import re

def fix_content(text):
    """Fix common content issues."""
    if not text:
        return text
    # Fix whitespace
    text = ' '.join(text.split())
    # Fix encoding issues
    text = text.replace('\\u2018', "'").replace('\\u2019', "'")
    text = text.replace('\\u201c', '"').replace('\\u201d', '"')
    # Fix citations
    text = re.sub(r'\[\s+(\d+)\s+\]', r'[\1]', text)
    return text

def process_file(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
    for item in data:
        if 'content' in item:
            item['content'] = fix_content(item['content'])
        if 'text' in item:
            item['text'] = fix_content(item['text'])
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Fixed content for {len(data)} items")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python fix_plsbeta_content.py <input.json> <output.json>")
        sys.exit(1)
    process_file(sys.argv[1], sys.argv[2])
