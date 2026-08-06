"""Bookmarks and reading lists."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from server import db
from datetime import datetime
from bson import ObjectId

router = APIRouter()
bookmarks_collection = db["bookmarks"]
reading_lists_collection = db["reading_lists"]

class BookmarkCreate(BaseModel):
    user_id: str
    case_id: str
    notes: Optional[str] = None

class ReadingListCreate(BaseModel):
    user_id: str
    name: str
    description: Optional[str] = None

@router.post("/bookmarks/add")
async def add_bookmark(bookmark: BookmarkCreate):
    """Add a bookmark."""
    try:
        new_bookmark = {
            "user_id": bookmark.user_id,
            "case_id": bookmark.case_id,
            "notes": bookmark.notes,
            "created_at": datetime.utcnow(),
        }
        result = await bookmarks_collection.insert_one(new_bookmark)
        return {"id": str(result.inserted_id), **new_bookmark}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add bookmark: {str(e)}")

@router.get("/bookmarks/list")
async def list_bookmarks(user_id: str = Query(...)):
    """List all bookmarks for a user."""
    try:
        cursor = bookmarks_collection.find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
        return {"bookmarks": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list bookmarks: {str(e)}")

@router.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(bookmark_id: str):
    """Delete a bookmark."""
    try:
        result = await bookmarks_collection.delete_one({"_id": ObjectId(bookmark_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Bookmark not found")
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete bookmark: {str(e)}")

@router.post("/reading-lists/create")
async def create_reading_list(reading_list: ReadingListCreate):
    """Create a new reading list."""
    try:
        new_list = {
            "user_id": reading_list.user_id,
            "name": reading_list.name,
            "description": reading_list.description,
            "cases": [],
            "created_at": datetime.utcnow(),
        }
        result = await reading_lists_collection.insert_one(new_list)
        return {"id": str(result.inserted_id), **new_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create reading list: {str(e)}")

@router.get("/reading-lists/list")
async def list_reading_lists(user_id: str = Query(...)):
    """List all reading lists for a user."""
    try:
        cursor = reading_lists_collection.find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
        return {"reading_lists": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reading lists: {str(e)}")
