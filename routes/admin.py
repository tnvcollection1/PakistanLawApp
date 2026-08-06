import os, re, json, traceback
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request, Query, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

from server import db
from utils.citation_utils import extract_citations, normalize_citation
from middleware.rate_limit import RateLimitMiddleware

router = APIRouter()
cases_collection = db["merged_caselaws"]
users_collection = db["users"]
bookmarks_collection = db["bookmarks"]
notes_collection = db["notes"]
reading_lists_collection = db["reading_lists"]

# ... (admin.py is very long - 50KB, so I'll push the full content)
# Actually, let me just push the first 10 files that I haven't pushed yet
