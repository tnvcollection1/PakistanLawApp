from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from typing import Optional, List
import statistics

router = APIRouter()

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]


@router.get("/court_performance/summary")
async def get_court_performance_summary(
    year: Optional[int] = Query(None, description="Filter by year"),
    court: Optional[str] = Query(None, description="Filter by court name")
):
    """Get aggregated performance metrics for courts."""
    collection = db["cases"]
    match_stage = {}
    if year:
        match_stage["year"] = year
    if court:
        match_stage["court"] = court
    
    pipeline = [
        {"$match": match_stage},
        {"$group": {
            "_id": "$court",
            "total_cases": {"$sum": 1},
            "avg_case_length": {"$avg": {"$strLenCP": "$full_text"}},
            "total_judges": {"$addToSet": "$judges"},
            "categories": {"$addToSet": "$category"}
        }},
        {"$sort": {"total_cases": -1}}
    ]
    
    results = list(collection.aggregate(pipeline))
    return {"courts": results, "total": len(results)}


@router.get("/court_performance/timeline")
async def get_court_performance_timeline(
    court: str = Query(..., description="Court name"),
    start_year: Optional[int] = Query(1950),
    end_year: Optional[int] = Query(2024)
):
    """Get year-by-year case volume for a specific court."""
    collection = db["cases"]
    pipeline = [
        {"$match": {"court": court, "year": {"$gte": start_year, "$lte": end_year}}},
        {"$group": {
            "_id": "$year",
            "case_count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    results = list(collection.aggregate(pipeline))
    return {"court": court, "timeline": results}


@router.get("/court_performance/judges")
async def get_court_judges(
    court: str = Query(..., description="Court name"),
    limit: int = Query(50, le=200)
):
    """Get judges associated with a court."""
    collection = db["cases"]
    judges = collection.distinct("judges", {"court": court})
    return {"court": court, "judges": judges[:limit], "total_judges": len(judges)}


@router.get("/court_performance/categories")
async def get_court_categories(
    court: str = Query(..., description="Court name")
):
    """Get case categories for a court."""
    collection = db["cases"]
    categories = collection.distinct("category", {"court": court})
    return {"court": court, "categories": categories}
