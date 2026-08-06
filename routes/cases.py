"""Cases listing and detail API routes."""
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query
from server import db

router = APIRouter()
cases_collection = db["merged_caselaws"]

def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict."""
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    # Remove large fields from listing
    doc.pop("raw_text", None)
    doc.pop("full_content", None)
    return doc

@router.get("/cases/list")
async def list_cases(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    court: str = Query(None),
    year: int = Query(None),
):
    """List cases with pagination and filtering."""
    try:
        query_filter = {}
        if court:
            query_filter["court"] = {"$regex": court, "$options": "i"}
        if year:
            query_filter["year"] = year
        
        # Use estimated count for performance (fast on MongoDB)
        total = await cases_collection.estimated_document_count()
        
        skip = (page - 1) * limit
        cursor = cases_collection.find(query_filter).sort("year", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        results = [serialize_doc(doc) for doc in docs]
        
        return {
            "data": results,
            "total": total,
            "page": page,
            "limit": limit,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list cases: {str(e)}")

@router.get("/caselaws")
async def get_caselaws(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Get case laws (alias for list_cases)."""
    return await list_cases(page=page, limit=limit)
