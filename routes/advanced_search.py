"""
Advanced Search API Routes for PakistanLawApp
=============================================
Multi-field search with filters, facets, and sorting.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from server import db

router = APIRouter()
cases_collection = db["merged_caselaws"]

@router.post("/advanced-search")
async def advanced_search(
    query: Optional[str] = None,
    citation: Optional[str] = None,
    court: Optional[str] = None,
    judge: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    sections: Optional[List[str]] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("relevance", enum=["relevance", "year", "citation"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
):
    """Advanced search with multiple filters."""
    try:
        # Build query filter
        query_filter = {}
        
        if query:
            query_filter["$or"] = [
                {"full_content": {"$regex": query, "$options": "i"}},
                {"headnotes": {"$regex": query, "$options": "i"}},
                {"title": {"$regex": query, "$options": "i"}},
            ]
        
        if citation:
            query_filter["citation"] = {"$regex": citation, "$options": "i"}
        if court:
            query_filter["court"] = {"$regex": court, "$options": "i"}
        if judge:
            query_filter["judges"] = {"$regex": judge, "$options": "i"}
        if year_from or year_to:
            query_filter["year"] = {}
            if year_from:
                query_filter["year"]["$gte"] = year_from
            if year_to:
                query_filter["year"]["$lte"] = year_to
        if sections:
            query_filter["$or"] = query_filter.get("$or", []) + [
                {"full_content": {"$regex": f"Section\\s+{s}", "$options": "i"}} for s in sections
            ]
        
        # Get total count
        total = await cases_collection.estimated_document_count()
        
        # Get results
        skip = (page - 1) * limit
        sort_field = "year" if sort_by == "year" else "citation" if sort_by == "citation" else "_id"
        sort_direction = -1 if sort_order == "desc" else 1
        
        cursor = cases_collection.find(query_filter, {"raw_text": 0, "full_content": 0}).sort(sort_field, sort_direction).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        results = []
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        
        return {
            "results": results,
            "total": total,
            "page": page,
            "limit": limit,
            "filters": {
                "query": query,
                "citation": citation,
                "court": court,
                "judge": judge,
                "year_from": year_from,
                "year_to": year_to,
                "sections": sections,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advanced search failed: {str(e)}")

@router.get("/search/suggestions")
async def search_suggestions(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
):
    """Get search suggestions for autocomplete."""
    try:
        # Find matching citations
        citation_cursor = cases_collection.find(
            {"citation": {"$regex": f"^{q}", "$options": "i"}},
            {"citation": 1, "title": 1}
        ).limit(limit)
        citation_docs = await citation_cursor.to_list(length=limit)
        
        suggestions = []
        for doc in citation_docs:
            suggestions.append({
                "type": "citation",
                "value": doc.get("citation", ""),
                "label": f"{doc.get('citation', '')} - {doc.get('title', '')[:50]}",
            })
        
        # Find matching courts
        court_pipeline = [
            {"$match": {"court": {"$regex": q, "$options": "i"}}},
            {"$group": {"_id": "$court", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]
        court_docs = await cases_collection.aggregate(court_pipeline).to_list(length=limit)
        for doc in court_docs:
            suggestions.append({
                "type": "court",
                "value": doc["_id"],
                "label": f"{doc['_id']} ({doc['count']} cases)",
            })
        
        return {"suggestions": suggestions[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestions failed: {str(e)}")
