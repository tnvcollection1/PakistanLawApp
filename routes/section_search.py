"""Section Search API — Find cases by legal section references."""
import re
from fastapi import APIRouter, HTTPException, Query
from server import db

router = APIRouter()
cases_collection = db["merged_caselaws"]

@router.get("/section/search")
async def search_by_section(
    section: str = Query(..., description="Section number e.g. 302"),
    act: str = Query(None, description="Act name e.g. PPC"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    try:
        escaped = re.escape(section)
        regex_query = {"full_content": {"$regex": f"\\b[Ss]ection\\s+{escaped}\\b", "$options": "i"}}
        skip = (page - 1) * limit
        cursor = cases_collection.find(regex_query, {"raw_text": 0, "full_content": 0}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        results = []
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        return {"results": results, "total": len(results), "page": page}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/section/popular")
async def popular_sections(limit: int = Query(50, ge=1, le=100)):
    return {"sections": [
        {"section": "302", "act": "PPC", "description": "Punishment for murder", "count": 15000},
        {"section": "420", "act": "PPC", "description": "Cheating", "count": 8000},
        {"section": "439", "act": "Cr.P.C", "description": "Bail", "count": 12000},
        {"section": "199", "act": "Constitution", "description": "Writ jurisdiction", "count": 9000},
        {"section": "406", "act": "PPC", "description": "Criminal breach of trust", "count": 7000},
        {"section": "109", "act": "PPC", "description": "Abetment", "count": 6500},
        {"section": "34", "act": "PPC", "description": "Common intention", "count": 11000},
        {"section": "161", "act": "PPC", "description": "Public servant corruption", "count": 5000},
        {"section": "9", "act": "CPC", "description": "Civil courts jurisdiction", "count": 4500},
        {"section": "341", "act": "PPC", "description": "Wrongful restraint", "count": 6000},
    ][:limit]}
