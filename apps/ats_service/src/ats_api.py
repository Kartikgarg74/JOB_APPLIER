from fastapi.responses import JSONResponse
import logging
from typing import Generator, Any, List, Dict
import os
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import google.api_core.exceptions
import json
import spacy
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key") # TODO: Replace with a strong, unique key from environment variables
ALGORITHM = "HS256"


# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logging.warning("spaCy model 'en_core_web_sm' not found. Downloading...")
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

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

def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience="job-applier")
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        return TokenData(username=username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

class ATSScorer:
    def __init__(self, nlp_model: Any):
        self.nlp = nlp_model

    def parse_text(self, text: str) -> Dict[str, Any]:
        doc = self.nlp(text)
        # This is a simplified parsing. In a real scenario, you'd extract more structured data.
        return {"text": text, "tokens": [token.text for token in doc]}

    def score_skills(self, job_skills: List[str], resume_skills: List[str]) -> float:
        job_skills_lower = {s.lower() for s in job_skills}
        resume_skills_lower = {s.lower() for s in resume_skills}
        matched = len(job_skills_lower.intersection(resume_skills_lower))
        if not job_skills_lower: return 100.0
        return (matched / len(job_skills_lower)) * 100

    def score_experience(self, job_exp: str, resume_exp: str) -> float:
        # Simple keyword matching for demonstration
        job_exp_lower = job_exp.lower()
        resume_exp_lower = resume_exp.lower()
        score = 0.0
        if "senior" in job_exp_lower and "senior" in resume_exp_lower: score += 30
        elif "mid" in job_exp_lower and "mid" in resume_exp_lower: score += 20
        elif "junior" in job_exp_lower and "junior" in resume_exp_lower: score += 10
        else: score += 5 # Basic match

        # More sophisticated matching would involve years of experience, project types, etc.
        return min(score, 100.0)

    def score_education(self, job_edu: str, resume_edu: str) -> float:
        job_edu_lower = job_edu.lower()
        resume_edu_lower = resume_edu.lower()
        score = 0.0
        if "bachelor" in job_edu_lower and "bachelor" in resume_edu_lower: score += 30
        if "master" in job_edu_lower and "master" in resume_edu_lower: score += 40
        if "phd" in job_edu_lower and "phd" in resume_edu_lower: score += 50
        if "degree" in job_edu_lower and "degree" in resume_edu_lower: score += 20
        return min(score, 100.0)

    def score_location(self, job_loc: str, resume_loc: str) -> float:
        if job_loc.lower() == resume_loc.lower():
            return 100.0
        return 0.0

    def calculate_ats_score(self, job_description: str, resume_text: str) -> Dict[str, Any]:
        # This is a highly simplified example. Real NLP would extract entities.
        # For demonstration, let's assume we can extract some keywords.
        # In a real scenario, you'd use NER, dependency parsing, etc.

        # Dummy extraction for skills, experience, education, location
        # These would come from more advanced NLP or structured data
        job_desc_lower = job_description.lower()
        resume_text_lower = resume_text.lower()

        # Example: Extract skills (very basic, needs improvement)
        job_skills = []
        resume_skills = []
        common_skills = ["python", "java", "sql", "fastapi", "react", "aws", "docker", "kubernetes", "nlp", "machine learning"]
        for skill in common_skills:
            if skill in job_desc_lower: job_skills.append(skill)
            if skill in resume_text_lower: resume_skills.append(skill)

        # Example: Experience (dummy)
        job_experience = "senior" if "senior" in job_desc_lower else "mid" if "mid" in job_desc_lower else "junior"
        resume_experience = "senior" if "senior" in resume_text_lower else "mid" if "mid" in resume_text_lower else "junior"

        # Example: Education (dummy)
        job_education = "bachelor" if "bachelor" in job_desc_lower else "none"
        resume_education = "bachelor" if "bachelor" in resume_text_lower else "none"

        # Example: Location (dummy)
        job_location = "remote" if "remote" in job_desc_lower else "new york"
        resume_location = "remote" if "remote" in resume_text_lower else "new york"

        skill_score = self.score_skills(job_skills, resume_skills)
        experience_score = self.score_experience(job_experience, resume_experience)
        education_score = self.score_education(job_education, resume_education)
        location_score = self.score_location(job_location, resume_location)

        # Weighted average
        total_score = (
            skill_score * 0.40 +
            experience_score * 0.30 +
            education_score * 0.20 +
            location_score * 0.10
        )

        # Dummy matched/missing keywords for now
        matched_keywords = list(set(job_skills).intersection(set(resume_skills)))
        missing_keywords = list(set(job_skills) - set(resume_skills))

        return {
            "job_match_score": total_score,
            "ats_score": total_score, # For simplicity, using same for now
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "cover_letter": "", # This will be generated by Gemini
            "application_status": "",
            "error_handling": {},
            "score_breakdown": {
                "skills": skill_score,
                "experience": experience_score,
                "education": education_score,
                "location": location_score,
            },
            "improvement_suggestions": [
                "Tailor your resume to include more keywords from the job description.",
                "Highlight projects relevant to the required experience."
            ]
        }


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


        ats_scorer = ATSScorer(nlp)
        ats_result = ats_scorer.calculate_ats_score(request.job_description, request.resume_text)

        # Initialize response variables with defaults for graceful degradation
        job_match_score = ats_result["job_match_score"]
        ats_score = ats_result["ats_score"]
        matched_keywords = ats_result["matched_keywords"]
        missing_keywords = ats_result["missing_keywords"]
        cover_letter = ats_result["cover_letter"]
        application_status = "submitted" # Assuming success if ATS score calculated
        error_handling = {"retry_attempts": 0, "fallback_used": False, "last_known_issue": None}

        # If Gemini API key is configured, use Gemini for cover letter generation
        if GEMINI_API_KEY:
            @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(google.api_core.exceptions.GoogleAPIError))
            def get_gemini_model():
                return genai.GenerativeModel(GEMINI_MODEL, system_instruction=GEMINI_SYSTEM_PROMPT)
            model = get_gemini_model()

            user_preferences = {}
            if request.tone: user_preferences["tone"] = request.tone
            if request.domain: user_preferences["domain"] = request.domain

            content = f"""Resume Content:
{request.resume_text}

Job Description:
{request.job_description}

User Preferences: {user_preferences}"""

            for attempt in range(3): # Max 3 retries
                try:
                    logger.info(f"Attempt {attempt + 1} to call Gemini API.")
                    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(google.api_core.exceptions.GoogleAPIError))
                    async def generate_content_with_retry(model_obj, content_str):
                        return await model_obj.generate_content_async(content_str)
                    response = await generate_content_with_retry(model, content)
                    gemini_output = response.text

                    try:
                        parsed_gemini_output = json.loads(gemini_output)
                        cover_letter = parsed_gemini_output.get("cover_letter", cover_letter)
                        # Optionally update other fields if Gemini provides them
                        # job_match_score = parsed_gemini_output.get("job_match_score", job_match_score)
                        # ats_score = parsed_gemini_output.get("ats_score", ats_score)
                        # matched_keywords = parsed_gemini_output.get("matched_keywords", matched_keywords)
                        # missing_keywords = parsed_gemini_output.get("missing_keywords", missing_keywords)
                        # application_status = parsed_gemini_output.get("application_status", application_status)
                        # error_handling = parsed_gemini_output.get("error_handling", error_handling)
                    except json.JSONDecodeError:
                        logger.warning("Gemini output is not valid JSON. Using raw text as cover letter.")
                        cover_letter = gemini_output # Fallback to raw text if not JSON
                    break # Break loop if successful
                except Exception as e:
                    logger.error(f"Gemini API call failed (attempt {attempt + 1}): {e}")
                    error_handling["retry_attempts"] = attempt + 1
                    error_handling["last_known_issue"] = str(e)
                    if attempt == 2: # Last attempt
                        error_handling["fallback_used"] = True
                        application_status = "failed_gracefully"
                    await asyncio.sleep(2 ** attempt) # Exponential backoff

        # Increment metrics
        ats_score_counter.inc()
        # You can use token_data.username for user-specific logic if needed

        return {
            "message": "ATS score calculated successfully",
            "job_match_score": job_match_score,
            "ats_score": ats_score,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "cover_letter": cover_letter,
            "application_status": application_status,
            "error_handling": error_handling,
            "score_breakdown": ats_result.get("score_breakdown", {}),
            "improvement_suggestions": ats_result.get("improvement_suggestions", []),
        }
    except SQLAlchemyError as e:
        logger.error(
            f"Database error during ATS scoring: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="An unexpected error occurred during ATS scoring.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )






@router.post("/v1/ats-score-file")
async def score_ats_file_endpoint(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    tone: str | None = Form(None),
    domain: str | None = Form(None),
    db: Session = Depends(get_db),
    token_data: TokenData = Depends(verify_token),
) -> dict:
    """Score ATS compatibility for an uploaded resume file against a job description.

    This endpoint takes an uploaded resume file and a job description,
    and then uses the `ATSScorerAgent` to generate an ATS compatibility score
    along with recommendations.

    Args:
        resume_file (UploadFile): The uploaded resume file.
        job_description (str): The job description text.
        tone (str | None): User preference for cover letter tone.
        domain (str | None): User preference for cover letter domain.
        db (Session): Database session dependency.
        token (TokenData): Authentication token data.

    Returns:
        Dict[str, Any]: A dictionary containing a success message, the ATS score, and recommendations.

    Raises:
        HTTPException: If the resume parsing fails, or if an internal server error occurs.
    """
    try:
        MAX_FILE_SIZE_MB = 5
        MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

        # Check file size
        resume_file.file.seek(0, os.SEEK_END)  # Move to the end of the file
        file_size = resume_file.file.tell()  # Get the current position (which is the file size)
        resume_file.file.seek(0)  # Seek back to the beginning of the file

        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds the limit of {MAX_FILE_SIZE_MB}MB."
            )

        # Read the content of the uploaded resume file
        resume_text = (await resume_file.read()).decode("utf-8")

        ats_scorer = ATSScorer(nlp)
        ats_result = ats_scorer.calculate_ats_score(job_description, resume_text)

        # Initialize response variables with defaults for graceful degradation
        job_match_score = ats_result["job_match_score"]
        ats_score = ats_result["ats_score"]
        matched_keywords = ats_result["matched_keywords"]
        missing_keywords = ats_result["missing_keywords"]
        cover_letter = ats_result["cover_letter"]
        application_status = "submitted" # Assuming success if ATS score calculated
        error_handling = {"retry_attempts": 0, "fallback_used": False, "last_known_issue": None}

        # If Gemini API key is configured, use Gemini for cover letter generation
        if GEMINI_API_KEY:
            @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(google.api_core.exceptions.GoogleAPIError))
            def get_gemini_model():
                return genai.GenerativeModel(GEMINI_MODEL, system_instruction=GEMINI_SYSTEM_PROMPT)
            model = get_gemini_model()

            user_preferences = {}
            if tone: user_preferences["tone"] = tone
            if domain: user_preferences["domain"] = domain

            content = f"""Resume Content:
{resume_text}

Job Description:
{job_description}

User Preferences: {user_preferences}"""

            for attempt in range(3): # Max 3 retries
                try:
                    logger.info(f"Attempt {attempt + 1} to call Gemini API.")
                    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(google.api_core.exceptions.GoogleAPIError))
                    async def generate_content_with_retry(model_obj, content_str):
                        return await model_obj.generate_content_async(content_str)
                    response = await generate_content_with_retry(model, content)
                    gemini_output = response.text

                    try:
                        parsed_gemini_output = json.loads(gemini_output)
                        cover_letter = parsed_gemini_output.get("cover_letter", cover_letter)
                    except json.JSONDecodeError:
                        logger.warning("Gemini output is not valid JSON. Using raw text as cover letter.")
                        cover_letter = gemini_output # Fallback to raw text if not JSON
                    break # Break loop if successful
                except Exception as e:
                    logger.error(f"Gemini API call failed (attempt {attempt + 1}): {e}")
                    error_handling["retry_attempts"] = attempt + 1
                    error_handling["last_known_issue"] = str(e)
                    if attempt == 2: # Last attempt
                        error_handling["fallback_used"] = True
                        application_status = "failed_gracefully"
                    await asyncio.sleep(2 ** attempt) # Exponential backoff

        # Increment metrics
        ats_score_counter.inc()

        return {
            "message": "ATS score calculated successfully",
            "job_match_score": job_match_score,
            "ats_score": ats_score,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "cover_letter": cover_letter,
            "application_status": application_status,
            "error_handling": error_handling,
            "score_breakdown": ats_result.get("score_breakdown", {}),
            "improvement_suggestions": ats_result.get("improvement_suggestions", []),
        }
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        logger.error(
            f"Database error during ATS scoring: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to score ATS due to a database error."
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during ATS scoring: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during ATS scoring."
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
