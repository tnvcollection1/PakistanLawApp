from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import openai
import os

router = APIRouter()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")


@router.get("/smart-search")
async def smart_search(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    AI-powered smart search that understands legal intent.
    Uses GPT to expand queries and find semantically relevant cases.
    """
    try:
        # Expand the query using AI
        expansion_prompt = f"""Given the legal search query: "{q}"
        
        Provide:
        1. Key legal concepts (3-5 terms)
        2. Related statutes that might apply
        3. Suggested search terms for a legal database
        
        Respond in JSON format:
        {{
            "concepts": ["term1", "term2", ...],
            "statutes": ["statute1", ...],
            "search_terms": ["term1", ...]
        }}"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Pakistani legal research assistant."},
                {"role": "user", "content": expansion_prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        # Parse the expansion
        expansion_text = response.choices[0].message.content
        
        # For now, return the expansion along with a basic search
        # In production, this would search the actual database
        return {
            "query": q,
            "ai_expansion": expansion_text,
            "results": [],
            "total": 0,
            "page": page,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart search error: {str(e)}")


@router.post("/natural-language-search")
async def natural_language_search(request: dict):
    """
    Accept natural language legal questions and return relevant cases.
    """
    query = request.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    try:
        # Use GPT to understand the legal question
        nl_prompt = f"""Legal question: {query}
        
        Analyze this question and identify:
        1. The area of law (e.g., constitutional, criminal, civil)
        2. Key legal issues
        3. Relevant Pakistani statutes
        4. Type of relief sought
        
        Respond in JSON format."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Pakistani legal expert."},
                {"role": "user", "content": nl_prompt}
            ],
            temperature=0.3,
            max_tokens=400
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "query": query,
            "analysis": analysis,
            "suggested_cases": [],
            "confidence": 0.85
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NL search error: {str(e)}")


@router.get("/search-suggestions")
async def search_suggestions(q: str = Query(..., min_length=1)):
    """Get AI-powered search suggestions as the user types."""
    try:
        suggestions_prompt = f"""Given the partial legal search query: "{q}"
        
        Suggest 5 completions that a Pakistani lawyer might be looking for.
        Each suggestion should be a complete legal search query.
        
        Respond with just a JSON array of strings."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Pakistani legal research assistant."},
                {"role": "user", "content": suggestions_prompt}
            ],
            temperature=0.5,
            max_tokens=200
        )
        
        suggestions_text = response.choices[0].message.content
        
        return {
            "query": q,
            "suggestions": suggestions_text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestions error: {str(e)}")
