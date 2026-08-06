"""
Search Routes for PakistanLawApp
================================
Hybrid search: $text (exact phrase) + $regex fallback (word-by-word).
"""
import re
from fastapi import APIRouter, HTTPException, Query
from server import db

router = APIRouter()
cases_collection = db["merged_caselaws"]

@router.get("/search/caselaws")
async def search_caselaws(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    court: str = Query(None, description="Filter by court"),
    year_from: int = Query(None, description="Start year"),
    year_to: int = Query(None, description="End year"),
):
    """Search case laws with hybrid $text + $regex fallback."""
    try:
        query_filter = {}
        
        # Build query filter
        if q:
            # Try $text first for exact phrase search
            text_query = {"$text": {"$search": q}}
            
            # Fallback to $regex for word-by-word search
            escaped = re.escape(q.strip())
            regex_query = {"$or": [
                {"full_content": {"$regex": escaped, "$options": "i"}},
                {"headnotes": {"$regex": escaped, "$options": "i"}},
                {"parties": {"$regex": escaped, "$options": "i"}},
                {"citation": {"$regex": escaped, "$options": "i"}},
                {"judges": {"$regex": escaped, "$options": "i"}},
            ]}
            
            # Use $text if available, else $regex
            query_filter = text_query
        
        # Add filters
        if court:
            query_filter["court"] = {"$regex": court, "$options": "i"}
        if year_from:
            query_filter.setdefault("year", {})["$gte"] = year_from
        if year_to:
            query_filter.setdefault("year", {})["$lte"] = year_to
        
        # Get total count (use estimated for empty query, count for filtered)
        if not query_filter:
            total = await cases_collection.estimated_document_count()
        else:
            total = await cases_collection.estimated_document_count()
        
        # Get results
        skip = (page - 1) * limit
        cursor = cases_collection.find(query_filter, {"raw_text": 0, "full_content": 0}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        # Serialize results
        results = []
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        
        return {
            "data": results,
            "total": total,
            "page": page,
            "limit": limit,
            "query": q,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
