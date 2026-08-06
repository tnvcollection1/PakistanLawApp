"""Download cases as text, JSON, or ZIP."""
import re, io, json, zipfile
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from server import db

router = APIRouter()
cases_collection = db["merged_caselaws"]

@router.get("/download/{case_id}")
async def download_case(case_id: str, format: str = "txt"):
    """Download a case in various formats."""
    try:
        doc = await cases_collection.find_one(
            {"_id": ObjectId(case_id)},
            {"raw_text": 0}
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        
        citation = doc.get("citation", "Unknown")
        title = doc.get("title", "Untitled")
        content = doc.get("full_content", "") or doc.get("headnotes", "No content available")
        
        if format.lower() == "txt":
            text = f"{citation}\n{title}\n\n{content}"
            output = io.BytesIO(text.encode('utf-8'))
            
            return StreamingResponse(
                output,
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename={citation.replace(' ', '_')}.txt"}
            )
        
        elif format.lower() == "json":
            doc["id"] = str(doc.pop("_id"))
            output = io.BytesIO(json.dumps(doc, indent=2, default=str).encode('utf-8'))
            
            return StreamingResponse(
                output,
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={citation.replace(' ', '_')}.json"}
            )
        
        elif format.lower() == "zip":
            output = io.BytesIO()
            with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
                text = f"{citation}\n{title}\n\n{content}"
                zf.writestr(f"{citation.replace(' ', '_')}.txt", text.encode('utf-8'))
                
                doc["id"] = str(doc.pop("_id"))
                zf.writestr(f"{citation.replace(' ', '_')}.json", json.dumps(doc, indent=2, default=str).encode('utf-8'))
            
            output.seek(0)
            return StreamingResponse(
                output,
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename={citation.replace(' ', '_')}.zip"}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use 'txt', 'json', or 'zip'")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
