"""Citation Network - Build and analyze citation networks."""
import re
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from server import db
from bson import ObjectId

router = APIRouter()
cases_collection = db["merged_caselaws"]

class NetworkRequest(BaseModel):
    case_id: str
    depth: int = 2

@router.get("/citation-network/{case_id}")
async def get_citation_network(
    case_id: str,
    depth: int = Query(2, ge=1, le=5),
):
    """Get citation network for a case."""
    try:
        doc = await cases_collection.find_one(
            {"_id": ObjectId(case_id)},
            {"full_content": 1, "citation": 1, "title": 1}
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        
        text = doc.get("full_content", "")
        citation = doc.get("citation", "")
        
        # Find cited cases in the text
        cited_pattern = re.compile(r'\b(\d{4})\s+([A-Z]+)\s+(\d+)\b')
        citations = []
        for match in cited_pattern.finditer(text):
            citations.append({
                "text": match.group(0),
                "year": match.group(1),
                "journal": match.group(2),
                "page": match.group(3),
            })
        
        return {
            "case_id": case_id,
            "citation": citation,
            "title": doc.get("title", ""),
            "citations_count": len(citations),
            "citations": citations[:50],  # Limit to 50
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get citation network: {str(e)}")
