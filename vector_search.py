"""
Vector search module for PakistanLawApp.
Uses sentence-transformers for embeddings and FAISS for similarity search.
Indexes case headnotes/content for semantic retrieval.
"""
import numpy as np
import pickle
import os
import logging

logger = logging.getLogger(__name__)

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    _deps_available = True
except ImportError:
    _deps_available = False
    logger.warning("Vector search dependencies not available (faiss/sentence-transformers). Falling back to keyword search.")

INDEX_DIR = os.path.join(os.path.dirname(__file__), "vector_index")
INDEX_PATH = os.path.join(INDEX_DIR, "cases.index")
META_PATH = os.path.join(INDEX_DIR, "cases_meta.pkl")
MODEL_NAME = "all-MiniLM-L6-v2"  # 384-dim, ~80MB, fast & good quality

_model = None
_index = None
_metadata = None


def get_model():
    global _model
    if not _deps_available:
        return None
    if _model is None:
        logger.info(f"Loading sentence-transformer model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
        logger.info("Model loaded successfully")
    return _model


def load_index():
    """Load FAISS index and metadata from disk."""
    global _index, _metadata
    if not _deps_available:
        return False
    if _index is not None:
        return True

    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        logger.warning("Vector index not found. Run generate_embeddings.py first.")
        return False

    logger.info("Loading FAISS index...")
    _index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        _metadata = pickle.load(f)
    logger.info(f"Loaded index with {_index.ntotal} vectors, {len(_metadata)} metadata entries")
    return True


def search_cases(query: str, k: int = 10, threshold: float = 0.3):
    """
    Semantic search for cases matching the query.
    Returns list of {case_id, parties, court, year, score, snippet} dicts.
    """
    if not load_index():
        return []

    model = get_model()
    query_vec = model.encode([query], normalize_embeddings=True)
    query_vec = np.array(query_vec, dtype="float32")

    scores, indices = _index.search(query_vec, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(_metadata):
            continue
        if score < threshold:
            continue
        meta = _metadata[idx]
        results.append({
            "case_id": meta["case_id"],
            "parties": meta.get("parties", ""),
            "court": meta.get("court", ""),
            "year": meta.get("year", ""),
            "judge": meta.get("judge", ""),
            "score": float(score),
            "snippet": meta.get("snippet", "")[:1500],
        })
    return results


def get_index_stats():
    """Return stats about the loaded index."""
    if not load_index():
        return {"indexed": False, "count": 0}
    return {
        "indexed": True,
        "count": _index.ntotal,
        "metadata_count": len(_metadata),
        "model": MODEL_NAME,
        "dimension": _index.d,
    }
