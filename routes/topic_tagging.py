"""
AI Topic Auto-Tagging using Voyage AI.
Auto-tags cases with legal topics by comparing case embeddings to topic embeddings.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from database import db
from bson import ObjectId
import os
import numpy as np
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

VOYAGE_KEY = os.environ.get('VOYAGE_API_KEY')

# Pakistani legal topics for auto-tagging
LEGAL_TOPICS = [
    "Constitutional Law",
    "Criminal Law",
    "Civil Law",
    "Family Law",
    "Property Law",
    "Banking & Finance Law",
    "Service / Employment Law",
    "Tax Law",
    "Corporate / Company Law",
    "Contract Law",
    "Tort Law",
    "Environmental Law",
    "Intellectual Property Law",
    "Labour Law",
    "Land Revenue & Tenancy Law",
    "Insurance Law",
    "Customs & Excise Law",
    "Election Law",
    "Human Rights",
    "Administrative Law",
    "International Law",
    "Islamic / Sharia Law",
    "Media & Press Law",
    "Cyber Crime / IT Law",
    "Immigration Law",
    "Arbitration & ADR",
    "Consumer Protection",
    "Education Law",
    "Military / Martial Law",
    "Anti-Terrorism Law",
    "Narcotics / Drug Law",
    "Motor Vehicle / Accident Law",
    "Rent & Tenancy Law",
    "Pre-emption Law",
    "Succession & Inheritance Law",
    "Bail & Remand",
    "Habeas Corpus",
    "Writ Jurisdiction",
    "Contempt of Court",
    "Evidence Law",
    "Limitation Law",
]

# Cached topic embeddings
_topic_embeddings = None
_voyage_client = None


def _get_voyage():
    global _voyage_client
    if _voyage_client is None:
        import voyageai
        _voyage_client = voyageai.Client(api_key=VOYAGE_KEY)
    return _voyage_client


def _get_topic_embeddings():
    """Compute and cache topic embeddings."""
    global _topic_embeddings
    if _topic_embeddings is not None:
        return _topic_embeddings

    try:
        vo = _get_voyage()
        result = vo.embed(LEGAL_TOPICS, model='voyage-law-2', input_type='document')
        _topic_embeddings = np.array(result.embeddings, dtype='float32')
        # Normalize
        norms = np.linalg.norm(_topic_embeddings, axis=1, keepdims=True)
        _topic_embeddings = _topic_embeddings / norms
        logger.info(f"Cached {len(LEGAL_TOPICS)} topic embeddings")
        return _topic_embeddings
    except Exception as e:
        logger.error(f"Failed to embed topics: {e}")
        return None


@router.get("/topic-tagging/topics")
async def get_all_topics():
    """Get all available legal topics."""
    return {"topics": LEGAL_TOPICS, "count": len(LEGAL_TOPICS)}


@router.get("/topic-tagging/case/{case_id}")
async def tag_case(case_id: str, top_k: int = Query(5, ge=1, le=15)):
    """Auto-tag a single case with legal topics using Voyage AI."""
    if not VOYAGE_KEY:
        raise HTTPException(status_code=503, detail="Voyage AI not configured")

    # Get case data
    case = await db.pls_caselaws.find_one(
        {"case_id": case_id},
        {"_id": 0, "case_id": 1, "citation": 1, "parties": 1, "court": 1,
         "year": 1, "headnotes_text": 1, "headnotes": 1}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    text = f"{case.get('citation', '')} {case.get('parties', '')} {(case.get('headnotes_text') or case.get('headnotes') or '')[:3000]}"

    topic_embs = _get_topic_embeddings()
    if topic_embs is None:
        raise HTTPException(status_code=503, detail="Topic embeddings unavailable")

    try:
        vo = _get_voyage()
        result = vo.embed([text[:8000]], model='voyage-law-2', input_type='query')
        case_vec = np.array(result.embeddings[0], dtype='float32')
        case_vec = case_vec / np.linalg.norm(case_vec)

        # Compute cosine similarity with all topics
        similarities = np.dot(topic_embs, case_vec)
        top_indices = np.argsort(similarities)[::-1][:top_k]

        tags = []
        for idx in top_indices:
            tags.append({
                "topic": LEGAL_TOPICS[idx],
                "confidence": round(float(similarities[idx]), 4),
            })

        # Save tags to DB
        await db.pls_caselaws.update_one(
            {"case_id": case_id},
            {"$set": {"ai_topics": [t["topic"] for t in tags], "ai_topic_scores": tags}}
        )

        return {
            "case_id": case_id,
            "citation": case.get("citation"),
            "tags": tags,
        }
    except Exception as e:
        logger.error(f"Tagging error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/topic-tagging/batch")
async def batch_tag_cases(limit: int = Query(5000, ge=1, le=50000)):
    """Batch auto-tag cases using EXISTING FAISS vectors — zero Voyage AI token cost."""
    if not VOYAGE_KEY:
        raise HTTPException(status_code=503, detail="Voyage AI not configured")

    topic_embs = _get_topic_embeddings()
    if topic_embs is None:
        raise HTTPException(status_code=503, detail="Topic embeddings unavailable")

    # Load existing FAISS index + doc_ids
    try:
        from routes.semantic_search import _load_index, _indexes, _doc_ids
        if not _load_index('cases'):
            raise HTTPException(status_code=503, detail="FAISS index not loaded")

        index = _indexes['cases']
        doc_ids = _doc_ids['cases']
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"FAISS unavailable: {e}")

    # Find untagged case_ids
    cursor = db.pls_caselaws.find(
        {"ai_topics": {"$exists": False}},
        {"_id": 1, "case_id": 1}
    ).limit(limit)
    untagged = await cursor.to_list(length=limit)

    if not untagged:
        return {"message": "All cases already tagged", "tagged": 0, "tokens_used": 0}

    # Build a mapping from doc_id string to FAISS index position
    id_to_idx = {did: i for i, did in enumerate(doc_ids)}

    tagged_count = 0
    batch_size = 500
    from bson import ObjectId

    for i in range(0, len(untagged), batch_size):
        batch = untagged[i:i + batch_size]
        ops = []

        for case in batch:
            oid = str(case["_id"])
            case_id = case.get("case_id")
            if not case_id:
                continue
            faiss_idx = id_to_idx.get(oid)
            if faiss_idx is None:
                continue

            # Reconstruct vector from FAISS
            vec = index.reconstruct(int(faiss_idx)).astype('float32')
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm

            # Compute similarity against all topics
            sims = np.dot(topic_embs, vec)
            top_indices = np.argsort(sims)[::-1][:5]
            tags = [
                {"topic": LEGAL_TOPICS[idx], "confidence": round(float(sims[idx]), 4)}
                for idx in top_indices
            ]

            ops.append({
                "case_id": case_id,
                "ai_topics": [t["topic"] for t in tags],
                "ai_topic_scores": tags,
            })

        # Bulk update MongoDB
        if ops:
            from pymongo import UpdateOne
            bulk = [
                UpdateOne(
                    {"case_id": op["case_id"]},
                    {"$set": {"ai_topics": op["ai_topics"], "ai_topic_scores": op["ai_topic_scores"]}}
                )
                for op in ops
            ]
            await db.pls_caselaws.bulk_write(bulk)
            tagged_count += len(ops)

    remaining = await db.pls_caselaws.count_documents({"ai_topics": {"$exists": False}})
    return {
        "tagged": tagged_count,
        "remaining": remaining,
        "tokens_used": 0,
        "method": "faiss_vectors (zero cost)",
    }


@router.get("/topic-tagging/browse")
async def browse_by_topic(
    topic: str = Query(..., description="Legal topic to browse"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Browse cases by auto-tagged topic."""
    skip = (page - 1) * limit
    query = {"ai_topics": topic}
    total = await db.pls_caselaws.count_documents(query)
    cursor = db.pls_caselaws.find(
        query,
        {"_id": 0, "case_id": 1, "citation": 1, "parties": 1, "court": 1,
         "year": 1, "ai_topics": 1, "ai_topic_scores": 1}
    ).sort("year", -1).skip(skip).limit(limit)
    cases = await cursor.to_list(length=limit)

    return {"topic": topic, "data": cases, "total": total, "page": page, "limit": limit}


@router.get("/topic-tagging/stats")
async def topic_stats():
    """Get count of cases per topic."""
    pipeline = [
        {"$match": {"ai_topics": {"$exists": True}}},
        {"$unwind": "$ai_topics"},
        {"$group": {"_id": "$ai_topics", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    results = await db.pls_caselaws.aggregate(pipeline).to_list(length=100)
    total_tagged = await db.pls_caselaws.count_documents({"ai_topics": {"$exists": True}})
    total_untagged = await db.pls_caselaws.count_documents({"ai_topics": {"$exists": False}})

    return {
        "topics": [{"topic": r["_id"], "count": r["count"]} for r in results],
        "total_tagged": total_tagged,
        "total_untagged": total_untagged,
    }
