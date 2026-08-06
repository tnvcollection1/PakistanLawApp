#!/usr/bin/env python3
"""
build_cross_references.py
Builds a cross-reference graph between cases by finding citation links.
Outputs JSON and optionally a GML file for visualization.
"""

import os, sys, json, re, sqlite3, argparse
from collections import defaultdict

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "instance", "cases.db")

CITE_PATTERNS = [
    re.compile(r"(\d{4})\s+(\w+)\s+(\d+)", re.IGNORECASE),  # e.g., "2020 SCMR 123"
    re.compile(r"PLD\s+(\d{4})\s+(\w+)\s+(\d+)", re.IGNORECASE),  # e.g., "PLD 2020 SC 123"
    re.compile(r"(\d{4})\s+YLR\s+(\d+)", re.IGNORECASE),
]

def extract_citations(text):
    """Extract citation strings from case text."""
    if not text:
        return []
    found = []
    for pat in CITE_PATTERNS:
        for m in pat.finditer(text):
            found.append(m.group(0))
    return list(set(found))

def normalize_citation(cite):
    """Normalize citation for matching."""
    return re.sub(r"\s+", " ", cite.strip().lower())

def build_graph(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT id, title, case_number, court, full_text FROM cases")
    cases = [dict(row) for row in cur.fetchall()]

    # Build citation index
    cite_to_case = defaultdict(list)
    for case in cases:
        cnum = case.get("case_number")
        if cnum:
            cite_to_case[normalize_citation(cnum)].append(case["id"])

    nodes = {}
    edges = []

    for case in cases:
        nodes[case["id"]] = {
            "id": case["id"],
            "title": case.get("title", ""),
            "court": case.get("court", ""),
            "case_number": case.get("case_number", ""),
        }

        citations = extract_citations(case.get("full_text", ""))
        for cite in citations:
            norm = normalize_citation(cite)
            for target_id in cite_to_case.get(norm, []):
                if target_id != case["id"]:
                    edges.append({
                        "source": case["id"],
                        "target": target_id,
                        "citation": cite,
                    })

    conn.close()

    return {"nodes": list(nodes.values()), "edges": edges}

def output_gml(graph, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("graph [\n")
        f.write('  directed 1\n')
        for n in graph["nodes"]:
            f.write(f'  node [\n')
            f.write(f'    id {n["id"]}\n')
            safe_label = n["title"].replace('"', '\\"')[:60]
            f.write(f'    label "{safe_label}"\n')
            f.write(f'  ]\n')
        for e in graph["edges"]:
            f.write(f'  edge [\n')
            f.write(f'    source {e["source"]}\n')
            f.write(f'    target {e["target"]}\n')
            safe_label = e["citation"].replace('"', '\\"')[:40]
            f.write(f'    label "{safe_label}"\n')
            f.write(f'  ]\n')
        f.write("]\n")

def main():
    parser = argparse.ArgumentParser(description="Build cross-reference graph")
    parser.add_argument("--db", default=DB_PATH, help="Path to SQLite DB")
    parser.add_argument("--output", default="cross_references.json", help="Output JSON file")
    parser.add_argument("--gml", help="Output GML file for visualization")
    args = parser.parse_args()

    print(f"Building cross-reference graph from {args.db}...")
    graph = build_graph(args.db)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(graph['nodes'])} nodes and {len(graph['edges'])} edges to {args.output}")

    if args.gml:
        output_gml(graph, args.gml)
        print(f"Wrote GML to {args.gml}")

if __name__ == "__main__":
    main()
