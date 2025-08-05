from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ErrorHandling(BaseModel):
    retry_attempts: int
    fallback_used: bool
    last_known_issue: Optional[str]

class ApplicationSubmissionResponse(BaseModel):
    job_match_score: float
    ats_score: Optional[float] = None
    matched_keywords: Optional[List[str]] = None
    missing_keywords: Optional[List[str]] = None
    cover_letter: Optional[str] = None
    application_status: str
    error_handling: ErrorHandling