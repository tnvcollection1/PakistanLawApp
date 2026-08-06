"""Citations - General citation management."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from server import db
from bson import ObjectId
import re

router = APIRouter()
cases_collection = db["merged_caselaws"]

class CitationFormat(BaseModel):
    style: str = "bluebook"  # bluebook, apa, mla, chicago
    case_id: str

@router.get("/citations/format")
async def format_citation(
    case_id: str = Query(...),
    style: str = Query("bluebook"),
):
    """Format a citation in a specific style."""
    try:
        doc = await cases_collection.find_one(
            {"_id": ObjectId(case_id)},
            {"citation": 1, "title": 1, "year": 1, "court": 1, "page": 1}
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        
        citation = doc.get("citation", "")
        title = doc.get("title", "")
        year = doc.get("year", "")
        court = doc.get("court", "")
        
        if style == "bluebook":
            formatted = f"{title}, {citation} ({year})."
        elif style == "apa":
            formatted = f"{title} ({year}). {court}."
        elif style == "mla":
            formatted = f'"{title}." {court}, {year}.'
        elif style == "chicago":
            formatted = f'{title}. {court}. {year}.'
        else:
            formatted = citation
        
        return {
            "case_id": case_id,
            "style": style,
            "formatted": formatted,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to format citation: {str(e)}")
