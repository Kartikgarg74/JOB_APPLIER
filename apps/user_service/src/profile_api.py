from datetime import datetime
from datetime import datetime
from typing import List, Optional
import logging

from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from packages.errors.custom_exceptions import JobApplierException, NotificationError

from apps.job_applier_agent.src.auth_api import get_current_user
from packages.database.config import SessionLocal
from packages.database.models import User, Education, Experience, Project, JobPreference, Skill
from packages.notifications.notification_service import NotificationService
from packages.database.config import get_db
from packages.database.user_data_model import log_audit
from apps.job_applier_agent.src.main import profile_update_counter

logger = logging.getLogger(__name__)

router = APIRouter()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_notification_service() -> NotificationService:
    db_session = next(get_db())
    return NotificationService(db_session=db_session)


# Pydantic models for request and response
class UserProfileUpdate(BaseModel):
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    portfolio_url: Optional[str] = Field(None, max_length=255)
    personal_website: Optional[str] = Field(None, max_length=255)
    linkedin_profile: Optional[str] = Field(None, max_length=255)
    github_profile: Optional[str] = Field(None, max_length=255)
    years_of_experience: Optional[int] = Field(None, ge=0, le=100)
    skills: Optional[str] = Field(
        None, max_length=1000
    )  # Consider a List[str] and handle serialization
    onboarding_complete: Optional[bool] = Field(None, description="Has the user completed onboarding?")
    onboarding_step: Optional[str] = Field(None, description="Current onboarding step or progress.")
    job_preferences: Optional[dict] = Field(None, description="Job preferences for the user.")

    class Config:
        from_attributes = True


class EducationCreate(BaseModel):
    degree: str = Field(..., min_length=1, max_length=100)
    university: str = Field(..., min_length=1, max_length=100)
    field_of_study: str = Field(..., min_length=1, max_length=100)
    start_date: datetime
    end_date: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=1000)


class EducationResponse(EducationCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class EducationUpdate(BaseModel):
    degree: Optional[str] = Field(None, min_length=1, max_length=100)
    university: Optional[str] = Field(None, min_length=1, max_length=100)
    field_of_study: Optional[str] = Field(None, min_length=1, max_length=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=1000)


class ExperienceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    company: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    start_date: datetime
    end_date: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=1000)


class ExperienceResponse(ExperienceCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class ExperienceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    company: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=1000)


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)


class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    proficiency: Optional[str] = Field(None, max_length=50)


class SkillResponse(SkillCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True
    technologies: Optional[str] = Field(
        None, max_length=500
    )  # Consider a List[str] and handle serialization
    url: Optional[str] = Field(None, max_length=255)


class ProjectResponse(ProjectCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    technologies: Optional[str] = Field(None, max_length=500)
    url: Optional[str] = Field(None, max_length=255)


class JobPreferenceCreate(BaseModel):
    company_size: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    job_titles: Optional[str] = Field(
        None, max_length=500
    )  # Consider a List[str] and handle serialization
    locations: Optional[str] = Field(
        None, max_length=500
    )  # Consider a List[str] and handle serialization
    remote: Optional[bool] = False
    job_type: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    notifications: Optional[bool] = True


class JobPreferenceResponse(JobPreferenceCreate):
    id: int
    user_id: int


class JobPreferenceUpdate(BaseModel):
    company_size: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    job_titles: Optional[str] = Field(None, max_length=500)
    locations: Optional[str] = Field(None, max_length=500)
    remote: Optional[bool] = None
    job_type: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    notifications: Optional[bool] = None

    class Config:
        from_attributes = True


# User Profile Endpoints
@router.get("/profile", response_model=UserProfileUpdate)
async def get_user_profile(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Retrieve the current user's profile information.

    This endpoint fetches the detailed profile information for the authenticated user.

    Args:
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        UserProfileUpdate: The user's profile data.

    Raises:
        HTTPException: If the user profile is not found.
    """
    logger.info(f"Fetching profile for user ID: {current_user.id}")
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        logger.warning(f"User profile not found for ID: {current_user.id}")
        raise JobApplierException(
            status_code=status.HTTP_404_NOT_FOUND, message="User not found", error_code="USER_NOT_FOUND"
        )
    try:
        logger.info(f"Successfully fetched profile for user ID: {current_user.id}")
        return UserProfileUpdate(
            phone=user.phone,
            address=user.address,
            portfolio_url=user.portfolio_url,
            personal_website=user.personal_website,
            linkedin_profile=user.linkedin_profile,
            github_profile=user.github_profile,
            years_of_experience=user.years_of_experience,
            skills=user.skills,
            onboarding_complete=user.onboarding_complete,
            onboarding_step=user.onboarding_step,
        )
    except SQLAlchemyError as e:
        logger.error(
            f"Database error fetching profile for user {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="Failed to retrieve user profile due to a database error.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred fetching profile for user {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="An unexpected error occurred while retrieving user profile.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


@router.put("/profile", response_model=UserProfileUpdate)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the current user's profile information.

    Allows the authenticated user to update their profile details.

    Args:
        profile_data (UserProfileUpdate): The updated profile data.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        UserProfileUpdate: The updated user's profile data.

    Raises:
        HTTPException: If the user profile is not found or an error occurs during update.
    """
    logger.info(f"Updating profile for user ID: {current_user.id}")
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        logger.warning(
            f"User profile not found for ID: {current_user.id} during update attempt."
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update main profile fields
    for field, value in profile_data.dict(exclude_unset=True, exclude={"job_preferences"}).items():
        setattr(user, field, value)

    # Update job preferences if provided
    if hasattr(profile_data, "job_preferences") and profile_data.job_preferences:
        prefs = profile_data.job_preferences
        if user.job_preferences:
            for key, value in prefs.items():
                setattr(user.job_preferences, key, value)
        else:
            from packages.database.models import JobPreference
            user.job_preferences = JobPreference(**prefs)

    notification_service = get_notification_service()

    try:
        db.commit()
        db.refresh(user)
        profile_update_counter.inc()
        logging.info(f"AUDIT: Profile updated for user ID: {current_user.id}")
        log_audit(db, current_user.id, "profile_update", "users", current_user.id, {"fields": list(profile_data.dict(exclude_unset=True).keys())})
        logger.info(f"Successfully updated profile for user ID: {current_user.id}")
        try:
            notification_service.send_success_notification(
                current_user.id,
                "Profile Update Success",
                "Your profile has been successfully updated.",
            )
        except NotificationError as e:
            logger.error(f"Notification error for user {current_user.id}: {e}")
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error updating profile for user {current_user.id}: {e}",
            exc_info=True,
        )
        try:
            notification_service.send_failure_notification(
                current_user.id,
                "Profile Update Failed",
                f"Failed to update your profile due to a database error: {e}",
            )
        except NotificationError as notif_e:
            logger.error(f"Notification error for user {current_user.id}: {notif_e}")
        raise JobApplierException(
            message="Failed to update profile due to a database error.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"An unexpected error occurred updating profile for user {current_user.id}: {e}",
            exc_info=True,
        )
        try:
            notification_service.send_failure_notification(
                current_user.id,
                "Profile Update Failed",
                f"An unexpected error occurred while updating your profile: {e}",
            )
        except NotificationError as notif_e:
            logger.error(f"Notification error for user {current_user.id}: {notif_e}")
        raise JobApplierException(
            message="An unexpected error occurred while updating profile.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


@router.post("/profile", response_model=UserProfileUpdate, status_code=status.HTTP_201_CREATED)
async def create_user_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new user profile or update an existing one.

    This endpoint allows the authenticated user to create their profile information.
    If a profile already exists, it will be updated.

    Args:
        profile_data (UserProfileUpdate): The profile data to create or update.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        UserProfileUpdate: The created or updated user's profile data.

    Raises:
        JobApplierException: If an error occurs during creation or update.
    """
    logger.info(f"Attempting to create/update profile for user ID: {current_user.id}")
    user = db.query(User).filter(User.id == current_user.id).first()
    notification_service = get_notification_service()

    if not user:
        logger.warning(f"User not found for ID: {current_user.id}. Cannot create profile without a user.")
        raise JobApplierException(
            status_code=status.HTTP_404_NOT_FOUND, message="User not found", error_code="USER_NOT_FOUND"
        )

    try:
        for field, value in profile_data.dict(exclude_unset=True).items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        profile_update_counter.inc()
        logging.info(f"AUDIT: Profile created/updated for user ID: {current_user.id}")
        log_audit(db, current_user.id, "profile_create_or_update", "users", current_user.id, {"fields": list(profile_data.dict(exclude_unset=True).keys())})
        logger.info(f"Successfully created/updated profile for user ID: {current_user.id}")
        try:
            notification_service.send_success_notification(
                current_user.id,
                "Profile Creation/Update Success",
                "Your profile has been successfully created/updated.",
            )
        except NotificationError as e:
            logger.error(f"Notification error for user {current_user.id}: {e}")
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error creating/updating profile for user {current_user.id}: {e}",
            exc_info=True,
        )
        try:
            notification_service.send_failure_notification(
                current_user.id,
                "Profile Creation/Update Failed",
                f"Failed to create/update your profile due to a database error: {e}",
            )
        except NotificationError as notif_e:
            logger.error(f"Notification error for user {current_user.id}: {notif_e}")
        raise JobApplierException(
            message="Failed to create/update profile due to a database error.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"An unexpected error occurred creating/updating profile for user {current_user.id}: {e}",
            exc_info=True,
        )
        try:
            notification_service.send_failure_notification(
                current_user.id,
                "Profile Creation/Update Failed",
                f"An unexpected error occurred while creating/updating your profile: {e}",
            )
        except NotificationError as notif_e:
            logger.error(f"Notification error for user {current_user.id}: {notif_e}")
        raise JobApplierException(
            message="An unexpected error occurred while creating/updating profile.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


@router.post("/education", response_model=EducationResponse)
async def create_education(
    education: EducationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new education entry to the user's profile.

    Allows the authenticated user to add a new educational qualification to their profile.

    Args:
        education (EducationCreate): The education data to add.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        EducationResponse: The newly created education entry.

    Raises:
        JobApplierException: If an error occurs during creation.
    """
    logger.info(f"Creating education entry for user ID: {current_user.id}")
    db_education = Education(**education.dict(), user_id=current_user.id)
    try:
        db.add(db_education)
        db.commit()
        db.refresh(db_education)
        logger.info(
            f"Successfully created education entry for user ID: {current_user.id}"
        )
        return db_education
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error creating education entry for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to create education entry due to a database error.",
            details={"error": str(e)},
            error_code="DB_ERROR"
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"An unexpected error occurred creating education entry for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while creating education entry.",
            details={"error": str(e)},
            error_code="UNKNOWN_ERROR"
        )


@router.get("/education", response_model=List[EducationResponse])
async def get_all_education(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Retrieve all education entries for the current user.

    Fetches all educational qualifications associated with the authenticated user's profile.

    Args:
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        List[EducationResponse]: A list of education entries.

    Raises:
        JobApplierException: If an error occurs during retrieval.
    """
    logger.info(f"Fetching all education entries for user ID: {current_user.id}")
    try:
        education_entries = (
            db.query(Education).filter(Education.user_id == current_user.id).all()
        )
        logger.info(
            f"Successfully fetched {len(education_entries)} education entries for user ID: {current_user.id}"
        )
        return education_entries
    except SQLAlchemyError as e:
        logger.error(
            f"Database error fetching education entries for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error fetching education entries: {e}", error_code="DB_ERROR"
        )
    except Exception as e:
        logger.error(
            f"Error fetching education entries for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error fetching education entries: {e}", error_code="UNKNOWN_ERROR"
        )


@router.put("/education/{education_id}", response_model=EducationResponse)
async def update_education(
    education_id: int,
    education: EducationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing education entry.

    Allows the authenticated user to update a specific educational qualification by its ID.

    Args:
        education_id (int): The ID of the education entry to update.
        education (EducationUpdate): The updated education data.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        EducationResponse: The updated education entry.

    Raises:
        HTTPException: If the education entry is not found or an error occurs during update.
    """
    logger.info(
        f"Updating education entry {education_id} for user ID: {current_user.id}"
    )
    db_education = (
        db.query(Education)
        .filter(Education.id == education_id, Education.user_id == current_user.id)
        .first()
    )
    if not db_education:
        logger.warning(
            f"Education entry {education_id} not found for user ID: {current_user.id} during update attempt."
        )
        raise JobApplierException(
            status_code=status.HTTP_404_NOT_FOUND, message="Education entry not found", error_code="EDUCATION_NOT_FOUND"
        )
    for key, value in education.dict(exclude_unset=True).items():
        setattr(db_education, key, value)
    try:
        db.commit()
        db.refresh(db_education)
        logger.info(
            f"Successfully updated education entry {education_id} for user ID: {current_user.id}"
        )

        return db_education
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error updating education entry {education_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error updating education entry: {e}", error_code="DB_ERROR"
        )
    except Exception as e:
        logger.error(
            f"Error updating education entry {education_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error updating education entry: {e}", error_code="UNKNOWN_ERROR"
        )


@router.delete("/education/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(
    education_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an education entry.

    Allows the authenticated user to delete a specific educational qualification by its ID.

    Args:
        education_id (int): The ID of the education entry to delete.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        None

    Raises:
        JobApplierException: If the education entry is not found or an error occurs during deletion.
    """
    logger.info(
        f"Deleting education entry {education_id} for user ID: {current_user.id}"
    )
    try:
        db_education = (
            db.query(Education)
            .filter(Education.id == education_id, Education.user_id == current_user.id)
            .first()
        )
        if not db_education:
            logger.warning(
                f"Education entry {education_id} not found for user ID: {current_user.id} during deletion attempt."
            )
            raise JobApplierException(
                status_code=status.HTTP_404_NOT_FOUND, message="Education entry not found", error_code="EDUCATION_NOT_FOUND"
            )
        db.delete(db_education)
        db.commit()
        logger.info(
            f"Successfully deleted education entry {education_id} for user ID: {current_user.id}"
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error deleting education entry {education_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to delete education entry due to a database error.",
            details={"error": str(e)}
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"An unexpected error occurred deleting education entry {education_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while deleting education entry.",
            details={"error": str(e)}
        )


@router.post("/experience", response_model=ExperienceResponse)
async def create_experience(
    experience: ExperienceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new experience entry to the user's profile.

    Allows the authenticated user to add a new work experience to their profile.

    Args:
        experience (ExperienceCreate): The experience data to add.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        ExperienceResponse: The newly created experience entry.

    Raises:
        HTTPException: If an error occurs during creation.
    """
    logger.info(f"Creating experience entry for user ID: {current_user.id}")
    db_experience = Experience(**experience.dict(), user_id=current_user.id)
    try:
        db.add(db_experience)
        db.commit()
        db.refresh(db_experience)
        logger.info(
            f"Successfully created experience entry for user ID: {current_user.id}"
        )
        return db_experience
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error creating experience entry for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to create experience entry due to a database error.",
            details={"error": str(e)}
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"An unexpected error occurred creating experience entry for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while creating experience entry.",
            details={"error": str(e)}
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error creating experience entry for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error creating experience entry: {e}", error_code="DB_ERROR"
        )
    except Exception as e:
        logger.error(
            f"Error creating experience entry for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error creating experience entry: {e}", error_code="UNKNOWN_ERROR"
        )


@router.get("/experience", response_model=List[ExperienceResponse])
async def get_all_experience(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all experience entries for the current user.

    Fetches all work experience entries associated with the authenticated user's profile.

    Args:
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        List[ExperienceResponse]: A list of experience entries.

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    logger.info(f"Fetching all experience entries for user ID: {current_user.id}")
    try:
        experience_entries = (
            db.query(Experience).filter(Experience.user_id == current_user.id).all()
        )
        logger.info(
            f"Successfully fetched {len(experience_entries)} experience entries for user ID: {current_user.id}"
        )
        return experience_entries
    except SQLAlchemyError as e:
        logger.error(
            f"Database error fetching experience entries for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to retrieve experience entries due to a database error.",
            details={"error": str(e)},
            error_code="DB_ERROR"
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred fetching experience entries for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while fetching experience entries.",
            details={"error": str(e)},
            error_code="UNKNOWN_ERROR"
        )


@router.put("/experience/{experience_id}", response_model=ExperienceResponse)
async def update_experience(
    experience_id: int,
    experience: ExperienceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing experience entry.

    Allows the authenticated user to update a specific work experience by its ID.

    Args:
        experience_id (int): The ID of the experience entry to update.
        experience (ExperienceUpdate): The updated experience data.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        ExperienceResponse: The updated experience entry.

    Raises:
        HTTPException: If the experience entry is not found or an error occurs during update.
    """
    logger.info(
        f"Updating experience entry {experience_id} for user ID: {current_user.id}"
    )
    try:
        db_experience = (
            db.query(Experience)
            .filter(
                Experience.id == experience_id, Experience.user_id == current_user.id
            )
            .first()
        )
        if not db_experience:
            logger.warning(
                f"Experience entry {experience_id} not found for user ID: {current_user.id} during update attempt."
            )
            raise JobApplierException(
                status_code=status.HTTP_404_NOT_FOUND, message="Experience entry not found", error_code="EXPERIENCE_NOT_FOUND"
            )
        for key, value in experience.dict(exclude_unset=True).items():
            setattr(db_experience, key, value)
        db.commit()
        db.refresh(db_experience)
        logger.info(
            f"Successfully updated experience entry {experience_id} for user ID: {current_user.id}"
        )
        return db_experience
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error updating experience entry {experience_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to update experience entry due to a database error.",
            details={"error": str(e)},
            error_code="DB_ERROR"
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"An unexpected error occurred updating experience entry {experience_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while updating experience entry.",
            details={"error": str(e)},
            error_code="UNKNOWN_ERROR"
        )


@router.delete("/experience/{experience_id}")
async def delete_experience(
    experience_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an experience entry.

    Allows the authenticated user to delete a specific work experience by its ID.

    Args:
        experience_id (int): The ID of the experience entry to delete.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        Dict[str, str]: A confirmation message.

    Raises:
        HTTPException: If the experience entry is not found or an error occurs during deletion.
    """
    logger.info(
        f"Deleting experience entry {experience_id} for user ID: {current_user.id}"
    )
    db_experience = (
        db.query(Experience)
        .filter(Experience.id == experience_id, Experience.user_id == current_user.id)
        .first()
    )
    if not db_experience:
        logger.warning(
            f"Experience entry {experience_id} not found for user ID: {current_user.id} during delete attempt."
        )
        raise JobApplierException(
            status_code=status.HTTP_404_NOT_FOUND, message="Experience entry not found", error_code="EXPERIENCE_NOT_FOUND"
        )
    try:
        db.delete(db_experience)
        db.commit()
        logger.info(
            f"Successfully deleted experience entry {experience_id} for user ID: {current_user.id}"
        )
        return {"message": "Experience entry deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error deleting experience entry {experience_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to delete experience entry due to a database error.",
            details={"error": str(e)},
            error_code="DB_ERROR"
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"An unexpected error occurred deleting experience entry {experience_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while deleting experience entry.",
            details={"error": str(e)},
            error_code="UNKNOWN_ERROR"
        )


@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new project entry to the user's profile.

    Allows the authenticated user to add a new project to their profile.

    Args:
        project (ProjectCreate): The project data to add.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        ProjectResponse: The newly created project entry.

    Raises:
        HTTPException: If an error occurs during creation.
    """
    logger.info(f"Creating project entry for user ID: {current_user.id}")
    db_project = Project(**project.dict(), user_id=current_user.id)
    try:
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        logger.info(
            f"Successfully created project entry for user ID: {current_user.id}"
        )
        return db_project
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error creating project entry for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to create project entry due to a database error.",
            details={"error": str(e)},
            error_code="DB_ERROR"
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"An unexpected error occurred creating project entry for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while creating project entry.",
            details={"error": str(e)},
            error_code="UNKNOWN_ERROR"
        )


@router.get("/projects", response_model=List[ProjectResponse])
async def get_all_projects(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Retrieve all project entries for the current user.

    Fetches all projects associated with the authenticated user's profile.

    Args:
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        List[ProjectResponse]: A list of project entries.

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    logger.info(f"Fetching all project entries for user ID: {current_user.id}")
    try:
        project_entries = (
            db.query(Project).filter(Project.user_id == current_user.id).all()
        )
        logger.info(
            f"Successfully fetched {len(project_entries)} project entries for user ID: {current_user.id}"
        )
        return project_entries
    except SQLAlchemyError as e:
        logger.error(
            f"Database error fetching project entries for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to fetch project entries due to a database error.",
            details={"error": str(e)},
            error_code="DB_ERROR"
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred fetching project entries for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while fetching project entries.",
            details={"error": str(e)},
            error_code="UNKNOWN_ERROR"
        )


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing project entry.

    Allows the authenticated user to update a specific project by its ID.

    Args:
        project_id (int): The ID of the project entry to update.
        project (ProjectUpdate): The updated project data.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        ProjectResponse: The updated project entry.

    Raises:
        JobApplierException: If the project entry is not found or an error occurs during update.
    """
    logger.info(f"Updating project entry {project_id} for user ID: {current_user.id}")
    db_project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == current_user.id)
        .first()
    )
    if not db_project:
        logger.warning(
            f"Project entry {project_id} not found for user ID: {current_user.id} during update attempt."
        )
        raise JobApplierException(
            status_code=status.HTTP_404_NOT_FOUND, message="Project entry not found", error_code="PROJECT_NOT_FOUND"
        )
    for key, value in project.dict(exclude_unset=True).items():
        setattr(db_project, key, value)
    try:
        db.commit()
        db.refresh(db_project)
        logger.info(
            f"Successfully updated project entry {project_id} for user ID: {current_user.id}"
        )
        return db_project
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error updating project entry {project_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to update project entry due to a database error.",
            details={"error": str(e)},
            error_code="DB_ERROR"
        )
    except Exception as e:
        logger.error(
            f"Error updating project entry {project_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        db.rollback()
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while updating project entry.",
            details={"error": str(e)},
            error_code="UNKNOWN_ERROR"
        )


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a project entry.

    Allows the authenticated user to delete a specific project by its ID.

    Args:
        project_id (int): The ID of the project entry to delete.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        Dict[str, str]: A confirmation message.

    Raises:
        JobApplierException: If the project entry is not found or an error occurs during deletion.
    """
    logger.info(f"Deleting project entry {project_id} for user ID: {current_user.id}")
    db_project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == current_user.id)
        .first()
    )
    if not db_project:
        logger.warning(
            f"Project entry {project_id} not found for user ID: {current_user.id} during delete attempt."
        )
        raise JobApplierException(
            status_code=status.HTTP_404_NOT_FOUND, message="Project entry not found", error_code="PROJECT_NOT_FOUND"
        )
    try:
        db.delete(db_project)
        db.commit()
        logger.info(
            f"Successfully deleted project entry {project_id} for user ID: {current_user.id}"
        )
        return {"message": "Project entry deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error deleting project entry {project_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to delete project entry due to a database error.",
            details={"error": str(e)},
            error_code="DB_ERROR"
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"An unexpected error occurred deleting project entry {project_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while deleting project entry.",
            details={"error": str(e)},
            error_code="UNKNOWN_ERROR"
        )


@router.post("/job_preferences", response_model=JobPreferenceResponse)
async def create_job_preference(
    job_preference: JobPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new job preference entry for the user.

    Allows the authenticated user to add their job preferences.

    Args:
        job_preference (JobPreferenceCreate): The job preference data to add.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        JobPreferenceResponse: The newly created job preference entry.

    Raises:
        HTTPException: If an error occurs during creation.
    """
    logger.info(f"Creating job preference entry for user ID: {current_user.id}")
    try:
        # Check if job preferences already exist for this user
        existing_preference = (
            db.query(JobPreference)
            .filter(JobPreference.user_id == current_user.id)
            .first()
        )
        if existing_preference:
            logger.warning(
                f"Job preferences already exist for user ID: {current_user.id}. Use PUT to update."
            )
            raise JobApplierException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Job preferences already exist for this user. Use PUT to update.",
                error_code="JOB_PREFERENCE_EXISTS"
            )

        db_job_preference = JobPreference(
            **job_preference.dict(), user_id=current_user.id
        )
        db.add(db_job_preference)
        db.commit()
        db.refresh(db_job_preference)
        logger.info(
            f"Successfully created job preference entry for user ID: {current_user.id}"
        )
        return db_job_preference
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error creating job preference for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to create job preference due to a database error.",
            details={"error": str(e)},
            error_code="DB_ERROR"
        )
    except Exception as e:
        logger.error(
            f"Error creating job preference for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        db.rollback()
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while creating job preference.",
            details={"error": str(e)},
            error_code="UNKNOWN_ERROR"
        )


@router.get("/job_preferences", response_model=List[JobPreferenceResponse])
async def get_all_job_preferences(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Retrieve all job preference entries for the current user.

    Fetches all job preferences associated with the authenticated user's profile.

    Args:
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        List[JobPreferenceResponse]: A list of job preference entries.

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    logger.info(f"Fetching job preference entry for user ID: {current_user.id}")
    try:
        job_preference_entry = (
            db.query(JobPreference)
            .filter(JobPreference.user_id == current_user.id)
            .first()
        )
        if job_preference_entry:
            logger.info(
                f"Successfully fetched job preference entry for user ID: {current_user.id}"
            )
        else:
            logger.warning(
                f"No job preference entry found for user ID: {current_user.id}"
            )
        return job_preference_entry
    except SQLAlchemyError as e:
        logger.error(
            f"Database error fetching job preferences for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to fetch job preferences due to a database error.",
            details={"error": str(e)},
            error_code="DB_ERROR"
        )
    except Exception as e:
        logger.error(
            f"Error fetching job preferences for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while fetching job preferences.",
            details={"error": str(e)},
            error_code="UNKNOWN_ERROR"
        )


@router.put(
    "/job_preferences/{job_preference_id}", response_model=JobPreferenceResponse
)
async def update_job_preference(
    job_preference_id: int,
    job_preference: JobPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing job preference entry.

    Allows the authenticated user to update a specific job preference by its ID.

    Args:
        job_preference_id (int): The ID of the job preference entry to update.
        job_preference (JobPreferenceUpdate): The updated job preference data.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        JobPreferenceResponse: The updated job preference entry.

    Raises:
        HTTPException: If the job preference entry is not found or an error occurs during update.
    """
    logger.info(
        f"Updating job preference entry {job_preference_id} for user ID: {current_user.id}"
    )
    db_job_preference = (
        db.query(JobPreference)
        .filter(
            JobPreference.id == job_preference_id,
            JobPreference.user_id == current_user.id,
        )
        .first()
    )
    if not db_job_preference:
        logger.warning(
            f"Job preference entry {job_preference_id} not found for user ID: {current_user.id} during update attempt."
        )
        raise JobApplierException(
            status_code=status.HTTP_404_NOT_FOUND, message="Job preference not found", error_code="JOB_PREFERENCE_NOT_FOUND"
        )
    for key, value in job_preference.dict(exclude_unset=True).items():
        setattr(db_job_preference, key, value)
    try:
        db.commit()
        db.refresh(db_job_preference)
        logger.info(
            f"Successfully updated job preference entry {job_preference_id} for user ID: {current_user.id}"
        )
        return db_job_preference
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error updating job preference {job_preference_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to update job preference due to a database error.",
            details={"error": str(e)},
            error_code="DB_ERROR"
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"Error updating job preference {job_preference_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while updating job preference.",
            details={"error": str(e)},
            error_code="UNKNOWN_ERROR"
        )


@router.delete("/job_preferences/{job_preference_id}")
async def delete_job_preference(
    job_preference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a job preference entry.

    Allows the authenticated user to delete a specific job preference by its ID.

    Args:
        job_preference_id (int): The ID of the job preference entry to delete.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        Dict[str, str]: A confirmation message.

    Raises:
        JobApplierException: If the job preference entry is not found or an error occurs during deletion.
    """
    logger.info(
        f"Deleting job preference entry {job_preference_id} for user ID: {current_user.id}"
    )
    db_job_preference = (
        db.query(JobPreference)
        .filter(
            JobPreference.id == job_preference_id,
            JobPreference.user_id == current_user.id,
        )
        .first()
    )
    if not db_job_preference:
        logger.warning(
            f"Job preference entry {job_preference_id} not found for user ID: {current_user.id} during delete attempt."
        )
        raise JobApplierException(
            status_code=status.HTTP_404_NOT_FOUND, message="Job preference not found", error_code="JOB_PREFERENCE_NOT_FOUND"
        )
    try:
        db.delete(db_job_preference)
        db.commit()
        logger.info(
            f"Successfully deleted job preference entry {job_preference_id} for user ID: {current_user.id}"
        )
        return {"message": "Job preference entry deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error deleting job preference {job_preference_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to delete job preference due to a database error.",
            details={"error": str(e)},
            error_code="DB_ERROR"
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"Error deleting job preference {job_preference_id} for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while deleting job preference.",
            details={"error": str(e)},
            error_code="UNKNOWN_ERROR"
        )


@router.post("/skills", response_model=SkillResponse)
async def create_skill(
    skill: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new skill entry for the user.

    Allows the authenticated user to add a new skill to their profile.

    Args:
        skill (SkillCreate): The skill data to add.
        db (Session): Database session dependency.
        current_user (User): The authenticated user object.

    Returns:
        SkillResponse: The newly created skill entry.

    Raises:
        JobApplierException: If an error occurs during creation.
    """
    logger.info(f"Creating skill entry for user ID: {current_user.id}")
    try:
        db_skill = Skill(**skill.dict(), user_id=current_user.id)
        db.add(db_skill)
        db.commit()
        db.refresh(db_skill)
        logger.info(
            f"Successfully created skill entry for user ID: {current_user.id}"
        )
        return db_skill
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error creating skill for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to create skill due to a database error.",
            details={"error": str(e)},
            error_code="DB_ERROR"
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"An unexpected error occurred creating skill for user ID: {current_user.id}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while creating skill.",
            details={"error": str(e)},
            error_code="UNKNOWN_ERROR"
        )
