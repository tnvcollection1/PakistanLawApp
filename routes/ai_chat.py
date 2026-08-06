"""AI Chat Routes using OpenClaw (OpenAI-compatible gateway)."""
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/api/ai", tags=["AI Chat"])

OPENCLAW_URL = os.environ.get("OPENCLAW_URL", "http://localhost:18789/v1")

try:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(base_url=OPENCLAW_URL, api_key="not-needed")
    OPENAI_AVAILABLE = True
except ImportError:
    client = None
    OPENAI_AVAILABLE = False

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "moonshot/kimi-k2.6"
    temperature: float = 0.7
    max_tokens: int = 2000

class ChatResponse(BaseModel):
    message: str
    model: str

@router.post("/chat")
async def chat(request: ChatRequest):
    """General chat with AI using OpenClaw/Kimi."""
    if not OPENAI_AVAILABLE or not client:
        raise HTTPException(status_code=500, detail="AI chat not available")
    
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        response = await client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        return ChatResponse(
            message=response.choices[0].message.content,
            model=response.model,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.get("/health")
async def ai_health():
    """Check AI service health."""
    if not OPENAI_AVAILABLE or not client:
        return {"status": "unavailable", "openclaw_url": OPENCLAW_URL}
    
    try:
        # Try a simple completion to check health
        response = await client.chat.completions.create(
            model="moonshot/kimi-k2.6",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5,
        )
        return {"status": "ok", "model": response.model, "openclaw_url": OPENCLAW_URL}
    except Exception as e:
        return {"status": "error", "error": str(e), "openclaw_url": OPENCLAW_URL}
