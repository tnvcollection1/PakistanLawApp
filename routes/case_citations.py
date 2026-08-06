"""Case Citations - Manage and search citations."""
import re
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from server import db
from bson import ObjectId

router = APIRouter()
cases_collection = db["merged_caselaws"]

class CitationSearch(BaseModel):
    citation: str

@router.get("/citations/search")
async def search_citations(
    citation: str = Query(..., description="Citation to search for"),
    limit: int = Query(20, ge=1, le=100),
):
    """Search for a specific citation."""
    try:
        escaped = re.escape(citation.strip())
        regex_query = {"citation": {"$regex": escaped, "$options": "i"}}
        
        cursor = cases_collection.find(regex_query, {"raw_text": 0, "full_content": 0}).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        results = []
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        
        return {
            "citation": citation,
            "results": results,
            "total": len(results),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Citation search failed: {str(e)}")

@router.get("/citations/{case_id}")
async def get_case_citations(case_id: str):
    """Get all citations in a case."""
    try:
        doc = await cases_collection.find_one(
            {"_id": ObjectId(case_id)},
            {"citation": 1, "title": 1, "full_content": 1}
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        
        text = doc.get("full_content", "")
        
        # Extract common citation patterns
        patterns = [
            r'\b(\d{4})\s+PLD\s+(\d+)\b',
            r'\b(\d{4})\s+SCMR\s+(\d+)\b',
            r'\b(\d{4})\s+PCrLJ\s+(\d+)\b',
            r'\b(\d{4})\s+CLD\s+(\d+)\b',
            r'\b(\d{4})\s+PLC\s+(\d+)\b',
            r'\b(\d{4})\s+NLR\s+(\d+)\b',
            r'\b(\d{4})\s+MLD\s+(\d+)\b',
            r'\b(\d{4})\s+YLR\s+(\d+)\b',
        ]
        
        citations = []
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                citations.append(match.group(0))
        
        return {
            "case_id": case_id,
            "citation": doc.get("citation", ""),
            "citations_found": list(set(citations)),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get citations: {str(e)}")
