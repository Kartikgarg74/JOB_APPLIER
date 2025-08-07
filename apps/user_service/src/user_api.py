from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from packages.database.models import User
from packages.database.config import SessionLocal
from packages.errors.custom_exceptions import JobApplierException
from passlib.context import CryptContext
from apps.job_applier_agent.src.auth.auth_api import get_current_user
from apps.job_applier_agent.src.auth.schemas import UserResponse, UserUpdate
from apps.user_service.src.main import limiter

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/users/me", response_model=UserResponse, dependencies=[Depends(limiter)])
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user's information.

    Retrieves the profile information of the currently authenticated user.

    Args:
        current_user (User): The authenticated user object.

    Returns:
        UserResponse: The user's profile information.
    """
    # [CONTEXT] Retrieve the currently authenticated user's information.
    try:
        return current_user
    except SQLAlchemyError as e:
        raise JobApplierException(
            message="Failed to retrieve user information due to a database error.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
    except Exception as e:
        raise JobApplierException(
            message="An unexpected error occurred while retrieving user information.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )






@router.put("/users/me", response_model=UserResponse, dependencies=[Depends(limiter)])
async def update_users_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's information.

    Updates the profile information of the currently authenticated user.

    Args:
        user_update (UserUpdate): The updated user information.
        current_user (User): The authenticated user object.
        db (Session): Database session dependency.

    Returns:
        UserResponse: The updated user's profile information.
    """
    # [CONTEXT] Update the currently authenticated user's information.
    try:
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(current_user, field, value)
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        return current_user
    except SQLAlchemyError as e:
        db.rollback()
        raise JobApplierException(
            message="Failed to update user information due to a database error.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(limiter)])
async def delete_users_me(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Delete current user's account.

    Deletes the account of the currently authenticated user.

    Args:
        current_user (User): The authenticated user object.
        db (Session): Database session dependency.

    Returns:
        None: Returns no content upon successful deletion.
    """
    # [CONTEXT] Delete the currently authenticated user's account.
    try:
        db.delete(current_user)
        db.commit()
        return
    except SQLAlchemyError as e:
        db.rollback()
        raise JobApplierException(
            message="Failed to delete user account due to a database error.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


# Admin endpoint to get all users (for demonstration, needs proper authorization)
@router.get("/users/all", response_model=list[UserResponse], dependencies=[Depends(limiter)])
async def get_all_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get all user accounts (Admin only).

    Retrieves a list of all user accounts. This endpoint is intended for administrative purposes
    and requires proper authorization.

    Args:
        db (Session): Database session dependency.
        current_user (User): The authenticated user object (for authorization).

    Returns:
        list[UserResponse]: A list of all user profiles.
    """
    # [CONTEXT] Retrieve all user accounts. This endpoint is for administrative purposes and requires proper authorization.
    # In a real application, this would be restricted to admin users only.
    # For now, it simply requires any authenticated user.
    try:
        users = db.query(User).all()
        return users
    except SQLAlchemyError as e:
        raise JobApplierException(
            message="Failed to retrieve all users due to a database error.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
    except Exception as e:
        raise JobApplierException(
            message="An unexpected error occurred while retrieving all users.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
