from dotenv import load_dotenv
load_dotenv()

import os
import sentry_sdk

# Initialize GlitchTip/Sentry error monitoring
_glitchtip_dsn = os.environ.get('GLITCHTIP_DSN', '')
if _glitchtip_dsn:
    sentry_sdk.init(
        dsn=_glitchtip_dsn,
        traces_sample_rate=0.2,
        environment=os.environ.get('ENVIRONMENT', 'production'),
    )
    print(f"GlitchTip initialized (DSN: ...{_glitchtip_dsn[-20:]})")
else:
    print("GlitchTip DSN not set — error monitoring disabled")

from fastapi import FastAPI
from middleware.rate_limit import AntiScrapingMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request

# Import database (initializes connection)
from database import db

# Import route modules
from routes.auth import router as auth_router
from routes.caselaws import router as caselaws_router
from routes.reference import router as reference_router
from routes.bookmarks import router as bookmarks_router
from routes.search import router as search_router
from routes.analytics import router as analytics_router
from routes.journals import router as journals_router
from routes.exports import router as exports_router
from routes.admin import router as admin_router
from routes.pls_data import router as pls_data_router
from routes.notes import router as notes_router
from routes.updates import router as updates_router
from routes.miscellaneous import router as misc_router
from routes.citations import router as citations_router
from routes.chatbot import router as chatbot_router
from routes.alerts import router as alerts_router
from routes.features import router as features_router
from routes.court_performance import router as court_perf_router
from routes.recommender import router as recommender_router
from routes.reading_lists import router as reading_lists_router
from routes.summarizer import router as summarizer_router
from routes.scanner import router as scanner_router
from routes.export_brief import router as export_brief_router
from routes.feed import router as feed_router
from routes.notifications import router as notifications_router
from routes.contracts import router as contracts_router
from routes.search_analytics import router as search_analytics_router
from routes.citator import router as citator_router
from routes.court_integrations import router as court_integrations_router
from routes.statute_links import router as statute_links_router
from routes.enterprise import router as enterprise_router
from routes.ai_case_finder import router as ai_case_finder_router
from routes.citation_network import router as citation_network_router
from routes.ai_headnotes_browse import router as ai_headnotes_browse_router
from routes.case_citations import router as case_citations_router
from routes.judge_analytics import router as judge_analytics_router
from routes.blacks_law import router as blacks_law_router
from routes.ai_smart_search import router as ai_smart_search_router
from routes.ai_case_summary import router as ai_case_summary_router
from routes.data_cleaning import router as data_cleaning_router
from routes.metadata_extraction import router as metadata_extraction_router
from routes.ai_streaming import router as ai_streaming_router
from routes.statute_scraper import router as statute_scraper_router
from routes.statute_explorer import router as statute_explorer_router
from routes.semantic_search import router as semantic_search_router
from routes.document_analyzer import router as document_analyzer_router
from routes.urdu_support import router as urdu_support_router
from routes.topic_tagging import router as topic_tagging_router
from routes.faiss_rebuild import router as faiss_rebuild_router
from routes.stats import router as stats_router
from routes.ollama_search import router as ollama_router
from routes.ai_summarizer import router as ai_summarizer_router
from routes.ai_assistant import router as ai_assistant_router
from routes.related_cases import router as related_cases_router
from routes.advanced_search import router as advanced_search_router
from routes.section_search import router as section_search_router
try:
    from routes.export_case import router as export_case_router
except Exception as e:
    export_case_router = None
    print(f"[WARN] export_case import failed: {e}")
try:
    from routes.download_case import router as download_case_router
except Exception as e:
    download_case_router = None
    print(f"[WARN] download_case import failed: {e}")
try:
    from routes.ai_chat import router as ai_chat_router
except Exception as e:
    ai_chat_router = None
    print(f"[WARN] ai_chat import failed: {e}")
try:
    from routes.ai_embedded import router as ai_embedded_router
except Exception as e:
    ai_embedded_router = None
    print(f"[WARN] ai_embedded import failed: {e}")

app = FastAPI(title="Pakistan LawSite Clone API", docs_url=None, redoc_url=None, openapi_url=None)

# Gzip compression for all responses > 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.environ.get("FRONTEND_URL", "http://localhost:3000"),
        "https://pakistanlawapp.com",
        "https://www.pakistanlawapp.com",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Anti-scraping and rate limiting protection
app.add_middleware(AntiScrapingMiddleware)

# Create main API router with /api prefix
from fastapi import APIRouter
api_router = APIRouter(prefix="/api")

# Include all route modules
api_router.include_router(auth_router)
api_router.include_router(caselaws_router)
api_router.include_router(reference_router)
api_router.include_router(bookmarks_router)
api_router.include_router(search_router)
api_router.include_router(analytics_router)
api_router.include_router(journals_router)
api_router.include_router(exports_router)
api_router.include_router(admin_router)
api_router.include_router(pls_data_router)
api_router.include_router(notes_router)
api_router.include_router(updates_router)
api_router.include_router(misc_router)
api_router.include_router(citations_router)
api_router.include_router(chatbot_router)
api_router.include_router(alerts_router)
api_router.include_router(features_router)
api_router.include_router(court_perf_router)
api_router.include_router(recommender_router)
api_router.include_router(reading_lists_router)
api_router.include_router(summarizer_router)
api_router.include_router(scanner_router)
api_router.include_router(export_brief_router)
api_router.include_router(feed_router)
api_router.include_router(notifications_router)
api_router.include_router(contracts_router)
api_router.include_router(search_analytics_router)
api_router.include_router(citator_router)
api_router.include_router(court_integrations_router)
api_router.include_router(statute_links_router)
api_router.include_router(enterprise_router)
api_router.include_router(ai_case_finder_router)
api_router.include_router(citation_network_router)
api_router.include_router(ai_headnotes_browse_router)
api_router.include_router(case_citations_router)
api_router.include_router(judge_analytics_router)
api_router.include_router(blacks_law_router)
api_router.include_router(ai_smart_search_router)
api_router.include_router(ai_case_summary_router)
api_router.include_router(data_cleaning_router)
api_router.include_router(metadata_extraction_router)
api_router.include_router(ai_streaming_router)
api_router.include_router(statute_scraper_router)
api_router.include_router(statute_explorer_router)
api_router.include_router(semantic_search_router)
api_router.include_router(document_analyzer_router)
api_router.include_router(urdu_support_router)
api_router.include_router(topic_tagging_router)
api_router.include_router(faiss_rebuild_router)
api_router.include_router(stats_router)
api_router.include_router(ai_summarizer_router)
api_router.include_router(ai_assistant_router)
api_router.include_router(related_cases_router)
try:
    if export_case_router:
        api_router.include_router(export_case_router)
except Exception as e:
    print(f"[WARN] export_case router: {e}")
try:
    if download_case_router:
        api_router.include_router(download_case_router)
except Exception as e:
    print(f"[WARN] download_case router: {e}")
try:
    if ai_chat_router:
        api_router.include_router(ai_chat_router)
except Exception as e:
    print(f"[WARN] ai_chat router: {e}")
try:
    if ai_embedded_router:
        api_router.include_router(ai_embedded_router)
except Exception as e:
    print(f"[WARN] ai_embedded router: {e}")

# Health check
@api_router.get("/health")
async def health():
    return {"status": "ok"}

# Script download endpoint
from fastapi.responses import FileResponse
@api_router.get("/download-script/{name}")
async def download_script(name: str):
    import os
    scripts = {
        "digilawyer_extract": "/app/backend/scripts/scrapers/digilawyer_extract.py",
        "digilawyer_browser": "/app/backend/scripts/scrapers/digilawyer_browser.py",
        "digilawyer_console": "/app/backend/scripts/scrapers/digilawyer_console.js",
        "digilawyer_scraper": "/app/backend/scripts/scrapers/digilawyer_scraper.py",
        "pls_journal_scraper": "/app/backend/scripts/scrapers/pls_journal_scraper.py",
        "global_search_audit_report": "/app/backend/scripts/scrapers/global_search_audit_report.pdf",
    }
    path = scripts.get(name)
    if path and os.path.exists(path):
        return FileResponse(path, filename=f"{name}.py", media_type="text/x-python")
    return {"error": "Script not found"}

# Include the main router
api_router.include_router(advanced_search_router)
api_router.include_router(section_search_router)

app.include_router(api_router)
app.include_router(ollama_router)

# Sitemap endpoint (serves XML sitemap for SEO)
from fastapi.responses import Response
@app.get("/sitemap.xml")
async def sitemap():
    """Generate XML sitemap with case law and statute URLs."""
    base_url = "https://pakistanlawapp.com"
    urls = [
        f"<url><loc>{base_url}/</loc><priority>1.0</priority></url>",
        f"<url><loc>{base_url}/dashboard</loc><priority>0.9</priority></url>",
        f"<url><loc>{base_url}/global-search</loc><priority>0.9</priority></url>",
        f"<url><loc>{base_url}/search</loc><priority>0.8</priority></url>",
        f"<url><loc>{base_url}/statutes</loc><priority>0.8</priority></url>",
        f"<url><loc>{base_url}/dictionary</loc><priority>0.7</priority></url>",
        f"<url><loc>{base_url}/legal-terms</loc><priority>0.7</priority></url>",
        f"<url><loc>{base_url}/blacks-law-dictionary</loc><priority>0.7</priority></url>",
        f"<url><loc>{base_url}/about</loc><priority>0.5</priority></url>",
    ]
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(urls)}
</urlset>'''
    return Response(content=xml, media_type="application/xml")

# Auto-scanner scheduler (every 6 hours)
import asyncio as _asyncio

async def _scanner_loop():
    """Run new cases scanner every 6 hours."""
    await _asyncio.sleep(60)  # Wait 1 min after startup
    while True:
        try:
            from routes.scanner import run_scanner
            await run_scanner()
        except Exception as e:
            print(f"Scanner error: {e}")
        await _asyncio.sleep(6 * 3600)  # 6 hours

@app.on_event("startup")
async def start_scanner_scheduler():
    # Seed admin user
    from auth_utils import seed_admin
    await seed_admin(db)
    
    # Create MongoDB indexes for fast search
    try:
        await db.pls_caselaws.create_index([("citation", 1)])
        await db.pls_caselaws.create_index([("year", -1)])
        await db.pls_caselaws.create_index([("court", 1), ("year", -1)])
        await db.pls_caselaws.create_index([("court", 1)])
        await db.pls_caselaws.create_index([("case_id", 1)])
        await db.pls_caselaws.create_index([("parties", 1)])
        await db.pls_dictionary.create_index([("word", 1)])
        await db.pls_legal_terms.create_index([("term", 1)])
        await db.pls_legal_terms.create_index([("name", 1)])
        await db.pls_statutes.create_index([("name", 1)])
        await db.pls_words_phrases.create_index([("phrase", 1)])
        await db.pls_words_phrases.create_index([("word", 1)])
        await db.pls_words_phrases.create_index([("name", 1)])
        await db.pls_maxims.create_index([("latin", 1)])
        await db.pls_maxims.create_index([("name", 1)])
        await db.pls_articles.create_index([("title", 1)])
        await db.pls_topics.create_index([("name", 1)])
        await db.blacks_law_dictionary.create_index([("term", 1)])
        print("MongoDB indexes ensured")
    except Exception as e:
        print(f"Index creation note: {e}")
    
    # Create weighted text index in background for full-text search
    async def _build_text_index():
        try:
            # Check if weighted text index exists
            indexes = await db.pls_caselaws.index_information()
            has_text = any(any(v == 'text' for _, v in info.get('key', [])) for info in indexes.values())
            if not has_text:
                print("Building weighted text index (background)...")
                await db.pls_caselaws.create_index(
                    [("citation", "text"), ("parties", "text"),
                     ("judge", "text"), ("petitioner", "text"), ("respondent", "text"),
                     ("court", "text")],
                    weights={"citation": 10, "parties": 8, "judge": 3,
                             "petitioner": 3, "respondent": 3, "court": 2},
                    name="weighted_search_index", default_language="english",
                )
                print("Weighted text index created!")
            else:
                print("Text index already exists")
        except Exception as e:
            print(f"Text index note: {e}")
    _asyncio.create_task(_build_text_index())
    
    _asyncio.create_task(_scanner_loop())


@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    response = await call_next(request)
    # Only add noindex for API and admin routes, not public pages
    if request.url.path.startswith("/api/") or request.url.path.startswith("/admin"):
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response

# ============================================
# Crash Prevention Middleware (added 2026-04-06)
# ============================================
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time

class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            # 30 second timeout for all requests
            return await asyncio.wait_for(call_next(request), timeout=30.0)
        except asyncio.TimeoutError:
            return JSONResponse(
                {"error": "Request timeout - please try again"},
                status_code=504
            )

# Add middleware (if not already added)
# app.add_middleware(TimeoutMiddleware)


try:
    from routes.citation_parser import router as citation_parser_router
    app.include_router(citation_parser_router)
except Exception as e:
    print(f"[WARN] citation_parser: {e}")

try:
    from routes.case_search import router as case_search_router
    app.include_router(case_search_router)
except Exception as e:
    print(f"[WARN] case_search: {e}")
