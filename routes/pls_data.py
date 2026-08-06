from fastapi import APIRouter, HTTPException
from server import db

router = APIRouter()
pls_collection = db["pls_data"]

@router.get("/pls-data")
async def get_pls_data():
    try:
        docs = await pls_collection.find().to_list(length=100)
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
        return {"data": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
