from fastapi import APIRouter, Depends, HTTPException, status
import logging
from typing import Generator, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from packages.database.config import SessionLocal
from packages.agents.agent_manager import AgentManager
from packages.common_types.common_types import ResumeData, JobListing
from packages.errors.custom_exceptions import JobApplierException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ATSScoreRequest(BaseModel):
    job_description: str
    resume_text: str


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


@router.post("/score_ats")
async def score_ats_endpoint(
    request: ATSScoreRequest,
    db: Session = Depends(get_db),
    token: TokenData = Depends(verify_token),
) -> dict[str, Any]:
    """Score ATS compatibility for a resume against a job description.

    This endpoint takes a job description and resume text, parses the resume,
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
        agent_manager = AgentManager(db)
        parser_agent = agent_manager.get_resume_parser_agent()
        parsed_resume_data = parser_agent.parse_resume(request.resume_text)

        if not parsed_resume_data:
            raise JobApplierException(
            message="Failed to parse resume text.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"resume_text_length": len(request.resume_text)}
        )

        ats_scorer_agent = agent_manager.get_ats_scorer_agent()

        # Create a dummy JobListing object for scoring
        job_listing_data: JobListing = {
            "job_id": "",  # Not relevant for scoring, can be empty
            "title": "",  # Not relevant for scoring, can be empty
            "company": "",  # Not relevant for scoring, can be empty
            "description": request.job_description,
            "requirements": request.job_description,  # Using job_description for requirements as well
            "application_url": "",  # Not relevant for scoring, can be empty
            "location": "",  # Not relevant for scoring, can be empty
            "job_type": None,  # Not relevant for scoring, can be empty
        }

        # Define weights (can be customized or fetched from user profile/settings)
        weights = {"keyword_match": 1.0, "skill_match": 1.5, "experience_match": 2.0}

        ats_result = ats_scorer_agent.score_ats(
            parsed_resume_data, request.job_description
        )
        return {
            "message": "ATS score generated successfully",
            "score": ats_result["score"],
            "recommendations": ats_result["recommendations"],
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