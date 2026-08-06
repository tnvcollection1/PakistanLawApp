from fastapi import APIRouter, Query
from datetime import datetime, timezone, timedelta
from database import db

router = APIRouter()


@router.post("/search-analytics/track")
async def track_search(data: dict):
    """Track a search query for analytics."""
    query = data.get("query", "").strip()
    if not query:
        return {"status": "skipped"}

    doc = {
        "query": query,
        "user": data.get("user", "anonymous"),
        "source": data.get("source", "unknown"),
        "results_count": data.get("results_count", 0),
        "filters": data.get("filters", {}),
        "timestamp": datetime.now(timezone.utc),
    }
    await db.search_analytics.insert_one(doc)
    return {"status": "tracked"}


@router.get("/search-analytics/dashboard")
async def get_analytics_dashboard(days: int = Query(30, ge=1, le=365)):
    """Get search analytics dashboard data."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # Total searches
    total_searches = await db.search_analytics.count_documents({"timestamp": {"$gte": cutoff}})

    # Top queries
    top_queries_pipeline = [
        {"$match": {"timestamp": {"$gte": cutoff}}},
        {"$group": {"_id": {"$toLower": "$query"}, "count": {"$sum": 1}, "avg_results": {"$avg": "$results_count"}}},
        {"$sort": {"count": -1}},
        {"$limit": 20},
        {"$project": {"_id": 0, "query": "$_id", "count": 1, "avg_results": {"$round": ["$avg_results", 0]}}},
    ]
    top_queries = await db.search_analytics.aggregate(top_queries_pipeline).to_list(length=20)

    # Failed searches (0 results)
    failed_pipeline = [
        {"$match": {"timestamp": {"$gte": cutoff}, "results_count": 0}},
        {"$group": {"_id": {"$toLower": "$query"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15},
        {"$project": {"_id": 0, "query": "$_id", "count": 1}},
    ]
    failed_searches = await db.search_analytics.aggregate(failed_pipeline).to_list(length=15)

    # Daily volume
    daily_pipeline = [
        {"$match": {"timestamp": {"$gte": cutoff}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "count": {"$sum": 1},
            "unique_users": {"$addToSet": "$user"},
        }},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "date": "$_id", "count": 1, "unique_users": {"$size": "$unique_users"}}},
    ]
    daily_volume = await db.search_analytics.aggregate(daily_pipeline).to_list(length=365)

    # Search source breakdown
    source_pipeline = [
        {"$match": {"timestamp": {"$gte": cutoff}}},
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "source": "$_id", "count": 1}},
    ]
    sources = await db.search_analytics.aggregate(source_pipeline).to_list(length=20)

    # Unique users
    unique_users = len(await db.search_analytics.distinct("user", {"timestamp": {"$gte": cutoff}}))

    return {
        "period_days": days,
        "total_searches": total_searches,
        "unique_users": unique_users,
        "top_queries": top_queries,
        "failed_searches": failed_searches,
        "daily_volume": daily_volume,
        "sources": sources,
    }
