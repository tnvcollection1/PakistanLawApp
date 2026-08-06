from fastapi import APIRouter, Query
from database import db
import re

router = APIRouter()


@router.get("/court-performance")
async def court_performance_dashboard():
    """Court performance metrics - cases per court, yearly trends, busiest courts."""
    async def compute():
        court_pipeline = [
            {"$match": {"court": {"$exists": True, "$ne": ""}}},
            {"$group": {
                "_id": "$court",
                "total": {"$sum": 1},
                "with_content": {"$sum": {"$cond": [{"$and": [{"$ne": ["$full_content", ""]}, {"$ne": ["$full_content", None]}, {"$ifNull": ["$full_content", False]}]}, 1, 0]}},
                "min_year": {"$min": "$year"},
                "max_year": {"$max": "$year"},
            }},
            {"$sort": {"total": -1}},
            {"$limit": 25}
        ]
        courts = await db.pls_caselaws.aggregate(court_pipeline).to_list(25)

        top5 = [c["_id"] for c in courts[:5]]
        trend_pipeline = [
            {"$match": {"court": {"$in": top5}, "year": {"$exists": True, "$gte": 1990}}},
            {"$group": {"_id": {"court": "$court", "year": "$year"}, "count": {"$sum": 1}}},
            {"$sort": {"_id.year": 1}}
        ]
        trends = await db.pls_caselaws.aggregate(trend_pipeline).to_list(1000)

        trend_years = sorted(set(t["_id"]["year"] for t in trends))
        trend_map = {}
        for t in trends:
            yr = t["_id"]["year"]
            ct = t["_id"]["court"]
            if yr not in trend_map:
                trend_map[yr] = {"year": yr}
            trend_map[yr][ct] = t["count"]
        trend_data = [trend_map[yr] for yr in trend_years]

        year_pipeline = [
            {"$match": {"year": {"$exists": True, "$gte": 1947}}},
            {"$group": {"_id": "$year", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        yearly = await db.pls_caselaws.aggregate(year_pipeline).to_list(200)

        peak = max(yearly, key=lambda x: x["count"]) if yearly else {"_id": 0, "count": 0}

        total_cases = await db.pls_caselaws.count_documents({})
        total_courts = len(await db.pls_caselaws.distinct("court"))

        return {
            "summary": {
                "total_cases": total_cases,
                "total_courts": total_courts,
                "peak_year": peak["_id"],
                "peak_year_count": peak["count"],
            },
            "courts": [
                {
                    "name": c["_id"],
                    "total": c["total"],
                    "with_content": c["with_content"],
                    "active_years": (c["max_year"] - c["min_year"] + 1) if c.get("min_year") and c.get("max_year") else 0,
                    "first_year": c.get("min_year"),
                    "last_year": c.get("max_year"),
                }
                for c in courts
            ],
            "top5_courts": top5,
            "yearly_trend": trend_data,
            "yearly_total": [{"year": y["_id"], "count": y["count"]} for y in yearly],
        }

    from routes.analytics import get_cached
    return await get_cached("court_performance", compute)


@router.get("/precedent-tracker/{case_id}")
async def precedent_tracker(case_id: str):
    """Track legal precedent chain for a case - citations it makes and cases that cite it."""
    # Get the source case
    source = await db.pls_caselaws.find_one(
        {"case_id": case_id},
        {"_id": 0, "case_id": 1, "parties": 1, "court": 1, "year": 1, "judge": 1, "full_content": 1, "headnotes_text": 1}
    )
    if not source:
        return {"error": "Case not found"}

    content = (source.get("full_content") or "") + " " + (source.get("headnotes_text") or "")

    # Extract citation patterns from the case content
    citation_patterns = [
        r'(\d{4}\s+(?:PLD|SCMR|CLC|PCrLJ|PTD|PLC|CLD|YLR|GBLR|MLD|ALD|KLR|PLJ)\s+\d+)',
        r'(\d{4}\s+S\s*\d+)',
        r'(PLD\s+\d{4}\s+\w+\s+\d+)',
    ]

    cited_refs = set()
    for pattern in citation_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for m in matches:
            cited_refs.add(m.strip())

    # Find cases this case cites (cases referenced in text)
    cites_cases = []
    if cited_refs:
        refs_list = list(cited_refs)[:30]  # Limit to 30 citations
        for ref in refs_list:
            parts = ref.split()
            if len(parts) >= 2:
                # Try to find matching case
                search_q = {"$or": [
                    {"case_id": {"$regex": re.escape(ref.replace(" ", "")), "$options": "i"}},
                    {"citation": {"$regex": re.escape(ref), "$options": "i"}},
                ]}
                found = await db.pls_caselaws.find_one(
                    search_q,
                    {"_id": 0, "case_id": 1, "parties": 1, "court": 1, "year": 1, "judge": 1}
                )
                if found:
                    cites_cases.append(found)
                else:
                    cites_cases.append({"case_id": ref, "parties": "Referenced Citation", "court": "", "year": None})

    # Find cases that cite THIS case (reverse citations)
    cited_by_pipeline = [
        {"$match": {
            "$or": [
                {"full_content": {"$regex": re.escape(case_id), "$options": "i"}},
                {"headnotes_text": {"$regex": re.escape(case_id), "$options": "i"}},
            ],
            "case_id": {"$ne": case_id}
        }},
        {"$project": {"_id": 0, "case_id": 1, "parties": 1, "court": 1, "year": 1, "judge": 1}},
        {"$sort": {"year": -1}},
        {"$limit": 30}
    ]
    cited_by = await db.pls_caselaws.aggregate(cited_by_pipeline).to_list(30)

    # Remove full_content from source before returning
    source.pop("full_content", None)
    source.pop("headnotes_text", None)

    return {
        "source_case": source,
        "cites": cites_cases[:20],
        "cited_by": cited_by,
        "raw_citations": list(cited_refs)[:30],
        "total_cites": len(cites_cases),
        "total_cited_by": len(cited_by),
    }


@router.get("/legal-timeline")
async def legal_timeline(
    query: str = Query(..., description="Topic or keyword to search"),
    limit: int = Query(50, ge=10, le=100),
):
    """Get chronological evolution of case law on a topic."""
    search_filter = {
        "$or": [
            {"full_content": {"$regex": query, "$options": "i"}},
            {"headnotes_text": {"$regex": query, "$options": "i"}},
            {"parties": {"$regex": query, "$options": "i"}},
        ],
        "year": {"$exists": True, "$gte": 1947}
    }

    total = await db.pls_caselaws.count_documents(search_filter)

    # Get cases sorted by year
    cases = await db.pls_caselaws.find(
        search_filter,
        {"_id": 0, "case_id": 1, "parties": 1, "court": 1, "year": 1, "judge": 1}
    ).sort("year", 1).limit(limit).to_list(limit)

    # Get distribution by decade
    decade_pipeline = [
        {"$match": search_filter},
        {"$group": {
            "_id": {"$subtract": ["$year", {"$mod": ["$year", 10]}]},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    decades = await db.pls_caselaws.aggregate(decade_pipeline).to_list(20)

    # Get distribution by court
    court_pipeline = [
        {"$match": search_filter},
        {"$group": {"_id": "$court", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    courts = await db.pls_caselaws.aggregate(court_pipeline).to_list(10)

    # Year-by-year counts
    year_pipeline = [
        {"$match": search_filter},
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    years = await db.pls_caselaws.aggregate(year_pipeline).to_list(200)

    return {
        "query": query,
        "total": total,
        "cases": cases,
        "decades": [{"decade": d["_id"], "count": d["count"]} for d in decades],
        "courts": [{"name": c["_id"], "count": c["count"]} for c in courts],
        "yearly": [{"year": y["_id"], "count": y["count"]} for y in years],
    }
