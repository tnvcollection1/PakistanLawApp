"""Citation utilities for PakistanLawApp."""
import re

# Common citation patterns for Pakistani case law
CITATION_PATTERNS = [
    r'\b(\d{4})\s+PLD\s+(\d+)\b',           # PLD citations
    r'\b(\d{4})\s+SCMR\s+(\d+)\b',          # SCMR citations
    r'\b(\d{4})\s+PCrLJ\s+(\d+)\b',        # PCrLJ citations
    r'\b(\d{4})\s+CLD\s+(\d+)\b',          # CLD citations
    r'\b(\d{4})\s+PLC\s+(\d+)\b',         # PLC citations
    r'\b(\d{4})\s+NLR\s+(\d+)\b',          # NLR citations
    r'\b(\d{4})\s+MLD\s+(\d+)\b',          # MLD citations
    r'\b(\d{4})\s+YLR\s+(\d+)\b',          # YLR citations
]

def extract_citations(text):
    """Extract all legal citations from text."""
    citations = []
    for pattern in CITATION_PATTERNS:
        for match in re.finditer(pattern, text):
            citations.append({
                "text": match.group(0),
                "year": match.group(1),
                "page": match.group(2),
                "position": match.start(),
            })
    return citations

def normalize_citation(citation):
    """Normalize a citation for comparison."""
    # Remove extra spaces and standardize format
    normalized = re.sub(r'\s+', ' ', citation.strip())
    return normalized.upper()

def is_valid_citation(citation):
    """Check if a string looks like a valid Pakistani case citation."""
    for pattern in CITATION_PATTERNS:
        if re.search(pattern, citation):
            return True
    return False
