"""Citator - Check if a case has been cited."""
from fastapi import APIRouter, HTTPException, Query
from server import db
from bson import ObjectId
import re

router = APIRouter()
cases_collection = db["merged_caselaws"]

@router.get("/citator/{case_id}")
async def citator_check(case_id: str):
    """Check if a case has been cited by other cases."""
    try:
        doc = await cases_collection.find_one(
            {"_id": ObjectId(case_id)},
            {"citation": 1, "title": 1}
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        
        citation = doc.get("citation", "")
        if not citation:
            return {
                "case_id": case_id,
                "citation": "",
                "cited_by": [],
                "cited_by_count": 0,
            }
        
        # Search for this citation in other cases
        escaped = re.escape(citation)
        regex_query = {"full_content": {"$regex": escaped, "$options": "i"}}
        
        cursor = cases_collection.find(regex_query, {"raw_text": 0, "full_content": 0}).limit(50)
        docs = await cursor.to_list(length=50)
        
        cited_by = []
        for d in docs:
            if str(d["_id"]) != case_id:
                cited_by.append({
                    "id": str(d["_id"]),
                    "citation": d.get("citation", ""),
                    "title": d.get("title", ""),
                })
        
        return {
            "case_id": case_id,
            "citation": citation,
            "cited_by_count": len(cited_by),
            "cited_by": cited_by,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Citator check failed: {str(e)}")
