"""AI Streaming Clean - Clean streaming implementation."""
import asyncio, json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class StreamCleanRequest(BaseModel):
    message: str

@router.post("/ai/stream-clean")
async def ai_stream_clean(request: StreamCleanRequest):
    """Clean streaming AI responses."""
    async def generate():
        response_text = "I am an AI assistant for Pakistan Law App. I can help you with legal research, case analysis, and more."
        words = response_text.split()
        for word in words:
            yield f"data: {json.dumps({'choices': [{'delta': {'content': word + ' '}}]})}\n\n"
            await asyncio.sleep(0.05)
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )
