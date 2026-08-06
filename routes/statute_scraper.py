"""
Statute Scraping Management API — trigger and monitor statute section scraping.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from database import db
import os
import json
import subprocess

router = APIRouter()

PROGRESS_FILE = '/tmp/statute_scraper_progress.json'


@router.get("/statute-scraper/status")
async def get_scrape_status():
    """Get current scraping progress."""
    # Check how many statutes have been scraped
    total = await db.pls_statutes.estimated_document_count()
    scraped = await db.pls_statutes.count_documents({"sections_scraped_at": {"$exists": True}})
    with_sections = await db.pls_statutes.count_documents({"sections_count": {"$gt": 0}})

    progress = {}
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            progress = json.load(f)

    return {
        "total_statutes": total,
        "scraped": scraped,
        "with_sections": with_sections,
        "remaining": total - scraped,
        "percent_complete": round((scraped / total * 100), 1) if total > 0 else 0,
        "scraper_progress": progress,
    }


@router.post("/statute-scraper/trigger")
async def trigger_scrape(batch: int = 50, letter: str = None):
    """Trigger a batch of statute scraping in the background."""
    cmd = ["python3", "scripts/scrape_statutes.py", "--batch", str(batch)]
    if letter:
        cmd += ["--letter", letter]

    try:
        # Run in background
        process = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            stdout=open('/tmp/statute_scraper.log', 'a'),
            stderr=subprocess.STDOUT,
        )
        return {
            "status": "started",
            "pid": process.pid,
            "batch_size": batch,
            "letter": letter,
            "message": f"Scraping {batch} statutes in background. Check /api/statute-scraper/status for progress.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statute-scraper/sections/{statute_name}")
async def get_statute_sections(statute_name: str):
    """Get sections for a specific statute."""
    statute = await db.pls_statutes.find_one(
        {"name": {"$regex": f"^{statute_name}$", "$options": "i"}},
        {"_id": 0}
    )
    if not statute:
        raise HTTPException(status_code=404, detail="Statute not found")

    sections = statute.get("sections", [])
    return {
        "name": statute.get("name"),
        "category": statute.get("category"),
        "year": statute.get("year"),
        "sections_count": len(sections),
        "sections": sections,
        "scraped_at": statute.get("sections_scraped_at"),
    }
