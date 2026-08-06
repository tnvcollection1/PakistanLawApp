"""Alerts system for case updates and notifications."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from server import db
from datetime import datetime

router = APIRouter()
alerts_collection = db["alerts"]
cases_collection = db["merged_caselaws"]

class AlertCreate(BaseModel):
    user_id: str
    query: str
    email: Optional[str] = None
    frequency: str = "daily"  # daily, weekly, monthly

@router.post("/alerts/create")
async def create_alert(alert: AlertCreate):
    """Create a new alert for case updates."""
    try:
        new_alert = {
            "user_id": alert.user_id,
            "query": alert.query,
            "email": alert.email,
            "frequency": alert.frequency,
            "created_at": datetime.utcnow(),
            "last_checked": None,
            "active": True,
        }
        result = await alerts_collection.insert_one(new_alert)
        return {"id": str(result.inserted_id), **new_alert}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")

@router.get("/alerts/list")
async def list_alerts(user_id: str = Query(...)):
    """List all alerts for a user."""
    try:
        cursor = alerts_collection.find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
        return {"alerts": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list alerts: {str(e)}")

@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete an alert."""
    try:
        from bson import ObjectId
        result = await alerts_collection.delete_one({"_id": ObjectId(alert_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete alert: {str(e)}")
