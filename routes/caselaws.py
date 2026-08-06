"""Caselaws - Browse and search case laws."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from server import db
from bson import ObjectId

router = APIRouter()
cases_collection = db["merged_caselaws"]

@router.get("/caselaws/browse")
async def browse_caselaws(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    court: str = Query(None),
    year: int = Query(None),
):
    """Browse case laws with pagination."""
    try:
        query_filter = {}
        if court:
            query_filter["court"] = {"$regex": court, "$options": "i"}
        if year:
            query_filter["year"] = year
        
        total = await cases_collection.estimated_document_count()
        skip = (page - 1) * limit
        
        cursor = cases_collection.find(query_filter, {"raw_text": 0, "full_content": 0}).sort("year", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        results = []
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        
        return {
            "data": results,
            "total": total,
            "page": page,
            "limit": limit,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to browse caselaws: {str(e)}")

@router.get("/caselaws/{case_id}")
async def get_caselaw(case_id: str):
    """Get a specific case law."""
    try:
        doc = await cases_collection.find_one(
            {"_id": ObjectId(case_id)},
            {"raw_text": 0}
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        
        doc["id"] = str(doc.pop("_id"))
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get caselaw: {str(e)}")

@router.get("/caselaws/court/{court}")
async def get_caselaws_by_court(
    court: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Get case laws by court."""
    try:
        query_filter = {"court": {"$regex": court, "$options": "i"}}
        total = await cases_collection.count_documents(query_filter)
        skip = (page - 1) * limit
        
        cursor = cases_collection.find(query_filter, {"raw_text": 0, "full_content": 0}).sort("year", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        results = []
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        
        return {
            "data": results,
            "total": total,
            "page": page,
            "limit": limit,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get caselaws by court: {str(e)}")
