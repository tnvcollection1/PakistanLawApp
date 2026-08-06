"""Case Recommender — Voyage AI powered, no GPT dependency."""
from fastapi import APIRouter, HTTPException, Query
from database import db
import os

router = APIRouter()


@router.get("/recommend/similar/{case_id}")
async def recommend_similar(case_id: str, limit: int = Query(10, ge=1)):
    """Find similar cases using Voyage AI semantic similarity."""
    case = await db.pls_caselaws.find_one(
        {"case_id": case_id},
        {"_id": 0, "case_id": 1, "citation": 1, "parties": 1, "headnotes_text": 1, "headnotes": 1}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    search_text = f"{case.get('parties', '')} {(case.get('headnotes_text') or case.get('headnotes') or '')[:500]}"
    
    try:
        from routes.semantic_search import _embed_query, _search_collection
        query_vec = _embed_query(search_text)
        if query_vec is not None:
            results = []
            for src in ['pls_cases', 'eastlaw_cases']:
                try:
                    results.extend(await _search_collection(src, query_vec, limit + 1))
                except Exception:
                    pass
            similar = []
            for r in results:
                if r.get("case_id") != case_id:
                    similar.append({
                        "case_id": r.get("case_id"),
                        "citation": r.get("citation"),
                        "parties": r.get("parties"),
                        "court": r.get("court"),
                        "year": r.get("year"),
                        "similarity": round(r.get("similarity", 0), 3),
                    })
            return {"case_id": case_id, "similar_cases": similar[:limit], "total": len(similar)}
    except Exception as e:
        print(f"Voyage similarity error: {e}")
    
    # Fallback: keyword search
    headnotes = case.get("headnotes_text") or case.get("headnotes") or case.get("parties") or ""
    words = [w for w in headnotes.split() if len(w) > 4][:6]
    if words:
        cursor = db.pls_caselaws.find(
            {"$text": {"$search": " ".join(words)}, "case_id": {"$ne": case_id}},
            {"_id": 0, "case_id": 1, "citation": 1, "parties": 1, "court": 1, "year": 1,
             "score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit)
        results = await cursor.to_list(length=limit)
        return {"case_id": case_id, "similar_cases": results, "total": len(results)}
    
    return {"case_id": case_id, "similar_cases": [], "total": 0}


@router.get("/recommend/by-topic")
async def recommend_by_topic(topic: str = Query(..., min_length=2), limit: int = Query(20, ge=1)):
    """Find cases by topic using Voyage AI semantic search."""
    try:
        from routes.semantic_search import _embed_query, _search_collection
        query_vec = _embed_query(topic)
        if query_vec is not None:
            results = []
            for src in ['pls_cases', 'eastlaw_cases']:
                try:
                    results.extend(await _search_collection(src, query_vec, limit))
                except Exception:
                    pass
            cases = [{
                "case_id": r.get("case_id"),
                "citation": r.get("citation"),
                "parties": r.get("parties"),
                "court": r.get("court"),
                "year": r.get("year"),
                "similarity": round(r.get("similarity", 0), 3),
            } for r in results]
            return {"topic": topic, "cases": cases, "total": len(cases)}
    except Exception as e:
        print(f"Topic search error: {e}")
    
    return {"topic": topic, "cases": [], "total": 0}
