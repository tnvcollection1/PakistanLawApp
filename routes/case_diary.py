"""Case Diary — Track court cases, hearings, and deadlines."""
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from database import db
from auth_utils import get_current_user
import uuid

router = APIRouter()


class CaseEntry(BaseModel):
    case_number: str
    title: str
    court: str
    judge: Optional[str] = ""
    party_petitioner: str
    party_respondent: str
    case_type: str = "Civil"
    status: str = "Pending"
    filing_date: Optional[str] = None
    next_hearing_date: Optional[str] = None
    description: Optional[str] = ""
    priority: str = "Medium"
    tags: Optional[List[str]] = []
    related_cases: Optional[List[str]] = []


class HearingEntry(BaseModel):
    case_id: str
    hearing_date: str
    purpose: str
    outcome: Optional[str] = ""
    next_date: Optional[str] = None
    notes: Optional[str] = ""
    attended: bool = True


class TaskEntry(BaseModel):
    case_id: Optional[str] = None
    title: str
    description: Optional[str] = ""
    due_date: Optional[str] = None
    priority: str = "Medium"
    status: str = "Pending"


@router.post("/diary/cases")
async def create_case(request: Request, case: CaseEntry):
    user = await get_current_user(request, db)
    doc = case.dict()
    doc["id"] = str(uuid.uuid4())
    doc["user_id"] = user["username"]
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.case_diary.insert_one(doc)
    return {"success": True, "case": doc}


@router.get("/diary/cases")
async def list_cases(
    request: Request,
    status: Optional[str] = None,
    case_type: Optional[str] = None,
    priority: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    user = await get_current_user(request, db)
    query = {"user_id": user["username"]}
    if status:
        query["status"] = status
    if case_type:
        query["case_type"] = case_type
    if priority:
        query["priority"] = priority
    if keyword:
        query["$or"] = [
            {"case_number": {"$regex": keyword, "$options": "i"}},
            {"title": {"$regex": keyword, "$options": "i"}},
            {"party_petitioner": {"$regex": keyword, "$options": "i"}},
            {"party_respondent": {"$regex": keyword, "$options": "i"}},
        ]
    skip = (page - 1) * limit
    cursor = db.case_diary.find(query).sort("next_hearing_date", 1).skip(skip).limit(limit)
    cases = await cursor.to_list(length=limit)
    for c in cases:
        c["_id"] = str(c.get("_id"))
    total = await db.case_diary.count_documents(query)
    return {"data": cases, "total": total, "page": page, "limit": limit}


@router.get("/diary/cases/{case_id}")
async def get_case(case_id: str, request: Request):
    user = await get_current_user(request, db)
    case = await db.case_diary.find_one({"id": case_id, "user_id": user["username"]})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case["_id"] = str(case.get("_id"))
    hearings_cursor = db.case_hearings.find({"case_id": case_id}).sort("hearing_date", -1)
    hearings = await hearings_cursor.to_list(length=100)
    for h in hearings:
        h["_id"] = str(h.get("_id"))
    tasks_cursor = db.case_tasks.find({"case_id": case_id}).sort("due_date", 1)
    tasks = await tasks_cursor.to_list(length=100)
    for t in tasks:
        t["_id"] = str(t.get("_id"))
    case["hearings"] = hearings
    case["tasks"] = tasks
    return case


@router.put("/diary/cases/{case_id}")
async def update_case(case_id: str, request: Request, case: CaseEntry):
    user = await get_current_user(request, db)
    existing = await db.case_diary.find_one({"id": case_id, "user_id": user["username"]})
    if not existing:
        raise HTTPException(status_code=404, detail="Case not found")
    update = case.dict()
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.case_diary.update_one({"id": case_id}, {"$set": update})
    return {"success": True}


@router.delete("/diary/cases/{case_id}")
async def delete_case(case_id: str, request: Request):
    user = await get_current_user(request, db)
    result = await db.case_diary.delete_one({"id": case_id, "user_id": user["username"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Case not found")
    await db.case_hearings.delete_many({"case_id": case_id})
    await db.case_tasks.delete_many({"case_id": case_id})
    return {"success": True}


@router.post("/diary/hearings")
async def create_hearing(request: Request, hearing: HearingEntry):
    user = await get_current_user(request, db)
    doc = hearing.dict()
    doc["id"] = str(uuid.uuid4())
    doc["user_id"] = user["username"]
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.case_hearings.insert_one(doc)
    if hearing.next_date:
        await db.case_diary.update_one(
            {"id": hearing.case_id},
            {"$set": {"next_hearing_date": hearing.next_date, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    return {"success": True, "hearing": doc}


@router.get("/diary/hearings")
async def list_hearings(
    request: Request,
    case_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    user = await get_current_user(request, db)
    query = {"user_id": user["username"]}
    if case_id:
        query["case_id"] = case_id
    if from_date or to_date:
        date_query = {}
        if from_date:
            date_query["$gte"] = from_date
        if to_date:
            date_query["$lte"] = to_date
        query["hearing_date"] = date_query
    cursor = db.case_hearings.find(query).sort("hearing_date", -1)
    hearings = await cursor.to_list(length=200)
    for h in hearings:
        h["_id"] = str(h.get("_id"))
    return {"data": hearings}


@router.delete("/diary/hearings/{hearing_id}")
async def delete_hearing(hearing_id: str, request: Request):
    user = await get_current_user(request, db)
    result = await db.case_hearings.delete_one({"id": hearing_id, "user_id": user["username"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Hearing not found")
    return {"success": True}


@router.post("/diary/tasks")
async def create_task(request: Request, task: TaskEntry):
    user = await get_current_user(request, db)
    doc = task.dict()
    doc["id"] = str(uuid.uuid4())
    doc["user_id"] = user["username"]
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.case_tasks.insert_one(doc)
    return {"success": True, "task": doc}


@router.get("/diary/tasks")
async def list_tasks(
    request: Request,
    case_id: Optional[str] = None,
    status: Optional[str] = None,
):
    user = await get_current_user(request, db)
    query = {"user_id": user["username"]}
    if case_id:
        query["case_id"] = case_id
    if status:
        query["status"] = status
    cursor = db.case_tasks.find(query).sort("due_date", 1)
    tasks = await cursor.to_list(length=200)
    for t in tasks:
        t["_id"] = str(t.get("_id"))
    return {"data": tasks}


@router.put("/diary/tasks/{task_id}")
async def update_task(task_id: str, request: Request, task: TaskEntry):
    user = await get_current_user(request, db)
    update = task.dict()
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.case_tasks.update_one(
        {"id": task_id, "user_id": user["username"]},
        {"$set": update}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}


@router.delete("/diary/tasks/{task_id}")
async def delete_task(task_id: str, request: Request):
    user = await get_current_user(request, db)
    result = await db.case_tasks.delete_one({"id": task_id, "user_id": user["username"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}


@router.get("/diary/stats")
async def get_stats(request: Request):
    user = await get_current_user(request, db)
    username = user["username"]
    total_cases = await db.case_diary.count_documents({"user_id": username})
    pending = await db.case_diary.count_documents({"user_id": username, "status": "Pending"})
    disposed = await db.case_diary.count_documents({"user_id": username, "status": "Disposed"})
    upcoming_hearings = await db.case_hearings.count_documents({
        "user_id": username,
        "hearing_date": {"$gte": datetime.now(timezone.utc).isoformat()[:10]}
    })
    pending_tasks = await db.case_tasks.count_documents({"user_id": username, "status": "Pending"})
    return {
        "total_cases": total_cases,
        "pending": pending,
        "disposed": disposed,
        "upcoming_hearings": upcoming_hearings,
        "pending_tasks": pending_tasks,
    }


@router.get("/diary/upcoming")
async def get_upcoming(request: Request, days: int = Query(7, ge=1, le=90)):
    user = await get_current_user(request, db)
    today = datetime.now(timezone.utc).isoformat()[:10]
    cursor = db.case_diary.find({
        "user_id": user["username"],
        "next_hearing_date": {"$gte": today},
        "status": {"$nin": ["Disposed", "Dismissed"]},
    }).sort("next_hearing_date", 1).limit(20)
    cases = await cursor.to_list(length=20)
    for c in cases:
        c["_id"] = str(c.get("_id"))
    task_cursor = db.case_tasks.find({
        "user_id": user["username"],
        "status": {"$nin": ["Completed"]},
    }).sort("due_date", 1).limit(20)
    tasks = await task_cursor.to_list(length=20)
    for t in tasks:
        t["_id"] = str(t.get("_id"))
    return {"upcoming_cases": cases, "pending_tasks": tasks}
