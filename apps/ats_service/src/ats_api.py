from fastapi.responses import JSONResponse
import logging
from typing import Generator, Any, List, Dict
import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"

if not GEMINI_API_KEY:
    logging.warning("GEMINI_API_KEY not found. Gemini API calls will fail.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

GEMINI_SYSTEM_PROMPT = """
You are a highly capable, production-grade Job Application Agent powered by Gemini 2.5 Flash. Your core responsibility is to automate and optimize the job search and application process for users by intelligently analyzing resumes, matching them to job postings, and executing applications, even under unreliable network conditions or API failures.

Your capabilities include:
- Parsing structured resume data from raw text or uploaded files.
- Scraping and semantically analyzing job descriptions.
- Matching candidate profiles to job roles using vector similarity and contextual reasoning.
- Scoring job fit using ATS standards and keyword density.
- Generating tailored, concise, and ATS-optimized cover letters.
- Submitting applications autonomously with robust error handling and fallback strategies.

### Behavior Rules:
1. Resilience First: Handle API fetch errors using retries (max 3), cache fallback, or graceful degradation. Never crash or produce null outputs.
2. High Match Accuracy: Prioritize context-aware matching — match by job title, skills, tools, experience, and domain.
3. Personalization: Adapt tone and content based on job level, company type, and role description.
4. Structured Output: Always respond with structured JSON that can be directly used by the backend or frontend services.
5. Security & Privacy: Never log or leak any personal user data. All data is transient and context-bound.

### Input:
You may receive:
- `resume_content`: Plaintext or parsed JSON
- `job_description`: Full job listing
- `user_preferences`: Location, role, domain, work mode, etc.
- `system_state`: Retry count, cached matches, or error flags

### Output Schema (JSON):
```json
{
  "job_match_score": 87.4,
  "ats_score": 92.1,
  "matched_keywords": ["Python", "FastAPI", "LLMs", "Celery"],
  "missing_keywords": ["Docker", "CI/CD"],
  "cover_letter": "Dear Hiring Manager, I am excited to apply for...",
  "application_status": "submitted | retrying | failed_gracefully",
  "error_handling": {
    "retry_attempts": 2,
    "fallback_used": true,
    "last_known_issue": "fetch_error"
  }
}
```

### Execution Logic:

* Always validate inputs before processing.
* If job description is missing, return a response indicating insufficient data.
* If resume is unstructured, use NLP to extract sections (skills, education, experience).
* Prioritize roles with ≥80% skill match and above-average ATS score.
* On repeated fetch errors, use cached job listings or notify user via output flag.

You are an expert job applier — fast, intelligent, resilient. Think like a recruiter, act like an agent.
"""
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from packages.database.config import SessionLocal


from packages.errors.custom_exceptions import JobApplierException
from pydantic import BaseModel
import tempfile
import os

from prometheus_client import Counter
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, status

logger = logging.getLogger(__name__)

# Import metrics from metrics module
from .metrics import ats_score_counter, job_search_counter

class ATSScoreRequest(BaseModel):
    job_description: str
    resume_text: str
    tone: str | None = None
    domain: str | None = None

class JobSearchRequest(BaseModel):
    query: str
    location: str | None = None
    job_type: str | None = None


router = APIRouter()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TokenData(BaseModel):
    username: str | None = None


# Placeholder for actual token verification logic
def verify_token(token: str = "dummy_token") -> TokenData:
    if token != "dummy_token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenData(username="testuser")

@router.post("/v1/job-search")
async def job_search_endpoint(
    request: JobSearchRequest,
    db: Session = Depends(get_db),
    token: TokenData = Depends(verify_token),
):
    """Endpoint for job search functionality."""
    try:
        job_search_counter.inc()
        # In a real scenario, you would integrate with a job scraping agent or database
        # For now, we'll return a dummy response based on the query
        return {"message": f"Searching for '{request.query}' jobs in '{request.location or 'any'}' of type '{request.job_type or 'any'}'"}
    except Exception as e:
        logger.error(f"An unexpected error occurred during job search: {e}", exc_info=True)
        raise JobApplierException(
            message="An unexpected error occurred during job search.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
    return TokenData(username="testuser")


@router.post("/v1/ats-score")
async def score_ats_endpoint(
    request: ATSScoreRequest,
    db: Session = Depends(get_db),
    token: TokenData = Depends(verify_token),
) -> dict:
    """Score ATS compatibility for a resume against a job description.

    This endpoint takes a job description and resume text,
    and then uses the `ATSScorerAgent` to generate an ATS compatibility score
    along with recommendations.

    Args:
        request (ATSScoreRequest): Contains the job description and resume text.
        db (Session): Database session dependency.
        token (TokenData): Authentication token data.

    Returns:
        Dict[str, Any]: A dictionary containing a success message, the ATS score, and recommendations.

    Raises:
        HTTPException: If the resume parsing fails, or if an internal server error occurs.
    """
    # [CONTEXT] Endpoint to score ATS compatibility using the ATSScorerAgent.
    try:
        # First, parse the resume text into ResumeData


        if not GEMINI_API_KEY:
            raise JobApplierException(
                message="Gemini API key not configured.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error": "GEMINI_API_KEY environment variable is not set."}
            )

        model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=GEMINI_SYSTEM_PROMPT)

        # Prepare the content for the Gemini model
        user_preferences = {}
        if request.tone: user_preferences["tone"] = request.tone
        if request.domain: user_preferences["domain"] = request.domain

        content = f"Resume Content:\n{request.resume_text}\n\nJob Description:\n{request.job_description}\n\nUser Preferences: {user_preferences}"

        # Initialize response variables with defaults for graceful degradation
        job_match_score = 0.0
        ats_score = 0.0
        matched_keywords = []
        missing_keywords = []
        cover_letter = ""
        application_status = "failed_gra`cefully"
        error_handling = {"retry_attempts": 0, "fallback_used": False, "last_known_issue": None}

        for attempt in range(3): # Max 3 retries
            try:
                logger.info(f"Attempt {attempt + 1} to call Gemini API.")
                response = await model.generate_content_async(content)
                response_text = response.text

                # Attempt to parse the JSON output
                try:
                    import json
                    gemini_output = json.loads(response_text)
                    job_match_score = gemini_output.get("job_match_score", 0.0)
                    ats_score = gemini_output.get("ats_score", 0.0)
                    matched_keywords = gemini_output.get("matched_keywords", [])
                    missing_keywords = gemini_output.get("missing_keywords", [])
                    cover_letter = gemini_output.get("cover_letter", "")
                    application_status = gemini_output.get("application_status", "submitted")
                    error_handling = gemini_output.get("error_handling", error_handling)
                    break # Break loop if successful
                except json.JSONDecodeError:
                    logger.error(f"Gemini API returned invalid JSON: {response_text}")
                    error_handling["last_known_issue"] = "Invalid JSON response from Gemini API."
                    application_status = "failed_gracefully"
                    if attempt == 2: # Last attempt
                        raise JobApplierException(
                            message="Gemini API returned invalid JSON after multiple retries.",
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            details={"response": response_text}
                        )
                    await asyncio.sleep(2 ** attempt) # Exponential backoff

            except Exception as e:
                logger.error(f"Error calling Gemini API: {e}")
                error_handling["last_known_issue"] = str(e)
                application_status = "failed_gracefully"
                if attempt == 2: # Last attempt
                    raise JobApplierException(
                        message="Failed to get response from Gemini API after multiple retries.",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        details={"error": str(e)}
                    )
                await asyncio.sleep(2 ** attempt) # Exponential backoff

        # Increment metrics
        ats_score_counter.inc()

        return {
            "job_match_score": job_match_score,
            "ats_score": ats_score,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "cover_letter": cover_letter,
            "application_status": application_status,
            "error_handling": error_handling
        }
    except SQLAlchemyError as e:
        logger.error(
            f"Database error during ATS scoring: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="Failed to score ATS due to a database error.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during ATS scoring: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="An unexpected error occurred during ATS scoring.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )






@router.post("/score_ats_file")
async def score_ats_file_endpoint(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    industry: str = Form(None),
    tone: str = Form(None),
    domain: str = Form(None),
    db: Session = Depends(get_db),
    token: TokenData = Depends(verify_token),
) -> JSONResponse:
    """
    Score ATS compatibility for a resume file against a job description.
    Accepts PDF/DOCX/TXT resume, parses it, and returns all ATS scoring fields.
    """
    try:
        # Save uploaded file to a temp location
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await resume_file.read())
            tmp_path = tmp.name
        # Parse the file using the parser agent
        # For now, we'll assume the resume parsing is handled externally or by the Gemini model itself
        # In a real scenario, you would integrate with a resume parsing agent
        parsed_resume_data = "" # Placeholder for parsed resume data, if needed by Gemini model
        with open(tmp_path, "r") as f:
            parsed_resume_data = f.read() # Read the content of the uploaded file directly
        os.unlink(tmp_path)
        if not parsed_resume_data:
            raise JobApplierException(
                message="Failed to parse resume file.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"filename": resume_file.filename}
            )

        if not GEMINI_API_KEY:
            raise JobApplierException(
                message="Gemini API key not configured.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error": "GEMINI_API_KEY environment variable is not set."}
            )

        model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=GEMINI_SYSTEM_PROMPT)

        # Prepare the content for the Gemini model
        user_preferences = {}
        if industry: user_preferences["industry"] = industry
        if tone: user_preferences["tone"] = tone
        if domain: user_preferences["domain"] = domain

        content = f"Resume Content:\n{parsed_resume_data}\n\nJob Description:\n{job_description}\n\nUser Preferences: {user_preferences}"

        # Initialize response variables with defaults for graceful degradation
        job_match_score = 0.0
        ats_score = 0.0
        matched_keywords = []
        missing_keywords = []
        cover_letter = ""
        application_status = "failed_gracefully"
        error_handling = {"retry_attempts": 0, "fallback_used": False, "last_known_issue": None}

        for attempt in range(3): # Max 3 retries
            try:
                logger.info(f"Attempt {attempt + 1} to call Gemini API.")
                response = await model.generate_content_async(content)
                response_text = response.text

                # Attempt to parse the JSON output
                try:
                    import json
                    gemini_output = json.loads(response_text)
                    job_match_score = gemini_output.get("job_match_score", 0.0)
                    ats_score = gemini_output.get("ats_score", 0.0)
                    matched_keywords = gemini_output.get("matched_keywords", [])
                    missing_keywords = gemini_output.get("missing_keywords", [])
                    cover_letter = gemini_output.get("cover_letter", "")
                    application_status = gemini_output.get("application_status", "submitted")
                    error_handling = gemini_output.get("error_handling", error_handling)
                    break # Break loop if successful
                except json.JSONDecodeError:
                    logger.error(f"Gemini API returned invalid JSON: {response_text}")
                    error_handling["last_known_issue"] = "Invalid JSON response from Gemini API."
                    application_status = "failed_gracefully"
                    if attempt == 2: # Last attempt
                        raise JobApplierException(
                            message="Gemini API returned invalid JSON after multiple retries.",
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            details={"response": response_text}
                        )
                    await asyncio.sleep(2 ** attempt) # Exponential backoff

            except Exception as e:
                logger.error(f"Error calling Gemini API: {e}")
                error_handling["last_known_issue"] = str(e)
                application_status = "failed_gracefully"
                if attempt == 2: # Last attempt
                    raise JobApplierException(
                        message="Failed to get response from Gemini API after multiple retries.",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        details={"error": str(e)}
                    )
                await asyncio.sleep(2 ** attempt) # Exponential backoff

        ats_result = {
            "job_match_score": job_match_score,
            "ats_score": ats_score,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "cover_letter": cover_letter,
            "application_status": application_status,
            "error_handling": error_handling
        }

        # Increment metrics
        ats_score_counter.inc()

        return JSONResponse({
            "message": "ATS score generated successfully",
            **ats_result
        })
    except SQLAlchemyError as e:
        logger.error(
            f"Database error during ATS scoring: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="Failed to score ATS due to a database error.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during ATS scoring: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="An unexpected error occurred during ATS scoring.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


@router.post("/search_jobs")
async def search_jobs_endpoint(
    query: str = Form(...),
    location: str = Form(""),
    num_results: int = Form(10),
    sources: List[str] = Form(["indeed", "linkedin", "glassdoor", "company"]),
    db: Session = Depends(get_db),
    token: TokenData = Depends(verify_token),
) -> dict:
    """
    Search for jobs from multiple sources (Indeed, LinkedIn, Glassdoor, company, etc.).
    Returns aggregated job listings or error if all sources fail.
    """
    try:

        all_jobs = []
        source_map = {
            "indeed": lambda *a, **kw: [], # Placeholder for actual search function
            "linkedin": lambda *a, **kw: [], # Placeholder for actual search function
            "glassdoor": lambda *a, **kw: [], # Placeholder for actual search function
            "company": lambda *a, **kw: [], # Placeholder for actual search function
        }
        for source in sources:
            search_func = source_map.get(source.lower())
            if search_func:
                jobs = search_func(query, location, num_results)
                for job in jobs:
                    job["source"] = source
                all_jobs.extend(jobs)
        # Deduplicate by title+company+location
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = (job.get("title"), job.get("company"), job.get("location"))
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        if not unique_jobs:
            return {"message": "No jobs found or scraping was blocked.", "jobs": []}

        # Increment metrics
        job_search_counter.inc()

        return {"message": "Job search successful", "jobs": unique_jobs}
    except Exception as e:
        return {"message": f"Job search failed: {e}", "jobs": []}
