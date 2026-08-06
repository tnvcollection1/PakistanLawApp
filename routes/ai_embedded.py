"""AI Embedded Routes — Context-aware AI helpers throughout the platform."""
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from server import db

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

router = APIRouter(prefix="/api/ai", tags=["AI Embedded"])
cases_collection = db["merged_caselaws"]

OPENCLAW_URL = os.environ.get("OPENCLAW_URL", "http://localhost:18789/v1")

if OPENAI_AVAILABLE:
    client = AsyncOpenAI(base_url=OPENCLAW_URL, api_key="not-needed")
else:
    client = None

class HeadnoteRequest(BaseModel):
    case_id: str

class SummaryRequest(BaseModel):
    case_id: str
    style: str = "brief"  # brief, detailed, bench

class SearchEnhanceRequest(BaseModel):
    query: str

class AskRequest(BaseModel):
    case_id: str
    question: str

class ExplainRequest(BaseModel):
    section: str
    act: str = "PPC"

class FindRelatedRequest(BaseModel):
    case_id: str

async def get_ai_client():
    if not client:
        raise HTTPException(status_code=500, detail="AI client not available")
    return client

@router.post("/generate-headnotes")
async def generate_headnotes(request: HeadnoteRequest):
    """Generate structured headnotes for a case."""
    try:
        from bson import ObjectId
        doc = await cases_collection.find_one({"_id": ObjectId(request.case_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        
        content = doc.get("full_content", "") or doc.get("headnotes", "")
        if not content:
            raise HTTPException(status_code=400, detail="Case has no content")
        
        ai_client = await get_ai_client()
        
        prompt = f"""Generate structured legal headnotes for the following Pakistani case law.
Extract: Facts, Issues, Law Applied, Decision, and Ratio Decidendi.

Case Content:
{content[:5000]}

Format as JSON with keys: facts, issues, law_applied, decision, ratio_decidendi."""
        
        response = await ai_client.chat.completions.create(
            model="moonshot/kimi-k2.6",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        
        headnotes = response.choices[0].message.content
        
        # Save to database
        await cases_collection.update_one(
            {"_id": ObjectId(request.case_id)},
            {"$set": {"ai_headnotes": headnotes, "headnotes_generated_at": doc.get("updated_at")}}
        )
        
        return {"case_id": request.case_id, "headnotes": headnotes}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Headnote generation failed: {str(e)}")

@router.post("/case-summary")
async def case_summary(request: SummaryRequest):
    """Generate a summary of a case in different styles."""
    try:
        from bson import ObjectId
        doc = await cases_collection.find_one({"_id": ObjectId(request.case_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        
        content = doc.get("full_content", "") or doc.get("headnotes", "")
        if not content:
            raise HTTPException(status_code=400, detail="Case has no content")
        
        ai_client = await get_ai_client()
        
        style_prompts = {
            "brief": "Summarize this case in 3-4 sentences. Focus on the holding and key facts.",
            "detailed": "Provide a comprehensive summary of this case. Include facts, procedural history, issues, analysis, and holding.",
            "bench": "Write this as a bench-style summary for a judge. Focus on the legal principles, precedents cited, and the ratio decidendi.",
        }
        
        prompt = f"""{style_prompts.get(request.style, style_prompts['brief'])}

Case: {doc.get('citation', 'Unknown')}
Title: {doc.get('title', 'Untitled')}

Content:
{content[:8000]}"""
        
        response = await ai_client.chat.completions.create(
            model="moonshot/kimi-k2.6",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        
        return {
            "case_id": request.case_id,
            "citation": doc.get("citation", ""),
            "style": request.style,
            "summary": response.choices[0].message.content,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

@router.post("/enhance-search")
async def enhance_search(request: SearchEnhanceRequest):
    """Parse search query and extract legal concepts."""
    try:
        ai_client = await get_ai_client()
        
        prompt = f"""Analyze this legal search query and extract key concepts, sections, and likely intent.

Query: "{request.query}"

Return JSON with:
- keywords: list of key legal terms
- sections: list of section numbers mentioned
- acts: list of acts mentioned
- intent: what the user is likely looking for (e.g., "case_law", "procedure", "definition")
- suggested_filters: object with suggested court, year range, etc."""
        
        response = await ai_client.chat.completions.create(
            model="moonshot/kimi-k2.6",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        
        return {
            "query": request.query,
            "analysis": response.choices[0].message.content,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search enhancement failed: {str(e)}")

@router.post("/ask-about-case")
async def ask_about_case(request: AskRequest):
    """Ask a specific question about a case."""
    try:
        from bson import ObjectId
        doc = await cases_collection.find_one({"_id": ObjectId(request.case_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        
        content = doc.get("full_content", "") or doc.get("headnotes", "")
        if not content:
            raise HTTPException(status_code=400, detail="Case has no content")
        
        ai_client = await get_ai_client()
        
        prompt = f"""Answer the following question about this Pakistani case law.

Case: {doc.get('citation', 'Unknown')}
Title: {doc.get('title', 'Untitled')}

Case Content:
{content[:6000]}

Question: {request.question}

Answer based only on the case content provided."""
        
        response = await ai_client.chat.completions.create(
            model="moonshot/kimi-k2.6",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        
        return {
            "case_id": request.case_id,
            "citation": doc.get("citation", ""),
            "question": request.question,
            "answer": response.choices[0].message.content,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Q&A failed: {str(e)}")

@router.post("/explain-section")
async def explain_section(request: ExplainRequest):
    """Explain a legal section in plain English."""
    try:
        ai_client = await get_ai_client()
        
        prompt = f"""Explain Section {request.section} of the {request.act} in plain English.
Include:
- What the section says
- What it means in practice
- Key legal concepts
- Relevant case law examples from Pakistan
- Common misconceptions

Make it accessible to law students and legal practitioners."""
        
        response = await ai_client.chat.completions.create(
            model="moonshot/kimi-k2.6",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        
        return {
            "section": request.section,
            "act": request.act,
            "explanation": response.choices[0].message.content,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

@router.post("/find-related")
async def find_related(request: FindRelatedRequest):
    """Find related cases using AI keyword extraction + MongoDB search."""
    try:
        from bson import ObjectId
        doc = await cases_collection.find_one({"_id": ObjectId(request.case_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        
        content = doc.get("full_content", "") or doc.get("headnotes", "")
        if not content:
            raise HTTPException(status_code=400, detail="Case has no content")
        
        ai_client = await get_ai_client()
        
        # Extract keywords using AI
        prompt = f"""Extract 5-10 key legal keywords from this case that would help find related cases.
Return only the keywords as a comma-separated list.

Case: {doc.get('citation', 'Unknown')}
{content[:3000]}"""
        
        response = await ai_client.chat.completions.create(
            model="moonshot/kimi-k2.6",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        
        keywords = response.choices[0].message.content.strip().split(",")
        keywords = [k.strip() for k in keywords if k.strip()]
        
        # Search for related cases using MongoDB $text
        related = []
        if keywords:
            query = " ".join(keywords)
            cursor = cases_collection.find(
                {"$text": {"$search": query}},
                {"raw_text": 0, "full_content": 0}
            ).limit(10)
            docs = await cursor.to_list(length=10)
            for d in docs:
                if str(d["_id"]) != request.case_id:
                    d["id"] = str(d.pop("_id"))
                    related.append(d)
        
        return {
            "case_id": request.case_id,
            "keywords": keywords,
            "related_cases": related,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Find related failed: {str(e)}")

@router.get("/headnote-status")
async def headnote_status():
    """Get progress stats on headnote generation."""
    try:
        total = await cases_collection.estimated_document_count()
        with_headnotes = await cases_collection.count_documents({"ai_headnotes": {"$exists": True}})
        without_headnotes = total - with_headnotes
        percentage = (with_headnotes / total * 100) if total > 0 else 0
        
        return {
            "total_cases": total,
            "cases_with_headnotes": with_headnotes,
            "cases_without_headnotes": without_headnotes,
            "percentage_complete": round(percentage, 2),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
