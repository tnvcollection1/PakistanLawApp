"""Black's Law Dictionary integration."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

# Common legal terms dictionary
LEGAL_TERMS = {
    "ab initio": "From the beginning.",
    "actus reus": "The guilty act or wrongful deed that constitutes the physical component of a crime.",
    "ad hoc": "For this particular purpose; specially.",
    "ad valorem": "According to value (used of taxation).",
    "affidavit": "A written statement confirmed by oath or affirmation, for use as evidence in court.",
    "alibi": "A claim or piece of evidence that one was elsewhere when an act, typically a criminal one, is alleged to have taken place.",
    "amicus curiae": "An impartial adviser, often voluntary, to a court of law in a particular case.",
    "bona fide": "Genuine; real; sincere; without intention to deceive.",
    "caveat emptor": "Let the buyer beware.",
    "corpus delicti": "The facts and circumstances constituting a crime.",
    "de facto": "In fact, whether by right or not.",
    "de jure": "By right; according to law.",
    "ex parte": "On behalf of one side only in a dispute.",
    "habeas corpus": "A writ requiring a person under arrest to be brought before a judge or into court.",
    "in camera": "In private; in chambers.",
    "ipso facto": "By the fact itself; by that very fact.",
    "mens rea": "The intention or knowledge of wrongdoing that constitutes part of a crime.",
    "modus operandi": "A particular mode of working; a method of operation.",
    "nolo contendere": "A plea by which a defendant in a criminal prosecution accepts conviction but does not plead guilty.",
    "prima facie": "At first sight; on the face of it.",
    "pro bono": "For the public good; undertaken without charge.",
    "pro se": "On one's own behalf; representing oneself.",
    "stare decisis": "The legal principle of determining points in litigation according to precedent.",
    "subpoena": "A writ ordering a person to attend a court.",
    "ultra vires": "Beyond one's legal power or authority.",
}

@router.get("/blacks-law/search")
async def search_blacks_law(term: str = Query(..., min_length=1)):
    """Search Black's Law Dictionary for a term."""
    try:
        term_lower = term.lower()
        results = []
        for key, definition in LEGAL_TERMS.items():
            if term_lower in key or term_lower in definition.lower():
                results.append({"term": key, "definition": definition})
        
        return {"term": term, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/blacks-law/term/{term}")
async def get_term_definition(term: str):
    """Get the definition of a specific legal term."""
    try:
        term_lower = term.lower()
        definition = LEGAL_TERMS.get(term_lower)
        if not definition:
            # Try partial match
            for key, value in LEGAL_TERMS.items():
                if term_lower in key:
                    definition = value
                    term = key
                    break
        
        if not definition:
            raise HTTPException(status_code=404, detail=f"Term '{term}' not found")
        
        return {"term": term, "definition": definition}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get definition: {str(e)}")

@router.get("/blacks-law/terms")
async def list_terms():
    """List all available legal terms."""
    return {"terms": [{"term": k, "definition": v} for k, v in LEGAL_TERMS.items()]}
