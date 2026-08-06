"""
Case Citations API - Extract and return structured citation data for a case
"""
from fastapi import APIRouter, HTTPException
from database import db
from cachetools import TTLCache
import re
import asyncio

router = APIRouter()

# Cache citation results per case_id (10 min TTL)
_citation_cache = TTLCache(maxsize=500, ttl=600)

JOURNAL_NAMES = {
    "PLD": "Pakistan Legal Decisions",
    "SCMR": "Supreme Court Monthly Review",
    "CLC": "Civil Law Cases",
    "PCrLJ": "Pakistan Criminal Law Journal",
    "YLR": "Yearly Law Reports",
    "MLD": "Monthly Law Digest",
    "PTD": "Pakistan Tax Decisions",
    "PLC": "Pakistan Labour Cases",
    "PTCL": "Pakistan Tax Cases (Lahore)",
    "PLJ": "Pakistan Law Journal",
    "NLR": "National Law Reports",
}

# Journal-to-court mapping (journals that imply a specific court)
JOURNAL_COURT_MAP = {
    "SCMR": "Supreme Court",
    "PTD": "Tax Tribunal",
    "PTCL": "Tax Tribunal",
    "PLC": "Labour Court",
}

# PLD court designator mapping
PLD_COURT_CODES = {
    "SC": "Supreme Court", "S.C.": "Supreme Court",
    "Supreme": "Supreme Court", "Supreme Court": "Supreme Court",
    "Lahore": "Lahore High Court", "Lah": "Lahore High Court",
    "Karachi": "Sindh High Court", "Kar": "Sindh High Court",
    "Sindh": "Sindh High Court",
    "Peshawar": "Peshawar High Court", "Pesh": "Peshawar High Court",
    "Quetta": "Balochistan High Court", "Quet": "Balochistan High Court",
    "Islamabad": "Islamabad High Court", "Isl": "Islamabad High Court",
    "FSC": "Federal Shariat Court", "Federal": "Federal Shariat Court",
}

# Compact journal patterns (e.g., "2021 SCMR 488")
CITATION_PATTERNS = [
    r'\d{4}\s+PLD\s+\d+',
    r'\d{4}\s+SCMR\s+\d+',
    r'\d{4}\s+CLC\s+\d+',
    r'\d{4}\s+PCr\.?L\.?J\.?\s+\d+',
    r'\d{4}\s+YLR\s+\d+',
    r'\d{4}\s+MLD\s+\d+',
    r'\d{4}\s+PTD\s+\d+',
    r'\d{4}\s+PLC\s+\d+',
    r'\d{4}\s+PTCL\s+\d+',
    r'\d{4}\s+PLJ\s+\d+',
    r'\d{4}\s+NLR\s+\d+',
    r'PLD\s+\d{4}\s+(?:Supreme\s+Court|SC|Lahore|Karachi|Peshawar|Quetta|Islamabad|FSC|Federal\s+Shariat\s+Court)\s+\d+',
    r'PLD\s+\d{4}\s+\w+\s+\d+',
]

# Spaced journal patterns (e.g., "2021 C L C 1114", "P L D 2026 Supreme 5")
SPACED_CITATION_PATTERNS = [
    r'\d{4,5}\s+P\s+L\s+D\s+\d+',
    r'\d{4,5}\s+S\s+C\s+M\s+R\s+\d+',
    r'\d{4,5}\s+C\s+L\s+C\s+\d+',
    r'\d{4,5}\s+P\s*C\s*r\s*\.?\s*L\s*\.?\s*J\.?\s+\d+',
    r'\d{4,5}\s+Y\s+L\s+R\s+\d+',
    r'\d{4,5}\s+M\s+L\s+D\s+\d+',
    r'\d{4,5}\s+P\s+T\s+D\s+\d+',
    r'\d{4,5}\s+P\s+L\s+C\s+\d+',
    r'\d{4,5}\s+P\s+L\s+J\s+\d+',
    r'\d{4,5}\s+N\s+L\s+R\s+\d+',
    r'P\s+L\s+D\s+\d{4}\s+\w+\s+\d+',
]

# Map spaced journal names to compact form
JOURNAL_NORMALIZE = {
    'P L D': 'PLD', 'S C M R': 'SCMR', 'C L C': 'CLC',
    'Y L R': 'YLR', 'M L D': 'MLD', 'P T D': 'PTD',
    'P L C': 'PLC', 'P L J': 'PLJ', 'N L R': 'NLR',
    'P C r. L. J': 'PCrLJ', 'P C r L J': 'PCrLJ',
}

STATUTE_PATTERNS = [
    r'(?:the\s+)?[A-Z][a-zA-Z\s]+Act[\s,]+\d{4}',
    r'(?:the\s+)?[A-Z][a-zA-Z\s]+Ordinance[\s,]+\d{4}',
    r'(?:the\s+)?Constitution\s+of\s+(?:the\s+)?Islamic\s+Republic\s+of\s+Pakistan',
    r'(?:Article|Section|S\.)\s+\d+[\w\(\)]*',
    r'(?:Order|Rule)\s+\d+[\w\(\)]*\s+of\s+C\.?P\.?C\.?',
    r'(?:Section|S\.)\s+\d+[\w\(\)]*\s+of\s+(?:the\s+)?[A-Z][a-zA-Z\s]+(?:Act|Ordinance|Code)',
]


def normalize_citation(raw: str) -> str:
    """Normalize a citation by collapsing spaces in journal names and fixing year."""
    normalized = re.sub(r'\s+', ' ', raw.strip())
    # Normalize spaced journal names to compact (e.g., "C L C" -> "CLC")
    for spaced, compact in JOURNAL_NORMALIZE.items():
        if spaced in normalized:
            normalized = normalized.replace(spaced, compact)
    # Fix 5-digit years like "20011" -> "2011"
    m = re.match(r'^(\d{5})\s+', normalized)
    if m:
        year_str = m.group(1)
        normalized = year_str[:4] + normalized[5:]
    return normalized


def identify_court_from_citation(citation: str) -> str:
    """Identify the court from a citation string."""
    upper = citation.upper()
    # Check journal-implied courts first
    for journal, court in JOURNAL_COURT_MAP.items():
        if journal in upper:
            return court
    # Check PLD citations for court designator (PLD YEAR COURT PAGE)
    pld_match = re.match(r'PLD\s+\d{4}\s+(\w+(?:\s+\w+)?)\s+\d+', citation, re.IGNORECASE)
    if pld_match:
        court_code = pld_match.group(1).strip()
        for code, name in PLD_COURT_CODES.items():
            if court_code.lower() == code.lower():
                return name
    return ""


def extract_citations(text: str) -> list:
    if not text:
        return []
    # Collapse newlines to spaces for matching across line breaks
    text_clean = re.sub(r'\n', ' ', text)
    citations = set()
    # Match compact patterns
    for pattern in CITATION_PATTERNS:
        matches = re.findall(pattern, text_clean, re.IGNORECASE)
        for m in matches:
            citations.add(normalize_citation(m))
    # Match spaced patterns
    for pattern in SPACED_CITATION_PATTERNS:
        matches = re.findall(pattern, text_clean, re.IGNORECASE)
        for m in matches:
            citations.add(normalize_citation(m))
    return list(citations)[:50]


def extract_statutes(text: str) -> list:
    if not text:
        return []
    statutes = set()
    for pattern in STATUTE_PATTERNS[:3]:
        matches = re.findall(pattern, text)
        for m in matches:
            cleaned = re.sub(r'\s+', ' ', m.strip())
            if len(cleaned) > 10 and len(cleaned) < 120:
                statutes.add(cleaned)
    sections = re.findall(r'(?:Section|S\.)\s+\d+[\w\(\)]*(?:\s+of\s+(?:the\s+)?[A-Z][a-zA-Z\s]+(?:Act|Ordinance|Code))?', text)
    for s in sections:
        cleaned = re.sub(r'\s+', ' ', s.strip())
        if len(cleaned) > 5 and len(cleaned) < 120:
            statutes.add(cleaned)
    articles = re.findall(r'Article\s+\d+[\w\(\)]*(?:\s+of\s+(?:the\s+)?Constitution)?', text)
    for a in articles:
        statutes.add(re.sub(r'\s+', ' ', a.strip()))
    return sorted(list(statutes))[:30]


@router.get("/case-citations/{case_id}")
async def get_case_citations(case_id: str):
    """Extract citations, statutes, and cross-references from a case."""
    import time as _time
    t0 = _time.time()

    # Return cached result if available
    if case_id in _citation_cache:
        return _citation_cache[case_id]

    case = await db.pls_caselaws.find_one(
        {"case_id": case_id},
        {"_id": 0, "case_id": 1, "citation": 1, "full_content": 1, "headnotes_text": 1}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    print(f"[citations] fetch case: {_time.time()-t0:.2f}s", flush=True)

    text = ((case.get("full_content") or "")[:15000] + "\n" + (case.get("headnotes_text") or "")[:5000])
    own_citation = case.get("citation", "")

    # 1. Extract case citations from text
    raw_citations = extract_citations(text)
    raw_citations = [c for c in raw_citations if c.upper() != own_citation.upper()]
    print(f"[citations] extract: {_time.time()-t0:.2f}s, found {len(raw_citations)}", flush=True)

    # 2. Batch-lookup cited cases using exact match
    cited_cases = []
    if raw_citations:
        normalized_cits = [re.sub(r'\s+', ' ', c.strip()) for c in raw_citations[:25]]
        # Try exact match first (fast with index)
        found_docs = await db.pls_caselaws.find(
            {"citation": {"$in": normalized_cits}},
            {"_id": 0, "case_id": 1, "citation": 1, "parties": 1, "court": 1, "year": 1}
        ).to_list(length=50)
        print(f"[citations] batch lookup: {_time.time()-t0:.2f}s, matched {len(found_docs)}", flush=True)

        found_map = {doc.get("citation", "").strip(): doc for doc in found_docs}

        for cit in normalized_cits:
            found = found_map.get(cit)
            if found:
                cited_cases.append({
                    "case_id": found["case_id"],
                    "citation": found.get("citation", ""),
                    "parties": found.get("parties", ""),
                    "court": found.get("court", ""),
                    "year": found.get("year"),
                    "matched": True
                })
            else:
                inferred_court = identify_court_from_citation(cit)
                year_match = re.search(r'\b(19|20)\d{2}\b', cit)
                inferred_year = int(year_match.group()) if year_match else None
                cited_cases.append({
                    "citation": cit,
                    "court": inferred_court,
                    "year": inferred_year,
                    "matched": False
                })

    # 3. Find cases that cite this case
    # NOTE: Skipped for now — $regex on full_content across 194K docs is too slow.
    # Requires pre-computed citation links (future background job).
    citing_cases = []

    # 4. Extract statute references
    statutes = extract_statutes(text)

    result = {
        "case_id": case_id,
        "own_citation": own_citation,
        "cited_cases": cited_cases,
        "citing_cases": citing_cases,
        "statutes_referenced": statutes,
        "total_cited": len([c for c in cited_cases if c.get("matched")]),
        "total_citing": len(citing_cases),
        "total_statutes": len(statutes),
    }

    _citation_cache[case_id] = result
    return result
