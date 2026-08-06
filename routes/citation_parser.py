"""
Citation Parser & Cross-Reference System
=========================================
Extracts legal references (sections, cases, terms, courts) from case text.
"""
import re
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from server import db

router = APIRouter()
cases_collection = db["merged_caselaws"]

# Regex patterns for legal references
SECTION_PATTERN = re.compile(r'\b[Ss]ection\s+(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?([A-Z][A-Za-z\s.]+?)(?:\s+\d{4}|\b)', re.IGNORECASE)
CITED_CASE_PATTERN = re.compile(r'\b(\d{4})\s+([A-Z]+)\s+(\d+)\b', re.IGNORECASE)
LEGAL_TERMS = [
    "murder", "theft", "robbery", "fraud", "assault", "bail", "warrant",
    "habeas corpus", "injunction", "trespass", "negligence", "defamation",
    "maintenance", "alimony", "jurisdiction", "precedent", "stare decisis",
]
COURT_NAMES = [
    "Supreme Court", "High Court", "District Court", "Sessions Court",
    "Magistrate Court", "Family Court", "Labour Court", "Anti-Terrorism Court",
    "Federal Shariat Court", "Islamabad High Court", "Lahore High Court",
    "Sindh High Court", "Peshawar High Court", "Balochistan High Court",
]

@router.get("/case/{case_id}/references")
async def get_case_references(case_id: str):
    """Extract all legal references from a case."""
    try:
        doc = await cases_collection.find_one(
            {"_id": ObjectId(case_id)},
            {"full_content": 1, "headnotes": 1, "citation": 1, "title": 1}
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        
        text = doc.get("full_content", "") or doc.get("headnotes", "")
        if not text:
            return {"case_id": case_id, "total_refs": 0, "references": {}}
        
        # Find sections
        sections = []
        for match in SECTION_PATTERN.finditer(text):
            sections.append({
                "text": match.group(0),
                "section": match.group(1),
                "act": match.group(2).strip(),
                "position": match.start(),
            })
        
        # Find cited cases
        cited_cases = []
        for match in CITED_CASE_PATTERN.finditer(text):
            cited_cases.append({
                "text": match.group(0),
                "year": match.group(1),
                "journal": match.group(2),
                "page": match.group(3),
                "position": match.start(),
            })
        
        # Find legal terms
        legal_terms = []
        text_lower = text.lower()
        for term in LEGAL_TERMS:
            for match in re.finditer(r'\b' + re.escape(term) + r'\b', text_lower):
                legal_terms.append({
                    "text": term,
                    "position": match.start(),
                })
        
        # Find courts
        courts = []
        for court in COURT_NAMES:
            for match in re.finditer(r'\b' + re.escape(court) + r'\b', text, re.IGNORECASE):
                courts.append({
                    "text": court,
                    "position": match.start(),
                })
        
        return {
            "case_id": case_id,
            "citation": doc.get("citation", doc.get("title", "")),
            "total_refs": len(sections) + len(cited_cases) + len(legal_terms) + len(courts),
            "references": {
                "sections": sections,
                "cited_cases": cited_cases,
                "legal_terms": legal_terms,
                "courts": courts,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse references: {str(e)}")

@router.get("/case/{case_id}/cross-references")
async def get_cross_references(case_id: str):
    """Build cross-reference network for a case."""
    try:
        doc = await cases_collection.find_one(
            {"_id": ObjectId(case_id)},
            {"full_content": 1, "citation": 1}
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        
        text = doc.get("full_content", "")
        if not text:
            return {"case_id": case_id, "cross_references": []}
        
        # Find all case citations in the text
        citations = []
        for match in CITED_CASE_PATTERN.finditer(text):
            citations.append({
                "citation": match.group(0),
                "year": match.group(1),
                "journal": match.group(2),
                "page": match.group(3),
            })
        
        # Find matching cases in database
        cross_refs = []
        for cite in citations:
            pattern = f"{cite['year']} {cite['journal']} {cite['page']}"
            matches = await cases_collection.find(
                {"citation": {"$regex": pattern, "$options": "i"}}
            ).limit(5).to_list(length=5)
            for match in matches:
                cross_refs.append({
                    "cited_citation": cite["citation"],
                    "case_id": str(match["_id"]),
                    "citation": match.get("citation", ""),
                    "title": match.get("title", ""),
                })
        
        return {"case_id": case_id, "cross_references": cross_refs}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build cross-references: {str(e)}")
