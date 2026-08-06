"""AI Summarizer - Summarize legal text."""
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 500

@router.post("/ai/summarize")
async def ai_summarize(request: SummarizeRequest):
    """Summarize legal text."""
    try:
        text = request.text.strip()
        if len(text) <= request.max_length:
            return {"summary": text, "original_length": len(text), "summary_length": len(text)}
        
        # Simple extractive summarization - take first and last sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 3:
            summary = text[:request.max_length]
        else:
            # Take first and last sentences
            summary = ". ".join(sentences[:2] + sentences[-2:]) + "."
            if len(summary) > request.max_length:
                summary = summary[:request.max_length] + "..."
        
        return {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
