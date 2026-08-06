from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import openai
import os

router = APIRouter()

openai.api_key = os.getenv("OPENAI_API_KEY")


@router.get("/find-similar")
async def find_similar_cases(
    case_id: str = Query(...),
    limit: int = Query(5, ge=1, le=20)
):
    """
    Find cases similar to a given case using AI analysis.
    """
    try:
        # In production, this would fetch the case text from the database
        # and use embeddings to find similar cases
        
        prompt = f"""Given case ID: {case_id}
        
        Suggest {limit} similar Pakistani legal cases that would be relevant.
        For each case, provide:
        1. Citation
        2. Brief description of similarity
        3. Relevance score (0-1)
        
        Respond in JSON format."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Pakistani legal research assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "case_id": case_id,
            "similar_cases": analysis,
            "total": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/analyze-case")
async def analyze_case(request: dict):
    """
    Analyze a case and extract key information.
    """
    case_text = request.get("text", "")
    if not case_text:
        raise HTTPException(status_code=400, detail="Case text is required")
    
    try:
        prompt = f"""Analyze the following Pakistani legal case and extract:
        
        1. Key legal issues
        2. Relevant statutes cited
        3. Precedents relied upon
        4. Court's reasoning
        5. Outcome/decision
        
        Case text:
        {case_text[:3000]}
        
        Respond in JSON format."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Pakistani legal analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=600
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "analysis": analysis,
            "text_length": len(case_text)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.get("/case-summary/{case_id}")
async def get_case_summary(case_id: str):
    """
    Generate a concise summary of a case.
    """
    try:
        prompt = f"""Provide a concise 3-paragraph summary of Pakistani case {case_id}.
        
        Include:
        1. Facts of the case
        2. Legal issues
        3. Decision and reasoning
        
        Keep it under 300 words."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Pakistani legal research assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=400
        )
        
        summary = response.choices[0].message.content
        
        return {
            "case_id": case_id,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary error: {str(e)}")
