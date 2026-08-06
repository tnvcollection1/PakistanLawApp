"""Urdu Language Support — Regex search, no GPT translation."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import db
import re

router = APIRouter()


class TranslateRequest(BaseModel):
    text: str
    direction: Optional[str] = "urdu_to_english"


class UrduSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 50


@router.post("/urdu/translate")
async def translate_text(req: TranslateRequest):
    """Basic Urdu keyword mapping — no GPT translation."""
    return {
        "original": req.text,
        "translated": req.text,  # Pass-through — no GPT available
        "note": "Full translation requires a translation API. Urdu text can be used directly in search.",
    }


@router.post("/urdu/search")
async def urdu_search(req: UrduSearchRequest):
    """Search cases using Urdu or transliterated text."""
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query is empty")
    
    results = []
    
    # Direct Voyage AI semantic search (handles multilingual text)
    try:
        from routes.semantic_search import _embed_query, _search_collection
        vec = _embed_query(query)
        if vec is not None:
            semantic_results = await _search_collection("cases", vec, req.limit)
            for r in semantic_results:
                results.append({
                    "case_id": r.get("case_id"),
                    "citation": r.get("citation"),
                    "parties": r.get("parties"),
                    "court": r.get("court"),
                    "year": r.get("year"),
                    "similarity": round(r.get("similarity", 0), 3),
                    "_search_method": "semantic",
                })
    except Exception as e:
        print(f"Urdu semantic search error: {e}")
    
    # Keyword fallback
    if not results:
        try:
            cursor = db.pls_caselaws.find(
                {"$or": [
                    {"parties": {"$regex": re.escape(query), "$options": "i"}},
                    {"full_content": {"$regex": re.escape(query), "$options": "i"}},
                ]},
                {"_id": 0, "case_id": 1, "citation": 1, "parties": 1, "court": 1, "year": 1}
            ).limit(req.limit)
            kw_results = await cursor.to_list(req.limit)
            for r in kw_results:
                r["_search_method"] = "keyword"
                results.append(r)
        except Exception:
            pass
    
    return {"query": query, "results": results, "total": len(results)}
