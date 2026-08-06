"""Court Integrations API — cause list scraping and caching."""
from fastapi import APIRouter, BackgroundTasks
from database import db
from datetime import datetime, timezone
from scrapers.cause_list_scraper import scrape_all_cause_lists, COURTS

router = APIRouter(prefix="/court-integrations", tags=["court-integrations"])

SCRAPE_STATE_ID = "court_scrape_status"


async def _get_scrape_state():
    doc = await db.scrape_state.find_one({"_id": SCRAPE_STATE_ID}, {"_id": 0})
    return doc or {"running": False, "progress": "", "last_run": None, "error": None}


async def _set_scrape_state(state):
    await db.scrape_state.update_one(
        {"_id": SCRAPE_STATE_ID},
        {"$set": state},
        upsert=True,
    )


@router.get("/courts")
async def list_courts():
    """List all supported courts with metadata."""
    courts = []
    for code, info in COURTS.items():
        courts.append({
            "code": code,
            "name": info["name"],
            "url": info["url"],
            "enabled": info.get("enabled", True),
        })
    return {"courts": courts}


@router.get("/cause-lists")
async def get_cause_lists(court: str = None, limit: int = 100):
    """Return cached cause lists, optionally filtered by court code."""
    query = {}
    if court:
        query["court_code"] = court

    cursor = db.cause_lists.find(query, {"_id": 0}).sort("scraped_at", -1).limit(limit)
    results = await cursor.to_list(length=limit)
    total = await db.cause_lists.count_documents(query)

    court_counts = {}
    pipeline = [{"$group": {"_id": "$court_code", "count": {"$sum": 1}}}]
    async for doc in db.cause_lists.aggregate(pipeline):
        court_counts[doc["_id"]] = doc["count"]

    state = await _get_scrape_state()

    return {
        "data": results,
        "total": total,
        "court_counts": court_counts,
        "last_scraped": state.get("last_run"),
        "scraping": state.get("running", False),
    }


@router.post("/scrape")
async def trigger_scrape(background_tasks: BackgroundTasks):
    """Trigger a background scrape of all court cause lists."""
    state = await _get_scrape_state()
    if state.get("running"):
        return {"status": "already_running", "progress": state.get("progress", "")}
    background_tasks.add_task(_scrape_task)
    return {"status": "started"}


@router.get("/scrape/status")
async def scrape_status():
    """Return current scrape job status."""
    return await _get_scrape_state()


async def _scrape_task():
    """Background task to scrape all court cause lists."""
    await _set_scrape_state({"running": True, "progress": "Starting...", "last_run": None, "error": None})

    try:
        await _set_scrape_state({"running": True, "progress": "Scraping court websites...", "error": None})
        results = await scrape_all_cause_lists()

        await _set_scrape_state({"running": True, "progress": f"Saving {len(results)} entries...", "error": None})
        await db.cause_lists.delete_many({})
        if results:
            await db.cause_lists.insert_many(results)

        await _set_scrape_state({
            "running": False,
            "progress": f"Done — {len(results)} cause lists found",
            "last_run": datetime.now(timezone.utc).isoformat(),
            "error": None,
        })

    except Exception as e:
        await _set_scrape_state({
            "running": False,
            "progress": f"Error: {e}",
            "error": str(e),
        })
        print(f"Court scrape error: {e}")
        import traceback
        traceback.print_exc()
