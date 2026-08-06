
"""
Search Within Case — Search inside a specific case's full text.
"""
import re
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query
from server import db

router = APIRouter()
cases_collection = db["merged_caselaws"]

@router.get("/case/{case_id}/search")
async def search_within_case(
    case_id: str,
    q: str = Query(..., description="Search query"),
):
    """Search within a specific case's full text. Returns highlighted snippets."""
    try:
        doc = await cases_collection.find_one(
            {"_id": ObjectId(case_id)},
            {"full_content": 1, "headnotes": 1, "citation": 1, "title": 1}
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        
        text = doc.get("full_content", "") or doc.get("headnotes", "")
        if not text:
            return {"case_id": case_id, "query": q, "total": 0, "snippets": []}
        
        escaped = re.escape(q.strip())
        pattern = re.compile(escaped, re.IGNORECASE)
        
        snippets = []
        for match in pattern.finditer(text):
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            snippet = text[start:end]
            # Highlight the match
            highlighted = snippet.replace(match.group(0), f"**{match.group(0)}**")
            snippets.append({
                "text": snippet,
                "highlighted": highlighted,
                "position": match.start(),
                "matched_text": match.group(0),
            })
        
        return {
            "case_id": case_id,
            "citation": doc.get("citation", doc.get("title", "")),
            "query": q,
            "total": len(snippets),
            "snippets": snippets[:20],  # Max 20 snippets
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(exc)}")

@router.get("/case/{case_id}")
async def get_case_detail(case_id: str):
    """Get full case details including full_content."""
    try:
        doc = await cases_collection.find_one(
            {"_id": ObjectId(case_id)},
            {"raw_text": 0}  # Exclude raw_text to keep response smaller
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        doc["id"] = str(doc.pop("_id"))
        return doc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load case: {str(exc)}")
