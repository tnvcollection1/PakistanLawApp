from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from database import db, ROOT_DIR
from models import StatuteUpdate
from bson import ObjectId

router = APIRouter()


# ============================================
# Statutes
# ============================================

@router.get("/statutes")
async def get_statutes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    year: Optional[int] = None,
    letter: Optional[str] = None
):
    query = {}
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    if keyword:
        query["$or"] = [
            {"title": {"$regex": keyword, "$options": "i"}},
            {"name": {"$regex": keyword, "$options": "i"}}
        ]
    if year:
        query["year"] = year
    if letter:
        query["$or"] = [
            {"title": {"$regex": f"^{letter}", "$options": "i"}},
            {"name": {"$regex": f"^{letter}", "$options": "i"}}
        ]

    skip = (page - 1) * limit
    cursor = db.pls_statutes.find(query).sort("year", -1).skip(skip).limit(limit)
    statutes = await cursor.to_list(length=limit)

    for statute in statutes:
        statute["_id"] = str(statute["_id"])

    total = await db.pls_statutes.count_documents(query)
    return {"data": statutes, "total": total, "page": page, "limit": limit}


@router.get("/statutes/count")
async def get_statutes_count():
    count = await db.pls_statutes.count_documents({})
    return {"count": count}


@router.get("/statutes/by-letter/{letter}")
async def get_statutes_by_letter(letter: str):
    query = {"title": {"$regex": f"^{letter.upper()}", "$options": "i"}}
    cursor = db.pls_statutes.find(query).sort("title", 1).limit(500)
    statutes = await cursor.to_list(length=500)
    for s in statutes:
        s["_id"] = str(s["_id"])
    return statutes


@router.get("/statutes/categories")
async def get_statute_categories():
    pipeline = [
        {"$group": {"_id": "$category"}},
        {"$sort": {"_id": 1}}
    ]
    cursor = db.pls_statutes.aggregate(pipeline)
    categories = await cursor.to_list(length=100)
    return [c["_id"] for c in categories if c["_id"]]


@router.get("/statutes/{statute_id}")
async def get_statute(statute_id: str):
    statute = await db.pls_statutes.find_one({"id": statute_id})
    if not statute:
        statute = await db.pls_statutes.find_one({"statute_id": statute_id})
    if not statute:
        raise HTTPException(status_code=404, detail="Statute not found")
    statute["_id"] = str(statute["_id"])
    return statute


@router.put("/statutes/{statute_id}/update")
async def update_statute(statute_id: str, update: StatuteUpdate):
    update_data = {"updated_at": datetime.utcnow().isoformat()}

    if update.title:
        update_data["title"] = update.title
        update_data["name"] = update.title
    if update.content:
        update_data["content"] = update.content
    if update.amendment_date:
        update_data["amendment_date"] = update.amendment_date
    if update.amendment_notes:
        update_data["amendment_notes"] = update.amendment_notes
    if update.is_current is not None:
        update_data["is_current"] = update.is_current
    if update.replaced_by:
        update_data["replaced_by"] = update.replaced_by
    if update.effective_date:
        update_data["effective_date"] = update.effective_date

    query = {"$or": [{"id": statute_id}, {"statute_id": statute_id}]}
    try:
        query["$or"].append({"_id": ObjectId(statute_id)})
    except Exception:
        pass

    await db.statute_amendments.insert_one({
        "statute_id": statute_id,
        "changes": update_data,
        "amended_at": datetime.utcnow().isoformat()
    })

    result = await db.pls_statutes.update_one(query, {"$set": update_data})

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Statute not found")

    return {"message": "Statute updated successfully"}


@router.get("/statutes/{statute_id}/amendments")
async def get_statute_amendments(statute_id: str):
    cursor = db.statute_amendments.find({"statute_id": statute_id}).sort("amended_at", -1)
    amendments = await cursor.to_list(length=100)
    for a in amendments:
        a["_id"] = str(a["_id"])
    return amendments


@router.post("/statutes/bulk-update")
async def bulk_update_statutes(updates: list):
    results = []
    for update in updates:
        statute_id = update.get("statute_id")
        if not statute_id:
            continue

        update_data = {k: v for k, v in update.items() if k != "statute_id"}
        update_data["updated_at"] = datetime.utcnow().isoformat()

        result = await db.pls_statutes.update_one(
            {"$or": [{"id": statute_id}, {"statute_id": statute_id}, {"title": statute_id}]},
            {"$set": update_data}
        )
        results.append({
            "statute_id": statute_id,
            "updated": result.modified_count > 0
        })

    return {"results": results, "total_updated": sum(1 for r in results if r["updated"])}


# ============================================
# Words & Phrases
# ============================================

@router.get("/words-phrases")
async def get_words_phrases(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    letter: Optional[str] = None,
    keyword: Optional[str] = None
):
    query = {}
    if letter:
        query["term"] = {"$regex": f"^{letter.upper()}", "$options": "i"}
    if keyword:
        query["term"] = {"$regex": keyword, "$options": "i"}

    skip = (page - 1) * limit
    cursor = db.pls_words_phrases.find(query).sort("phrase", 1).skip(skip).limit(limit)
    words = await cursor.to_list(length=limit)

    for word in words:
        word["_id"] = str(word["_id"])

    total = await db.pls_words_phrases.count_documents(query)
    return {"data": words, "total": total, "page": page, "limit": limit}


@router.get("/words-phrases/count")
async def get_words_phrases_count():
    count = await db.pls_words_phrases.count_documents({})
    return {"count": count}


@router.get("/words-phrases/by-letter/{letter}")
async def get_words_by_letter(letter: str):
    query = {"phrase": {"$regex": f"^{letter.upper()}", "$options": "i"}}
    cursor = db.pls_words_phrases.find(query).sort("phrase", 1).limit(500)
    words = await cursor.to_list(length=500)
    for w in words:
        w["_id"] = str(w["_id"])
    return words


# ============================================
# Legal Terms
# ============================================

@router.get("/legal-terms")
async def get_legal_terms(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    letter: Optional[str] = None,
    keyword: Optional[str] = None
):
    query = {}
    if letter:
        query["term"] = {"$regex": f"^{letter.upper()}", "$options": "i"}
    if keyword:
        query["term"] = {"$regex": keyword, "$options": "i"}

    skip = (page - 1) * limit
    cursor = db.pls_legal_terms.find(query).sort("term", 1).skip(skip).limit(limit)
    terms = await cursor.to_list(length=limit)

    for term in terms:
        term["_id"] = str(term["_id"])

    total = await db.pls_legal_terms.count_documents(query)
    return {"data": terms, "total": total, "page": page, "limit": limit}


@router.get("/legal-terms/count")
async def get_legal_terms_count():
    count = await db.pls_legal_terms.count_documents({})
    return {"count": count}


# ============================================
# Maxims
# ============================================

@router.get("/maxims")
async def get_maxims(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    letter: Optional[str] = None,
    keyword: Optional[str] = None
):
    query = {}
    if letter:
        query["latin"] = {"$regex": f"^{letter.upper()}", "$options": "i"}
    if keyword:
        query["$or"] = [
            {"latin": {"$regex": keyword, "$options": "i"}},
            {"meaning": {"$regex": keyword, "$options": "i"}}
        ]

    skip = (page - 1) * limit
    cursor = db.plsbeta_maxims.find(query).sort("latin", 1).skip(skip).limit(limit)
    maxims = await cursor.to_list(length=limit)

    for maxim in maxims:
        maxim["_id"] = str(maxim["_id"])

    total = await db.plsbeta_maxims.count_documents(query)
    return {"data": maxims, "total": total, "page": page, "limit": limit}


@router.get("/maxims/count")
async def get_maxims_count():
    count = await db.plsbeta_maxims.count_documents({})
    return {"count": count}


# ============================================
# Articles
# ============================================

@router.get("/articles")
async def get_articles(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    publication: Optional[str] = None,
    keyword: Optional[str] = None,
    author: Optional[str] = None,
    year: Optional[int] = None
):
    query = {}
    if publication:
        query["publication"] = publication
    if keyword:
        query["title"] = {"$regex": keyword, "$options": "i"}
    if author:
        query["author"] = {"$regex": author, "$options": "i"}
    if year:
        query["year"] = year

    skip = (page - 1) * limit
    cursor = db.pls_articles.find(query).sort("year", -1).skip(skip).limit(limit)
    articles = await cursor.to_list(length=limit)

    for article in articles:
        article["_id"] = str(article["_id"])

    total = await db.pls_articles.count_documents(query)
    return {"data": articles, "total": total, "page": page, "limit": limit}


@router.get("/articles/count")
async def get_articles_count():
    count = await db.pls_articles.count_documents({})
    return {"count": count}


# ============================================
# Topics
# ============================================

@router.get("/topics")
async def get_topics(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    keyword: Optional[str] = None,
    letter: Optional[str] = None
):
    query = {}
    if keyword:
        query["name"] = {"$regex": keyword, "$options": "i"}
    if letter:
        # Filter by first letter of name (not a separate 'letter' field)
        query["name"] = {"$regex": f"^{letter.upper()}", "$options": "i"}

    skip = (page - 1) * limit
    cursor = db.pls_topics.find(query).sort("name", 1).skip(skip).limit(limit)
    topics = await cursor.to_list(length=limit)

    for topic in topics:
        topic["_id"] = str(topic["_id"])

    total = await db.pls_topics.count_documents(query)
    return {"data": topics, "total": total, "page": page, "limit": limit}


@router.get("/topics/count")
async def get_topics_count():
    count = await db.pls_topics.count_documents({})
    return {"count": count}


# ============================================
# Dictionary
# ============================================

@router.get("/dictionary")
async def get_dictionary(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    letter: Optional[str] = None,
    keyword: Optional[str] = None
):
    query = {}
    if letter:
        query["word"] = {"$regex": f"^{letter.upper()}", "$options": "i"}
    if keyword:
        query["word"] = {"$regex": keyword, "$options": "i"}

    skip = (page - 1) * limit
    cursor = db.pls_dictionary.find(query).sort("word", 1).skip(skip).limit(limit)
    entries = await cursor.to_list(length=limit)

    for entry in entries:
        entry["_id"] = str(entry["_id"])

    total = await db.pls_dictionary.count_documents(query)
    return {"data": entries, "total": total, "page": page, "limit": limit}


@router.get("/dictionary/count")
async def get_dictionary_count():
    count = await db.pls_dictionary.count_documents({})
    return {"count": count}
