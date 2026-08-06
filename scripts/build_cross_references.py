import json, os, re
from collections import defaultdict

def build_cross_references(cases_dir='data/cases', out='data/cross_references.json'):
    os.makedirs('data', exist_ok=True)
    refs = defaultdict(list)
    for fname in os.listdir(cases_dir):
        if not fname.endswith('.txt'):
            continue
        path = os.path.join(cases_dir, fname)
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        case_id = fname.replace('.txt', '')
        # Find citations like (2023) 15 SCC 123
        citations = re.findall(r'\(\d{4}\)\s+\d+\s+\w+\s+\d+', text)
        for cite in citations:
            refs[cite].append(case_id)
    with open(out, 'w') as f:
        json.dump(dict(refs), f, indent=2)
    print(f"[+] Built cross-references for {len(refs)} citations")

if __name__ == '__main__':
    build_cross_references()
