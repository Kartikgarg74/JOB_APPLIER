import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi import HTTPException # Keep HTTPException for standard HTTP errors
from packages.errors.custom_exceptions import JobApplierException
from sqlalchemy.exc import SQLAlchemyError
from fastapi_limiter.depends import RateLimiter
from google.auth.transport import requests
from google.oauth2 import id_token
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from packages.database.config import SessionLocal
from packages.database.models import User
from packages.config.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .schemas import UserCreate, UserLogin, UserResponse, GoogleAuthCallback

logger = logging.getLogger(__name__)

router = APIRouter()

# Google OAuth2 Client ID
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

if not GOOGLE_CLIENT_ID:
    raise ValueError("GOOGLE_CLIENT_ID environment variable not set")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=5, seconds=10))])
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # [CONTEXT] Register a new user, supporting both password-based and Google OAuth registration
    logger.info(f"Attempting to register user: {user.username}")
    if user.password and user.google_id:
        logger.warning(
            f"Registration failed for {user.username}: Cannot register with both password and Google ID"
        )
        raise JobApplierException(
            message="Cannot register with both password and Google ID",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"reason": "Both password and Google ID provided"}
        )

    if not user.password and not user.google_id:
        logger.warning(
            f"Registration failed for {user.username}: Must provide either password or Google ID"
        )
        raise JobApplierException(
            message="Must provide either password or Google ID for registration",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"reason": "Neither password nor Google ID provided"}
        )

    if user.password:
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            logger.warning(
                f"Registration failed for {user.username}: Username already registered"
            )
            raise JobApplierException(
            message="Username already registered",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"username": user.username}
        )
        hashed_password = pwd_context.hash(user.password)
        new_user = User(
            username=user.username, email=user.email, password_hash=hashed_password
        )
    else:  # Google OAuth registration
        db_user = db.query(User).filter(User.google_id == user.google_id).first()
        if db_user:
            logger.warning(
                f"Registration failed for {user.username}: Google ID already registered"
            )
            raise JobApplierException(
            message="Google ID already registered",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"google_id": user.google_id}
        )
        new_user = User(
            username=user.username,
            email=user.email,
            google_id=user.google_id,
            image=user.image,
        )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"User {new_user.username} registered successfully.")
        return new_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error during registration for {user.username}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="Internal server error during registration",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e), "username": user.username}
        )
    except Exception as e:
        logger.error(
            f"Unexpected error during registration for {user.username}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="An unexpected error occurred during registration",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e), "username": user.username}
        )


@router.post("/login", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=5, seconds=10))])
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # [CONTEXT] Authenticate user and generate a token
    logger.info(f"Attempting to log in user: {user.username}")
    db_user = db.query(User).filter(User.username == user.username).first()
    try:
        if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
            logger.warning(f"Login failed for {user.username}: Invalid credentials")
            raise JobApplierException(
                message="Invalid credentials",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"username": user.username}
            )
    except SQLAlchemyError as e:
        logger.error(
            f"Database error during login for {user.username}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="Internal server error during login",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e), "username": user.username}
        )
    except Exception as e:
        logger.error(
            f"Unexpected error during login for {user.username}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="An unexpected error occurred during login",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e), "username": user.username}
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username, "user_id": db_user.id},
        expires_delta=access_token_expires,
    )
    logger.info(f"User {user.username} logged in successfully.")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth/google", dependencies=[Depends(RateLimiter(times=5, seconds=10))])
async def google_auth_callback(data: GoogleAuthCallback, db: Session = Depends(get_db)):
    # [CONTEXT] Handle Google OAuth callback, verify token, and manage user
    logger.info("Attempting Google OAuth authentication.")
    try:
        # Verify the ID token
        idinfo = id_token.verify_oauth2_token(
            data.id_token, requests.Request(), GOOGLE_CLIENT_ID
        )

        # Extract user information
        google_id = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo.get("name", email.split("@")[0])
        image = idinfo.get("picture")

        user = db.query(User).filter(User.google_id == google_id).first()
        if not user:
            # New user, register them
            logger.info(f"Registering new user via Google OAuth: {email}")
            new_user = User(
                username=name, email=email, google_id=google_id, image=image
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user = new_user
        else:
            logger.info(f"User {email} already exists, logging in via Google OAuth.")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires,
        )
        logger.info(f"Google authentication successful for user: {email}")
        return {
            "message": "Google authentication successful",
            "user_id": user.id,
            "access_token": access_token,
            "token_type": "bearer",
            "email": user.email,
            "image": user.image,
        }

    except ValueError as e:
        logger.warning(f"Google OAuth failed: Invalid Google ID token - {e}")
        raise JobApplierException(
            message="Invalid Google ID token",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details={"error": str(e)}
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error during Google OAuth authentication: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="Internal server error during Google OAuth authentication",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
    except Exception as e:
        logger.error(f"Google OAuth authentication failed: {e}", exc_info=True)
        raise JobApplierException(
            message="Google authentication failed",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error": str(e)}
        )
