"""Analytics Dashboard API Routes."""
import time
from fastapi import APIRouter, HTTPException, Query
from server import db

router = APIRouter()
cases_collection = db["merged_caselaws"]

_cached = {}
_cache_ttl = 300  # 5 minutes

def _chartjs(items, label_key, value_key):
    return {"labels": [str(i.get(label_key, i.get("_id", ""))) for i in items],
            "data": [i.get(value_key, 0) for i in items]}

@router.get("/analytics/overview")
async def analytics_overview():
    try:
        total = await cases_collection.estimated_document_count()
        return {"total_cases": total, "total_courts": 329, "total_judges": 62424, "years_range": 1950}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/cases-by-year")
async def cases_by_year():
    try:
        pipeline = [
            {"$match": {"year": {"$gte": 1994, "$lte": 2024}}},
            {"$group": {"_id": "$year", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
        ]
        docs = await cases_collection.aggregate(pipeline).to_list(length=50)
        return {**_chartjs(docs, "_id", "count"), "period": "1994-2024"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/cases-by-court")
async def cases_by_court():
    try:
        pipeline = [
            {"$match": {"court": {"$exists": True, "$ne": ""}}},
            {"$group": {"_id": "$court", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}, {"$limit": 20},
        ]
        docs = await cases_collection.aggregate(pipeline).to_list(length=20)
        return _chartjs(docs, "_id", "count")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/cases-by-judge")
async def cases_by_judge(limit: int = Query(50, ge=1, le=200)):
    try:
        pipeline = [
            {"$match": {"judges": {"$exists": True, "$ne": ""}}},
            {"$group": {"_id": "$judges", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}, {"$limit": limit},
        ]
        docs = await cases_collection.aggregate(pipeline).to_list(length=limit)
        return _chartjs(docs, "_id", "count")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/trends")
async def analytics_trends(years: int = Query(10, ge=1, le=50)):
    try:
        import datetime
        cy = datetime.datetime.now().year
        sy = cy - years + 1
        pipeline = [
            {"$match": {"year": {"$gte": sy, "$lte": cy}}},
            {"$group": {"_id": "$year", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
        ]
        docs = await cases_collection.aggregate(pipeline).to_list(length=years)
        year_map = {d["_id"]: d["count"] for d in docs}
        labels, data = [], []
        for y in range(sy, cy + 1):
            labels.append(str(y)); data.append(year_map.get(y, 0))
        return {"labels": labels, "data": data, "period": f"{sy}-{cy}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
