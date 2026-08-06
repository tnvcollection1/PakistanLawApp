"""
Related Cases - Find cases similar to a given case.
"""
from fastapi import APIRouter, HTTPException
from database import db
from bson import ObjectId

router = APIRouter()


@router.get("/cases/{case_id}/related")
async def get_related_cases(case_id: str, limit: int = 5):
    """Find cases related to the given case based on text similarity."""
    case = await db.merged_caselaws.find_one(
        {"_id": ObjectId(case_id)},
        {"citation": 1, "headnotes": 1, "_id": 0},
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    citation = case.get("citation", "")
    if not citation:
        raise HTTPException(status_code=400, detail="Case has no citation for related search")

    # Extract the first part of citation (e.g., "1977" from "1977 SCMR 48")
    # for a fast indexed lookup
    citation_parts = citation.split()
    search_term = citation_parts[0] if citation_parts else citation

    related = []

    # Try $text search with citation (uses idx_fulltext_search)
    try:
        related_cursor = db.merged_caselaws.find(
            {
                "$text": {"$search": citation},
                "_id": {"$ne": ObjectId(case_id)},
            },
            {
                "score": {"$meta": "textScore"},
                "citation": 1,
                "parties": 1,
                "headnotes": 1,
                "year": 1,
                "court": 1,
            },
        ).sort([("score", {"$meta": "textScore"})]).limit(limit)
        related = await related_cursor.to_list(limit)
    except Exception:
        pass

    # Fallback: citation prefix regex (uses idx_citation index)
    if not related:
        try:
            related_cursor = db.merged_caselaws.find(
                {
                    "citation": {"$regex": "^" + search_term, "$options": "i"},
                    "_id": {"$ne": ObjectId(case_id)},
                },
                {
                    "citation": 1,
                    "parties": 1,
                    "headnotes": 1,
                    "year": 1,
                    "court": 1,
                },
            ).limit(limit)
            related = await related_cursor.to_list(limit)
        except Exception:
            pass

    for r in related:
        r["_id"] = str(r["_id"])

    return {
        "case": citation,
        "case_id": case_id,
        "related_cases": related,
    }
