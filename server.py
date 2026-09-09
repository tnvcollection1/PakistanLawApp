from dotenv import load_dotenv
load_dotenv()

import os
import sentry_sdk

_glitchtip_dsn = os.environ.get('GLITCHTIP_DSN', '')
if _glitchtip_dsn:
    sentry_sdk.init(
        dsn=_glitchtip_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )
    print("[OK] GlitchTip error monitoring initialized")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from database import db, test_connection

from routes import search, cases, auth, citation_parser, case_search, analytics, section_search, advanced_search, export_case, download_case, ai_embedded, ai_chat, lawbot

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[STARTUP] PakistanLawApp backend starting...")
    await test_connection()
    yield
    print("[SHUTDOWN] PakistanLawApp backend shutting down...")

app = FastAPI(
    title="Pakistan Law App API",
    description="API for Pakistan Law App - Legal research platform with 369,810+ case laws",
    version="3.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(cases.router, prefix="/api", tags=["Cases"])
app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(citation_parser.router, prefix="/api", tags=["Citation Parser"])
app.include_router(case_search.router, prefix="/api", tags=["Case Search"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(section_search.router, prefix="/api", tags=["Section Search"])
app.include_router(advanced_search.router, prefix="/api", tags=["Advanced Search"])
app.include_router(export_case.router, prefix="/api", tags=["Export"])
app.include_router(download_case.router, prefix="/api", tags=["Download"])
app.include_router(ai_embedded.router, prefix="/api", tags=["AI Embedded"])
app.include_router(ai_chat.router, prefix="/api", tags=["AI Chat"])
app.include_router(lawbot.router, prefix="/api", tags=["PakistanLawBot"])

# ─── NEW LAWYER TOOLS ──────────────────────────────────────
try:
    from routes.case_diary import router as case_diary_router
    app.include_router(case_diary_router, prefix="/api", tags=["Case Diary"])
    print("[OK] case_diary")
except Exception as e:
    print(f"[WARN] case_diary: {e}")

try:
    from routes.document_vault import router as document_vault_router
    app.include_router(document_vault_router, prefix="/api", tags=["Document Vault"])
    print("[OK] document_vault")
except Exception as e:
    print(f"[WARN] document_vault: {e}")

try:
    from routes.contracts import router as contracts_router
    app.include_router(contracts_router, prefix="/api", tags=["Legal Drafter"])
    print("[OK] contracts")
except Exception as e:
    print(f"[WARN] contracts: {e}")

try:
    from routes.document_analyzer import router as doc_analyzer_router
    app.include_router(doc_analyzer_router, prefix="/api", tags=["Document Analyzer"])
    print("[OK] document_analyzer")
except Exception as e:
    print(f"[WARN] document_analyzer: {e}")

try:
    from routes.notes import router as notes_router
    app.include_router(notes_router, prefix="/api", tags=["Research Notebook"])
    print("[OK] notes")
except Exception as e:
    print(f"[WARN] notes: {e}")

# ───────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "3.1.0"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)
