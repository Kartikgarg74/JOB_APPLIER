from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from packages.database.config import SessionLocal
from packages.agents.agent_manager import AgentManager
from pydantic import BaseModel
from typing import Dict, Any, Generator
from frontend.lib.applications import ApplicationSubmissionResponse
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from packages.database.models import User
import logging
from packages.config.settings import settings
from packages.errors.custom_exceptions import JobApplierException
from apps.job_applier_agent.src.main import job_apply_counter
import google.generativeai as genai
import json

genai.configure(api_key=settings.GEMINI_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TokenData(BaseModel):
    username: str | None = None
    user_id: int | None = None


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str | None = payload.get("sub")
        user_id: int | None = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
        token_data = TokenData(username=username, user_id=user_id)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/match_jobs")
async def match_jobs_endpoint(
    user_profile: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Match jobs based on user profile.

    This endpoint uses the `JobMatcherAgent` to find suitable job listings
    based on the provided user profile.

    Args:
        user_profile (Dict[str, Any]): A dictionary containing the user's profile information.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        Dict[str, Any]: A dictionary containing a success message and the matched job listings.

    Raises:
        HTTPException: If an error occurs during the job matching process.
    """
    # [CONTEXT] Endpoint to match jobs using the JobMatcherAgent.
    try:
        agent_manager = AgentManager(db)
        job_matcher_agent = agent_manager.get_job_matcher_agent()
        matched_jobs = job_matcher_agent.match_jobs([user_profile])
        logger.info(f"User {current_user.username} successfully matched jobs.")
        return {"message": "Jobs matched successfully", "matched_jobs": matched_jobs}
    except SQLAlchemyError as e:
        logger.error(
            f"Database error matching jobs for user {current_user.username}: {e}", exc_info=True
        )
        raise JobApplierException(
            message="Failed to match jobs due to a database error.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while matching jobs for user {current_user.username}: {e}", exc_info=True
        )
        raise JobApplierException(
            message="An unexpected error occurred while matching jobs.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


@router.post("/apply")
async def apply_for_job_endpoint(
    application_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationSubmissionResponse:
    """Automate job application.

    This endpoint uses the `ApplicationAutomationAgent` to automate the job application process
    based on the provided application data.

    Args:
        application_data (Dict[str, Any]): A dictionary containing all necessary data for the application.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        Dict[str, Any]: A dictionary containing a message about the application status and results.

    Raises:
        HTTPException: If an error occurs during the application automation process.
    """
    # [CONTEXT] Endpoint to automate job application using the ApplicationAutomationAgent.
    try:
        agent_manager = AgentManager(db)
        app_automation_agent = agent_manager.get_application_automation_agent()
        result = app_automation_agent.apply_for_job(application_data)
        job_apply_counter.inc()
        logger.info(
            f"User {current_user.username} successfully initiated job application."
        )
        job_match_score = result.get("job_match_score", 0.0)
        return ApplicationSubmissionResponse(
            application_status="submitted",
            job_match_score=job_match_score,
            error_handling={
                "retry_attempts": 0,
                "fallback_used": False,
                "last_known_issue": None,
            },
        )
    except SQLAlchemyError as e:
        logger.error(
            f"Database error during application automation for user {current_user.username}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="Failed to automate application due to a database error.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during application automation for user {current_user.username}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="An unexpected error occurred during application automation.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


class CoverLetterRequest(BaseModel):
    resume_content: str
    job_description: str
    user_preferences: Dict[str, Any] = {}

@router.post("/coverletter/generate", summary="Generate a cover letter using Gemini 2.5 Flash")
async def generate_cover_letter_endpoint(
    request: CoverLetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Generate a cover letter using Gemini 2.5 Flash based on resume content and job description.

    Args:
        request (CoverLetterRequest): Request body containing resume content, job description, and user preferences.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        Dict[str, Any]: A dictionary containing a success message and the generated cover letter.

    Raises:
        HTTPException: If an error occurs during cover letter generation.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        
        prompt = f"""
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

        Please generate a tailored, concise, and ATS-optimized cover letter based on the following resume content and job description. Also, provide the job match score, ATS score, matched keywords, and missing keywords in the specified JSON format.

        Resume Content:
        {request.resume_content}

        Job Description:
        {request.job_description}

        User Preferences:
        {request.user_preferences}
        """
        
        response = model.generate_content(prompt)
        
        # Assuming the response is directly the JSON string
        generated_content = response.text
        
        # Parse the JSON response
        try:
            parsed_response = json.loads(generated_content)
            generated_letter = parsed_response.get("cover_letter", "")
            job_match_score = parsed_response.get("job_match_score", 0.0)
            ats_score = parsed_response.get("ats_score", 0.0)
            matched_keywords = parsed_response.get("matched_keywords", [])
            missing_keywords = parsed_response.get("missing_keywords", [])
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from Gemini response: {generated_content}")
            raise JobApplierException(
                message="Failed to parse Gemini response for cover letter generation.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"gemini_response": generated_content}
            )

        logger.info(
            f"User {current_user.username} successfully generated cover letter."
        )
        return {
            "message": "Cover letter generated successfully",
            "cover_letter": generated_letter,
            "job_match_score": job_match_score,
            "ats_score": ats_score,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
        }
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during cover letter generation for user {current_user.username}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="An unexpected error occurred during cover letter generation.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


@router.post("/unicorn/perform_magic")
async def perform_unicorn_magic_endpoint(
    user_profile_data: Dict[str, Any],
    job_posting_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Perform Unicorn magic.

    This endpoint uses the `UnicornAgent` to perform magical tasks
    based on the provided data.

    Args:
        user_profile_data (Dict[str, Any]): A dictionary containing the user's profile data.
        job_posting_data (Dict[str, Any]): A dictionary containing the job posting data.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        Dict[str, Any]: A dictionary containing a success message and the result of the magic.

    Raises:
        HTTPException: If an error occurs during Unicorn magic.
    """
    # [CONTEXT] Endpoint to perform Unicorn magic using the UnicornAgent.
    try:
        agent_manager = AgentManager(db)
        unicorn_agent = agent_manager.get_unicorn_agent()
        magic_result = await unicorn_agent.run({"user_profile": user_profile_data, "job_posting": job_posting_data})
        logger.info(
            f"User {current_user.username} successfully performed Unicorn magic."
        )
        return {"message": "Job application workflow initiated successfully", "result": magic_result}
    except SQLAlchemyError as e:
        logger.error(
            f"Database error during Unicorn magic for user {current_user.username}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="Failed to perform Unicorn magic due to a database error.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during Unicorn magic for user {current_user.username}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="An unexpected error occurred during Unicorn magic.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
