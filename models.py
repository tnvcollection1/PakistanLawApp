from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    id: str = Field(..., alias="_id")
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: bool = False
    created_at: datetime = datetime.now()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class Case(BaseModel):
    id: str = Field(..., alias="_id")
    citation: str
    title: str
    year: int
    court: str
    judges: Optional[str] = None
    headnotes: Optional[str] = None
    full_content: Optional[str] = None
    pdf_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CaseSearchResult(BaseModel):
    id: str
    citation: str
    title: str
    year: int
    court: str
    judges: Optional[str] = None
    headnotes: Optional[str] = None
    snippet: Optional[str] = None
    score: Optional[float] = None

class CitationReference(BaseModel):
    text: str
    type: str  # "section", "cited_case", "legal_term", "court"
    context: Optional[str] = None
    count: int = 1

class AnalyticsOverview(BaseModel):
    total_cases: int
    total_courts: int
    total_judges: int
    years_range: str
    cases_by_year: Optional[List[dict]] = None
    cases_by_court: Optional[List[dict]] = None

class ExportRequest(BaseModel):
    case_id: str
    format: str  # "pdf", "word", "txt", "json"

class AIRequest(BaseModel):
    case_id: Optional[str] = None
    query: Optional[str] = None
    style: Optional[str] = "brief"  # "brief", "detailed", "bench"

class AISummary(BaseModel):
    case_id: str
    citation: str
    summary: str
    style: str
    generated_at: datetime

class HeadnoteStatus(BaseModel):
    total_cases: int
    cases_with_headnotes: int
    cases_without_headnotes: int
    percentage_complete: float
    last_updated: Optional[datetime] = None
