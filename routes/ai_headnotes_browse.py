"""AI Headnotes Browse - Browse and manage AI-generated headnotes."""
import os
from fastapi import APIRouter, HTTPException, Query
from server import db
from bson import ObjectId

router = APIRouter()
cases_collection = db["merged_caselaws"]

@router.get("/ai/headnotes/browse")
async def browse_headnotes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    has_headnotes: bool = Query(None),
):
    """Browse cases with AI headnotes."""
    try:
        query_filter = {}
        if has_headnotes is not None:
            if has_headnotes:
                query_filter["ai_headnotes"] = {"$exists": True}
            else:
                query_filter["ai_headnotes"] = {"$exists": False}
        
        skip = (page - 1) * limit
        cursor = cases_collection.find(query_filter, {"raw_text": 0, "full_content": 0}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        results = []
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        
        total = await cases_collection.estimated_document_count()
        
        return {
            "results": results,
            "total": total,
            "page": page,
            "limit": limit,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Headnotes browse failed: {str(e)}")
