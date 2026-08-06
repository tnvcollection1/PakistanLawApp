"""AI Smart Search - Intelligent legal search."""
import re, json
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from server import db
from bson import ObjectId

router = APIRouter()
cases_collection = db["merged_caselaws"]

class SmartSearchRequest(BaseModel):
    query: str
    filters: Optional[dict] = None
    limit: Optional[int] = 20

@router.post("/ai/smart-search")
async def ai_smart_search(request: SmartSearchRequest):
    """Smart search with AI query understanding."""
    try:
        # Parse query for legal terms
        query = request.query.strip()
        escaped = re.escape(query)
        
        # Build search query
        search_query = {"$or": [
            {"full_content": {"$regex": escaped, "$options": "i"}},
            {"headnotes": {"$regex": escaped, "$options": "i"}},
            {"title": {"$regex": escaped, "$options": "i"}},
            {"citation": {"$regex": escaped, "$options": "i"}},
        ]}
        
        # Apply filters if provided
        if request.filters:
            if request.filters.get("court"):
                search_query["court"] = {"$regex": request.filters["court"], "$options": "i"}
            if request.filters.get("year_from"):
                search_query.setdefault("year", {})["$gte"] = request.filters["year_from"]
            if request.filters.get("year_to"):
                search_query.setdefault("year", {})["$lte"] = request.filters["year_to"]
        
        cursor = cases_collection.find(search_query, {"raw_text": 0, "full_content": 0}).limit(request.limit)
        docs = await cursor.to_list(length=request.limit)
        
        results = []
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        
        return {
            "query": request.query,
            "results": results,
            "total": len(results),
            "filters_applied": request.filters,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart search failed: {str(e)}")
