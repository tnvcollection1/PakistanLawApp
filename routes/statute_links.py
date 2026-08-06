"""
Statute-Case Cross-Reference API Routes

Provides endpoints to query the statute-to-case links built by the
cross-reference builder script.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from database import db

router = APIRouter()


@router.get("/statute-links/search")
async def search_statute_links(
    statute: str = Query(..., min_length=2, description="Statute name to search"),
    section: Optional[str] = Query(None, description="Specific section number"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Search for cases linked to a statute/section."""
    query = {"statute": {"$regex": statute, "$options": "i"}}
    
    if section:
        query["section"] = {"$regex": f"^{section}", "$options": "i"}
    
    skip = (page - 1) * limit
    
    cursor = db.statute_case_links.find(query, {"_id": 0}).sort([
        ("year", -1),
        ("case_id", -1)
    ]).skip(skip).limit(limit)
    
    results = await cursor.to_list(length=limit)
    total = await db.statute_case_links.count_documents(query)
    
    return {
        "data": results,
        "total": total,
        "page": page,
        "limit": limit,
        "statute_query": statute,
        "section_query": section
    }


@router.get("/statute-links/statutes")
async def list_linked_statutes(
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    """List all statutes that have case links."""
    match_stage = {}
    if keyword:
        match_stage = {"statute": {"$regex": keyword, "$options": "i"}}
    
    pipeline = [
        {"$match": match_stage} if match_stage else {"$match": {}},
        {"$group": {
            "_id": "$statute",
            "case_count": {"$sum": 1},
            "sections": {"$addToSet": "$section"},
        }},
        {"$project": {
            "statute": "$_id",
            "case_count": 1,
            "section_count": {"$size": "$sections"},
            "_id": 0
        }},
        {"$sort": {"case_count": -1}},
        {"$skip": (page - 1) * limit},
        {"$limit": limit},
    ]
    
    cursor = db.statute_case_links.aggregate(pipeline)
    results = await cursor.to_list(length=limit)
    
    # Get total count
    count_pipeline = [
        {"$match": match_stage} if match_stage else {"$match": {}},
        {"$group": {"_id": "$statute"}},
        {"$count": "total"}
    ]
    count_result = await db.statute_case_links.aggregate(count_pipeline).to_list(1)
    total = count_result[0]["total"] if count_result else 0
    
    return {
        "data": results,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/statute-links/sections/{statute}")
async def get_statute_sections(
    statute: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    """Get all sections of a statute that have case links."""
    pipeline = [
        {"$match": {"statute": {"$regex": f"^{statute}$", "$options": "i"}}},
        {"$group": {
            "_id": "$section",
            "case_count": {"$sum": 1},
            "sample_cases": {"$push": {
                "case_id": "$case_id",
                "parties": "$parties",
                "year": "$year",
                "court": "$court"
            }},
        }},
        {"$project": {
            "section": "$_id",
            "case_count": 1,
            "sample_cases": {"$slice": ["$sample_cases", 3]},
            "_id": 0
        }},
        {"$sort": {"case_count": -1}},
        {"$skip": (page - 1) * limit},
        {"$limit": limit},
    ]
    
    cursor = db.statute_case_links.aggregate(pipeline)
    results = await cursor.to_list(length=limit)
    
    # Get total sections
    count_pipeline = [
        {"$match": {"statute": {"$regex": f"^{statute}$", "$options": "i"}}},
        {"$group": {"_id": "$section"}},
        {"$count": "total"}
    ]
    count_result = await db.statute_case_links.aggregate(count_pipeline).to_list(1)
    total = count_result[0]["total"] if count_result else 0
    
    return {
        "data": results,
        "total": total,
        "statute": statute,
        "page": page,
        "limit": limit
    }


@router.get("/statute-links/cases/{statute}/{section}")
async def get_section_cases(
    statute: str,
    section: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    court: Optional[str] = None,
):
    """Get all cases linked to a specific statute section."""
    import re as _re
    # Strip year, amendment/ordinance suffix to match base act name
    statute_base = _re.sub(r"\s+\d{4}$", "", statute).strip()
    statute_base = _re.sub(r"\s*\(Amendment\).*$", "", statute_base, flags=_re.IGNORECASE).strip()
    statute_base = _re.sub(r"\s*\(Second Amendment\).*$", "", statute_base, flags=_re.IGNORECASE).strip()
    query = {
        "statute": {"$regex": f"^{_re.escape(statute_base)}", "$options": "i"},
        "section": section
    }
    
    if year_from or year_to:
        year_q = {}
        if year_from:
            year_q["$gte"] = year_from
        if year_to:
            year_q["$lte"] = year_to
        query["year"] = year_q
    
    if court:
        query["court"] = {"$regex": court, "$options": "i"}
    
    skip = (page - 1) * limit
    
    cursor = db.statute_case_links.find(query, {"_id": 0}).sort([
        ("year", -1),
        ("case_id", -1)
    ]).skip(skip).limit(limit)
    
    results = await cursor.to_list(length=limit)
    total = await db.statute_case_links.count_documents(query)
    
    # Enrich with full case details if needed
    case_ids = [r["case_id"] for r in results]
    cases_cursor = db.pls_caselaws.find(
        {"case_id": {"$in": case_ids}},
        {"_id": 0, "case_id": 1, "parties": 1, "court": 1, "year": 1, 
         "judge": 1, "headnotes": 1, "citation": 1}
    )
    cases_map = {c["case_id"]: c async for c in cases_cursor}
    
    enriched = []
    for r in results:
        case_detail = cases_map.get(r["case_id"], {})
        enriched.append({
            **r,
            "full_parties": case_detail.get("parties", r.get("parties", "")),
            "judge": case_detail.get("judge", ""),
            "citation": case_detail.get("citation", ""),
            "headnotes_preview": (case_detail.get("headnotes", "") or "")[:300],
        })
    
    return {
        "data": enriched,
        "total": total,
        "statute": statute,
        "section": section,
        "page": page,
        "limit": limit
    }


@router.get("/statute-links/suggest")
async def suggest_statutes(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=20),
):
    """Autocomplete suggestions for statute names."""
    pipeline = [
        {"$match": {"statute": {"$regex": q, "$options": "i"}}},
        {"$group": {
            "_id": "$statute",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {"$project": {"statute": "$_id", "count": 1, "_id": 0}}
    ]
    
    cursor = db.statute_case_links.aggregate(pipeline)
    results = await cursor.to_list(length=limit)
    
    return {"suggestions": results}


@router.get("/statute-links/stats")
async def get_statute_links_stats():
    """Get statistics about statute-case links."""
    total_links = await db.statute_case_links.count_documents({})
    
    if total_links == 0:
        return {
            "status": "not_built",
            "message": "Statute-case links have not been built yet. Run the build script first.",
            "total_links": 0
        }
    
    # Top statutes
    top_statutes_pipeline = [
        {"$group": {"_id": "$statute", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_statutes = await db.statute_case_links.aggregate(top_statutes_pipeline).to_list(10)
    
    # Unique statutes count
    unique_statutes = await db.statute_case_links.distinct("statute")
    
    # Year distribution
    year_pipeline = [
        {"$match": {"year": {"$exists": True, "$ne": None}}},
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"_id": -1}},
        {"$limit": 10}
    ]
    year_dist = await db.statute_case_links.aggregate(year_pipeline).to_list(10)
    
    return {
        "status": "ready",
        "total_links": total_links,
        "unique_statutes": len(unique_statutes),
        "top_statutes": [{"statute": s["_id"], "count": s["count"]} for s in top_statutes],
        "recent_years": [{"year": y["_id"], "count": y["count"]} for y in year_dist],
    }


@router.get("/statute-links/case/{case_id}")
async def get_case_statute_links(case_id: str):
    """Get all statute references found in a specific case."""
    cursor = db.statute_case_links.find(
        {"case_id": case_id},
        {"_id": 0, "statute": 1, "section": 1}
    )
    
    results = await cursor.to_list(length=100)
    
    return {
        "case_id": case_id,
        "statute_references": results,
        "count": len(results)
    }
