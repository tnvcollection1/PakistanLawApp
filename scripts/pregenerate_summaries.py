"""
Pregenerate Summaries - Pre-generate summaries for cases
"""
import json
import os

# This is a placeholder for actual summary generation
# In production, this would call an AI model

def generate_summary(text, max_length=200):
    """Generate a simple extractive summary (placeholder)."""
    sentences = text.split('.')
    summary = '. '.join(sentences[:3]) + '.'
    if len(summary) > max_length:
        summary = summary[:max_length] + '...'
    return summary

def process_cases(input_file, output_file):
    with open(input_file, 'r') as f:
        cases = json.load(f)
    for case in cases:
        text = case.get('content', '') or case.get('text', '')
        if text:
            case['summary'] = generate_summary(text)
    with open(output_file, 'w') as f:
        json.dump(cases, f, indent=2)
    print(f"Generated summaries for {len(cases)} cases")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python pregenerate_summaries.py <input.json> <output.json>")
        sys.exit(1)
    process_cases(sys.argv[1], sys.argv[2])
