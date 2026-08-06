"""
Metadata Extraction - Extract structured data from legal documents.
Uses GPT-4o-mini for intelligent extraction.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from database import db
from openai import AsyncOpenAI
import os
import json
import re

router = APIRouter()

# OpenAI Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


class ExtractionRequest(BaseModel):
    case_id: str
    extract_fields: Optional[List[str]] = None


async def extract_metadata(content: str, fields: List[str] = None) -> Dict:
    """Extract metadata from case content using AI."""
    if not openai_client or not content:
        return {}
    
    default_fields = [
        "judge_name",
        "court",
        "case_type",
        "legal_issues",
        "statutes_cited",
        "outcome",
        "key_dates"
    ]
    
    fields = fields or default_fields
    
    prompt = f"""Extract the following metadata from this Pakistani legal case.
Return as JSON object.

Fields to extract: {', '.join(fields)}

Case Content:
{content[:4000]}

Extracted Metadata (JSON):"""

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract structured metadata from legal documents. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.2
        )
        
        text = response.choices[0].message.content
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {}
    except Exception as e:
        print(f"Metadata extraction failed: {e}")
        return {}


@router.post("/extract-metadata")
async def extract_case_metadata(request: ExtractionRequest):
    """Extract metadata from a legal case."""
    case = await db.pls_caselaws.find_one(
        {"case_id": request.case_id},
        {"_id": 0, "case_id": 1, "citation": 1, "full_content": 1, "headnotes": 1, "headnotes_text": 1}
    )
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    content = case.get("full_content") or case.get("headnotes_text") or case.get("headnotes") or ""
    
    if not content:
        raise HTTPException(status_code=400, detail="No content available for extraction")
    
    metadata = await extract_metadata(content, request.extract_fields)
    
    return {
        "case_id": request.case_id,
        "citation": case.get("citation"),
        "extracted_metadata": metadata
    }


@router.get("/extract-metadata/{case_id}")
async def get_metadata(case_id: str):
    """Get extracted metadata for a case."""
    return await extract_case_metadata(ExtractionRequest(case_id=case_id))
