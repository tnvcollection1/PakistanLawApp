"""AI Streaming - Streaming AI responses."""
import os, asyncio, json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

class StreamRequest(BaseModel):
    message: str
    model: Optional[str] = "gpt-4"

@router.post("/ai/stream")
async def ai_stream(request: StreamRequest):
    """Stream AI responses."""
    async def generate():
        # Simulate streaming response
        words = ["I", "am", "an", "AI", "assistant", "for", "Pakistan", "Law", "App.", 
                 "I", "can", "help", "you", "with", "legal", "research", "and", "analysis."]
        for word in words:
            yield f"data: {json.dumps({'choices': [{'delta': {'content': word + ' '}}]})}\n\n"
            await asyncio.sleep(0.1)
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
