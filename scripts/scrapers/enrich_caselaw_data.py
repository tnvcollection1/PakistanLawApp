"""
Enrich Caselaw Data - Enrich existing caselaw with additional metadata
"""
import json
from datetime import datetime

def enrich_caselaw(input_file, output_file):
    with open(input_file, 'r') as f:
        cases = json.load(f)
    enriched = []
    for case in cases:
        case['enriched_at'] = datetime.utcnow().isoformat()
        case['word_count'] = len(case.get('content', '').split())
        case['citation_count'] = len(case.get('citations', []))
        case['has_headnotes'] = bool(case.get('headnotes'))
        case['has_summary'] = bool(case.get('summary'))
        enriched.append(case)
    with open(output_file, 'w') as f:
        json.dump(enriched, f, indent=2)
    print(f"Enriched {len(enriched)} cases to {output_file}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python enrich_caselaw_data.py <input.json> <output.json>")
        sys.exit(1)
    enrich_caselaw(sys.argv[1], sys.argv[2])
