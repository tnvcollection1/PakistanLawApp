"""Clean HTML - Clean and sanitize HTML content."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import re

router = APIRouter()

class CleanHTMLRequest(BaseModel):
    html: str
    remove_scripts: bool = True
    remove_styles: bool = True

@router.post("/clean-html")
async def clean_html(request: CleanHTMLRequest):
    """Clean and sanitize HTML content."""
    try:
        text = request.html
        
        # Remove script tags and content
        if request.remove_scripts:
            text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove style tags and content
        if request.remove_styles:
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return {
            "original_length": len(request.html),
            "cleaned_length": len(text),
            "cleaned": text,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTML cleaning failed: {str(e)}")
