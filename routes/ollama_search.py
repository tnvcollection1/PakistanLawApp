"""
Ollama AI Search with PakLawVector (TurboPuffer)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import httpx
import json
import os
import re
import numpy as np
import time

router = APIRouter(prefix="/api/ollama", tags=["Ollama AI"])

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "phi3:mini"
VOYAGE_API_KEY = os.environ.get("VOYAGE_API_KEY", "")

_pak_vector = None


def get_pak_vector():
    global _pak_vector
    if _pak_vector is None:
        try:
            from vector_engine.pak_vector import PakLawVector
            _pak_vector = PakLawVector(dim=1024, max_elements=500000)
            loaded = _pak_vector.load("/var/www/pakistanlawapp/vector_data/pak_vector")
            if loaded:
                print(f"✅ PakLawVector loaded: {_pak_vector.doc_count} vectors")
        except Exception as e:
            print(f"❌ PakLawVector error: {e}")
    return _pak_vector


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5


class ChatRequest(BaseModel):
    message: str


async def get_voyage_embedding(text: str) -> np.ndarray:
    """Get embedding from Voyage AI"""
    print(f"[DEBUG] Getting embedding for: {text[:50]}...")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.voyageai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {VOYAGE_API_KEY}"},
                json={"input": text[:4000], "model": "voyage-law-2"}
            )
            print(f"[DEBUG] Voyage response: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                return np.array(data["data"][0]["embedding"], dtype=np.float32)
            else:
                print(f"[DEBUG] Voyage error: {response.text[:100]}")
    except Exception as e:
        print(f"[DEBUG] Voyage exception: {e}")
    return None


async def search_with_pakvector(query: str, limit: int = 5) -> List[Dict]:
    """Vector search using PakLawVector"""
    from database import db
    
    pak_vector = get_pak_vector()
    if pak_vector is None:
        print("[DEBUG] PakLawVector not available")
        return []
    
    # Get embedding
    query_vec = await get_voyage_embedding(query)
    if query_vec is None:
        print("[DEBUG] No embedding returned")
        return []
    
    print(f"[DEBUG] Embedding dim: {len(query_vec)}")
    
    # Search
    t0 = time.time()
    results = pak_vector.search(query_vec, k=limit, use_cache=True)
    print(f"[DEBUG] PakLawVector search: {(time.time()-t0)*1000:.2f}ms, {len(results)} results")
    
    if not results:
        return []
    
    # Get details
    case_ids = [r['doc_id'] for r in results]
    score_map = {r['doc_id']: r['score'] for r in results}
    
    cases = await db.pls_caselaws.find(
        {"case_id": {"$in": case_ids}},
        {"_id": 0, "case_id": 1, "citation": 1, "parties": 1,
         "court": 1, "year": 1, "judge": 1, "headnotes": 1, "headnotes_text": 1}
    ).to_list(limit)
    
    for case in cases:
        case['relevance_score'] = round(score_map.get(case['case_id'], 0), 3)
        case['headnotes'] = (case.get('headnotes_text') or case.get('headnotes') or '')[:400]
        if 'headnotes_text' in case:
            del case['headnotes_text']
    
    cases.sort(key=lambda x: -x.get('relevance_score', 0))
    return cases


async def search_keyword_fallback(query: str, limit: int = 5) -> List[Dict]:
    """Keyword search fallback"""
    from database import db
    
    terms = query.lower().split()[:5]
    regex = "|".join(re.escape(t) for t in terms)
    
    cursor = db.pls_caselaws.find(
        {"$or": [
            {"headnotes": {"$regex": regex, "$options": "i"}},
            {"headnotes_text": {"$regex": regex, "$options": "i"}}
        ]},
        {"_id": 0, "case_id": 1, "citation": 1, "parties": 1,
         "court": 1, "year": 1, "headnotes": 1, "headnotes_text": 1}
    ).limit(limit)
    
    cases = await cursor.to_list(limit)
    for case in cases:
        case['headnotes'] = (case.get('headnotes_text') or case.get('headnotes') or '')[:400]
        case['relevance_score'] = 0.5
        if 'headnotes_text' in case:
            del case['headnotes_text']
    return cases


async def generate_answer(query: str, cases: List[Dict]):
    """Generate AI answer with Ollama"""
    context = ""
    for i, case in enumerate(cases[:3], 1):
        context += f"\nCase {i}: {case.get('citation', 'N/A')}\n{case.get('headnotes', '')[:300]}\n"

    prompt = f"""Answer this Pakistani legal question:
Question: {query}
Cases:
{context}
Brief answer with citations:"""

    try:
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
            )
            if response.status_code == 200:
                return response.json().get("response", "")
    except Exception as e:
        print(f"Ollama error: {e}")
    return None


@router.post("/search/fast")
async def fast_search(request: SearchRequest):
    """Fast vector search (no AI answer)"""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query required")
    
    t0 = time.time()
    
    # Try vector search
    cases = await search_with_pakvector(request.query.strip(), request.limit)
    search_method = "vector" if cases else "keyword"
    
    # Fallback
    if not cases:
        cases = await search_keyword_fallback(request.query.strip(), request.limit)
        search_method = "keyword"
    
    search_time = time.time() - t0
    pak_vector = get_pak_vector()
    stats = pak_vector.get_stats() if pak_vector else {}
    
    return {
        "query": request.query,
        "cases": cases,
        "total": len(cases),
        "search_method": search_method,
        "search_time_ms": round(search_time * 1000, 2),
        "cache_hit_rate": f"{stats.get('cache_hit_rate', 0)}%"
    }


@router.post("/search")
async def ollama_search(request: SearchRequest):
    """Full search with AI answer"""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query required")
    
    # Vector search
    cases = await search_with_pakvector(request.query.strip(), request.limit)
    search_method = "vector" if cases else "keyword"
    
    if not cases:
        cases = await search_keyword_fallback(request.query.strip(), request.limit)
        search_method = "keyword"
    
    # AI answer
    answer = await generate_answer(request.query, cases)
    
    return {
        "query": request.query,
        "ai_answer": answer,
        "cases": cases,
        "total": len(cases),
        "model": OLLAMA_MODEL,
        "search_method": search_method
    }


@router.post("/chat")
async def ollama_chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message required")
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": f"Pakistani legal expert: {request.message}", "stream": False}
            )
            if response.status_code == 200:
                return {"response": response.json().get("response", ""), "model": OLLAMA_MODEL}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def status():
    result = {"ollama": "unknown", "pakvector": "unknown"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            if response.status_code == 200:
                result["ollama"] = "running"
                result["models"] = [m["name"] for m in response.json().get("models", [])]
    except:
        result["ollama"] = "error"
    
    pak_vector = get_pak_vector()
    if pak_vector:
        result["pakvector"] = "running"
        result["vector_stats"] = pak_vector.get_stats()
    return result


# Pre-load
print("Pre-loading PakLawVector...")
_startup_pv = get_pak_vector()
