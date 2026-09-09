"""AI Chat Routes using OpenClaw (OpenAI-compatible gateway)."""
import os
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from database import db

router = APIRouter(tags=["AI Assistant"])
cases_collection = db["merged_caselaws"]
sessions_collection = db["chat_sessions"]
summaries_collection = db["case_summaries"]

# Ollama client setup (OpenAI-compatible API)
OPENCLAW_URL = os.environ.get("OPENCLAW_URL", "http://localhost:11434/v1")
DEFAULT_MODEL = os.environ.get("AI_MODEL", "smollm2:135m")

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []
    context_cases: Optional[List[dict]] = None

class QuickActionRequest(BaseModel):
    action: str
    params: Optional[dict] = {}

def _get_client():
    try:
        from openai import AsyncOpenAI
        return AsyncOpenAI(base_url=OPENCLAW_URL, api_key="not-needed")
    except ImportError:
        raise HTTPException(status_code=503, detail="AI client not available. Install: pip install openai")

SYSTEM_PROMPT = "You are a Pakistani legal research AI assistant. Help lawyers and law students research Pakistani case law, statutes, and legal procedures. Cite specific sections and cases when possible. Be precise and professional."

@router.get("/ai/health")
async def ai_health():
    try:
        client = _get_client()
        models = await client.models.list()
        model_list = [m.id for m in models.data] if hasattr(models, 'data') else ["smollm2:135m"]
        return {"status": "ok", "gateway": "Ollama", "models": model_list, "available": True}
    except Exception as e:
        return {"status": "error", "message": str(e), "available": False}

@router.get("/ai/models")
async def ai_models():
    try:
        client = _get_client()
        models = await client.models.list()
        model_list = [{"id": m.id, "name": m.id.split("/")[-1]} for m in models.data] if hasattr(models, 'data') else []
        return {"models": model_list or [{"id": "smollm2:135m", "name": "SmolLM2 135M"}]}
    except Exception:
        return {"models": [{"id": "smollm2:135m", "name": "SmolLM2 135M"}]}

@router.post("/ai/chat")
async def ai_chat(req: ChatRequest):
    try:
        client = _get_client()
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if req.history:
            messages.extend(req.history)
        if req.context_cases:
            ctx = "\n\n".join([f"Case {c.get('citation','')}: {c.get('headnotes','')[:500]}" for c in req.context_cases])
            messages.append({"role": "user", "content": f"Context cases:\n{ctx}\n\nQuestion: {req.message}"})
        else:
            messages.append({"role": "user", "content": req.message})

        response = await client.chat.completions.create(model=DEFAULT_MODEL, messages=messages, temperature=0.7, max_tokens=2048)
        return {"response": response.choices[0].message.content, "model": DEFAULT_MODEL}
    except HTTPException:
        raise
    except Exception as exc:
        return {"response": f"AI service temporarily unavailable: {str(exc)}", "model": DEFAULT_MODEL, "error": True}

@router.post("/ai/summarize")
async def ai_summarize(body: dict):
    try:
        case_id = body.get("case_id", "")
        cached = await summaries_collection.find_one({"case_id": case_id})
        if cached:
            return {"summary": cached["summary"], "model": DEFAULT_MODEL, "cached": True}

        doc = await cases_collection.find_one({"_id": ObjectId(case_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")

        client = _get_client()
        case_text = doc.get("full_content", doc.get("headnotes", ""))[:8000]
        citation = doc.get("citation", "Unknown")
        court = doc.get("court", "Unknown")
        date = doc.get("date", "Unknown")

        prompt = f"""You are a Pakistani legal research assistant. Summarize the following case in a structured format:
[1] FACTS - Brief facts of the case
[2] ISSUES - Legal questions raised
[3] HOLDING - Court's decision
[4] RATIO DECIDENDI - Reasoning behind the decision
[5] SIGNIFICANCE - Why this case is important

Case: {citation}
Court: {court}
Date: {date}

{case_text}"""

        response = await client.chat.completions.create(model=DEFAULT_MODEL, messages=[
            {"role": "system", "content": "You are a legal case summarizer. Provide concise, structured summaries."},
            {"role": "user", "content": prompt}
        ], temperature=0.3, max_tokens=2048)

        summary = response.choices[0].message.content
        await summaries_collection.insert_one({"case_id": case_id, "summary": summary, "model": DEFAULT_MODEL})
        return {"summary": summary, "model": DEFAULT_MODEL}
    except HTTPException:
        raise
    except Exception as exc:
        return {"summary": f"Could not generate summary: {str(exc)}", "error": True}

@router.post("/ai/quick-actions")
async def ai_quick_actions(req: QuickActionRequest):
    try:
        client = _get_client()
        action_prompts = {
            "explain_section": "Explain Section {section} of {act} in detail. Include punishment/provisions and relevant case law.",
            "compare_laws": "Compare {law_a} and {law_b} in Pakistani legal context.",
            "find_precedent": "Find relevant precedents for: {topic}. Cite specific cases.",
            "procedure_guide": "Provide a step-by-step procedure guide for: {procedure} in Pakistan.",
            "draft_petition": "Help draft a {petition_type} petition for {court}. Include standard format.",
        }
        prompt_template = action_prompts.get(req.action, "Help with: {action}")
        prompt = prompt_template.format(**req.params)

        response = await client.chat.completions.create(model=DEFAULT_MODEL, messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ], temperature=0.7, max_tokens=2048)

        return {"response": response.choices[0].message.content, "action": req.action, "model": DEFAULT_MODEL}
    except Exception as exc:
        return {"response": f"Quick action failed: {str(exc)}", "error": True}
