#!/usr/bin/env python3
"""Fix PLS Beta content issues"""

import json
import re

def fix_content_format(content):
    """Fix common content formatting issues"""
    if not content:
        return content
    
    # Fix paragraph spacing
    content = re.sub(r'\n\s*\n', '\n\n', content)
    
    # Fix citation formatting
    content = re.sub(r'(\d{4})\s+([A-Z]+)\s+(\d+)', r'\1 \2 \3', content)
    
    # Fix section references
    content = re.sub(r'section\s+(\d+)', r'Section \1', content, flags=re.IGNORECASE)
    
    # Clean up whitespace
    content = content.strip()
    
    return content

def fix_case_data(case_file='cases.json', output_file='cases_fixed.json'):
    """Fix case data formatting"""
    with open(case_file, 'r') as f:
        cases = json.load(f)
    
    fixed = []
    for case in cases:
        case['content'] = fix_content_format(case.get('content', ''))
        case['title'] = case.get('title', '').strip()
        case['citation'] = case.get('citation', '').strip()
        fixed.append(case)
    
    with open(output_file, 'w') as f:
        json.dump(fixed, f, indent=2)
    
    print(f"Fixed {len(fixed)} cases")

def fix_statute_data(statute_file='statutes.json', output_file='statutes_fixed.json'):
    """Fix statute data formatting"""
    with open(statute_file, 'r') as f:
        statutes = json.load(f)
    
    fixed = []
    for statute in statutes:
        statute['content'] = fix_content_format(statute.get('content', ''))
        statute['title'] = statute.get('title', '').strip()
        fixed.append(statute)
    
    with open(output_file, 'w') as f:
        json.dump(fixed, f, indent=2)
    
    print(f"Fixed {len(fixed)} statutes")

def main():
    fix_case_data()
    fix_statute_data()

if __name__ == '__main__':
    main()
