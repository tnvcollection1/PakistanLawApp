"""Chatbot - Simple chatbot interface."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

class ChatbotMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

@router.post("/chatbot/message")
async def chatbot_message(msg: ChatbotMessage):
    """Send a message to the chatbot."""
    try:
        # Simple response logic
        user_msg = msg.message.lower()
        
        if "hello" in user_msg or "hi" in user_msg:
            response = "Hello! Welcome to Pakistan Law App. How can I assist you with legal research today?"
        elif "search" in user_msg:
            response = "You can search for cases using the search bar at the top. Try searching by citation, parties, or keywords."
        elif "citation" in user_msg:
            response = "You can search by citation using the format: YEAR JOURNAL PAGE. For example: 2023 PLD 123."
        elif "section" in user_msg or "act" in user_msg:
            response = "You can search by legal section using the Section Search feature. Try searching for 'Section 302 PPC'."
        elif "help" in user_msg:
            response = "I can help you with: searching cases, finding citations, explaining legal sections, and finding related cases. What would you like to do?"
        else:
            response = "I understand you're asking about legal research. Can you provide more details about what you're looking for? I can help with case searches, citation lookups, and legal analysis."
        
        return {
            "response": response,
            "session_id": msg.session_id or "default",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot failed: {str(e)}")

@router.get("/chatbot/health")
async def chatbot_health():
    """Check chatbot health."""
    return {"status": "ok", "version": "1.0"}
