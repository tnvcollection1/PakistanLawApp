"""AI Case Finder - Find similar cases using AI."""
import os, json, re
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from server import db
from bson import ObjectId

router = APIRouter()
cases_collection = db["merged_caselaws"]

class CaseFinderRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

@router.post("/ai/case-finder")
async def ai_case_finder(request: CaseFinderRequest):
    """Find cases using AI-powered semantic search."""
    try:
        # Use regex search for now
        escaped = re.escape(request.query.strip())
        regex_query = {"$or": [
            {"full_content": {"$regex": escaped, "$options": "i"}},
            {"headnotes": {"$regex": escaped, "$options": "i"}},
            {"title": {"$regex": escaped, "$options": "i"}},
        ]}
        
        cursor = cases_collection.find(regex_query, {"raw_text": 0, "full_content": 0}).limit(request.limit)
        docs = await cursor.to_list(length=request.limit)
        
        results = []
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        
        return {
            "query": request.query,
            "results": results,
            "total": len(results),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Case finder failed: {str(e)}")

@router.get("/ai/case-finder")
async def ai_case_finder_get(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50),
):
    """GET endpoint for AI case finder."""
    return await ai_case_finder(CaseFinderRequest(query=q, limit=limit))
