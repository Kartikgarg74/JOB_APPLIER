from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from packages.database.config import SessionLocal
from packages.agents.agent_manager import AgentManager
from pydantic import BaseModel
from typing import Dict, Any, Generator
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from packages.database.models import User
import logging
from packages.config.settings import settings
from packages.errors.custom_exceptions import JobApplierException

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
) -> Dict[str, Any]:
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
        logger.info(
            f"User {current_user.username} successfully initiated job application."
        )
        return {"message": "Application process initiated", "result": result}
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


@router.post("/coverletter/generate")
async def generate_cover_letter_endpoint(
    cover_letter_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Generate a cover letter.

    This endpoint uses the `CoverLetterGeneratorAgent` to generate a cover letter
    based on the provided data.

    Args:
        cover_letter_data (Dict[str, Any]): A dictionary containing data required for cover letter generation.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        Dict[str, Any]: A dictionary containing a success message and the generated cover letter.

    Raises:
        HTTPException: If an error occurs during cover letter generation.
    """
    # [CONTEXT] Endpoint to generate a cover letter using the CoverLetterGeneratorAgent.
    try:
        agent_manager = AgentManager(db)
        cover_letter_agent = agent_manager.get_cover_letter_generator_agent()
        generated_letter = cover_letter_agent.generate_cover_letter(cover_letter_data, job_description="")
        logger.info(
            f"User {current_user.username} successfully generated cover letter."
        )
        return {
            "message": "Cover letter generated successfully",
            "cover_letter": generated_letter,
        }
    except SQLAlchemyError as e:
        logger.error(
            f"Database error during cover letter generation for user {current_user.username}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="Failed to generate cover letter due to a database error.",
        )
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