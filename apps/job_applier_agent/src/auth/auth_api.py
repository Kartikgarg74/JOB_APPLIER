import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, status, Response, Cookie, Request
from fastapi import HTTPException # Keep HTTPException for standard HTTP errors
from packages.errors.custom_exceptions import JobApplierException
from sqlalchemy.exc import SQLAlchemyError
from fastapi_limiter.depends import RateLimiter
from google.auth.transport import requests
from google.oauth2 import id_token
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import pyotp
import qrcode
import io
from fastapi.responses import StreamingResponse
import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time

from packages.database.config import SessionLocal
from packages.database.models import User
from packages.config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REDIS_URL, REDIS_TOKEN
from .schemas import UserCreate, UserLogin, UserResponse, GoogleAuthCallback
from packages.utilities.email_utils import send_email
import secrets
from packages.database.models import InAppNotification
from fastapi.security import OAuth2PasswordBearer
from packages.database.models import Skill, Project, Experience, Education, JobPreference
from packages.utilities.encryption_utils import mask_email, mask_phone
from apps.job_applier_agent.src.metrics import signup_counter, login_counter
from prometheus_client import Gauge
import redis

# In-memory blacklist for demo (use Redis/DB in production)
REVOKED_REFRESH_TOKENS = set()

REFRESH_TOKEN_EXPIRE_DAYS = 7

# In-memory IP blocklist for demo (use Redis in production)
FAILED_ATTEMPTS = {}
BLOCKED_IPS = {}
BLOCK_WINDOW = 600  # 10 minutes
BLOCK_THRESHOLD = 5
BLOCK_DURATION = 900  # 15 minutes

# Redis connection for user activity tracking (adjust host/port as needed)
redis_client = redis.Redis.from_url(REDIS_URL, password=REDIS_TOKEN)
dau_gauge = Gauge('active_users_daily', 'Number of unique users active today')
wau_gauge = Gauge('active_users_weekly', 'Number of unique users active this week')
mau_gauge = Gauge('active_users_monthly', 'Number of unique users active this month')

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


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Example common password list (expand in production)
COMMON_PASSWORDS = {"password", "12345678", "qwerty", "letmein", "admin", "welcome", "iloveyou"}

def is_strong_password(password: str) -> Optional[str]:
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one digit."
    if not re.search(r"[^A-Za-z0-9]", password):
        return "Password must contain at least one special character."
    if password.lower() in COMMON_PASSWORDS:
        return "Password is too common. Choose a more secure password."
    return None


def get_client_ip(request: Request):
    return request.client.host

class IPBlockMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        ip = get_client_ip(request)
        now = time.time()
        # Remove expired blocks
        if ip in BLOCKED_IPS and BLOCKED_IPS[ip] < now:
            del BLOCKED_IPS[ip]
        if ip in BLOCKED_IPS:
            return JSONResponse({"detail": "Too many failed attempts. Try again later."}, status_code=429)
        response = await call_next(request)
        return response

# Add middleware to app (in main.py, but for demo, add here if possible)
# app.add_middleware(IPBlockMiddleware)

# Helper to record failed attempts
def record_failed_attempt(ip):
    now = time.time()
    attempts = FAILED_ATTEMPTS.get(ip, [])
    # Remove old attempts
    attempts = [t for t in attempts if now - t < BLOCK_WINDOW]
    attempts.append(now)
    FAILED_ATTEMPTS[ip] = attempts
    if len(attempts) >= BLOCK_THRESHOLD:
        BLOCKED_IPS[ip] = now + BLOCK_DURATION


@router.post("/register", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=5, seconds=10))])
async def register_user(user: UserCreate, db: Session = Depends(get_db), request: Request = None):
    ip = get_client_ip(request)
    if ip in BLOCKED_IPS and BLOCKED_IPS[ip] > time.time():
        raise HTTPException(status_code=429, detail="Too many failed attempts. Try again later.")
    logger.info(f"Attempting to register user: {user.username}")
    if user.password and user.google_id:
        record_failed_attempt(ip)
        logger.warning(
            f"Registration failed for {user.username}: Cannot register with both password and Google ID"
        )
        raise JobApplierException(
            message="Cannot register with both password and Google ID",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"reason": "Both password and Google ID provided"}
        )

    if not user.password and not user.google_id:
        record_failed_attempt(ip)
        logger.warning(
            f"Registration failed for {user.username}: Must provide either password or Google ID"
        )
        raise JobApplierException(
            message="Must provide either password or Google ID for registration",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"reason": "Neither password nor Google ID provided"}
        )

    if user.password:
        # Enforce password policy
        policy_error = is_strong_password(user.password)
        if policy_error:
            record_failed_attempt(ip)
            logger.warning(f"Registration failed for {user.username}: {policy_error}")
            raise JobApplierException(
                message=policy_error,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"username": user.username}
            )
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            record_failed_attempt(ip)
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
            record_failed_attempt(ip)
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
        # Send welcome email
        send_email(
            new_user.email,
            "Welcome to Job Applier!",
            f"Hi {new_user.username},\n\nWelcome to Job Applier! We're excited to have you on board. Start exploring job opportunities and let us help you land your dream job!\n\nBest,\nThe Job Applier Team"
        )
        logger.info(f"User {new_user.username} registered successfully.")
        signup_counter.inc()
        if ip in FAILED_ATTEMPTS:
            del FAILED_ATTEMPTS[ip]
        log_audit(db, new_user.id, "register", "users", new_user.id, {"ip": ip})
        return new_user
    except SQLAlchemyError as e:
        record_failed_attempt(ip)
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
        record_failed_attempt(ip)
        logger.error(
            f"Unexpected error during registration for {user.username}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="An unexpected error occurred during registration",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e), "username": user.username}
        )


@router.post("/2fa/setup", dependencies=[Depends(RateLimiter(times=5, seconds=10))])
def setup_2fa(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.two_fa_enabled:
        raise HTTPException(status_code=400, detail="2FA already enabled")
    secret = pyotp.random_base32()
    user.two_fa_secret = secret
    user.two_fa_method = "totp"
    db.commit()
    db.refresh(user)
    log_audit(db, user.id, "2fa_setup", "users", user.id, {"ip": None})
    # Generate provisioning URI and QR code
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=user.email, issuer_name="JobApplier")
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

@router.post("/2fa/verify", dependencies=[Depends(RateLimiter(times=5, seconds=10))])
def verify_2fa(user_id: int, code: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.two_fa_secret:
        raise HTTPException(status_code=404, detail="2FA not setup for user")
    totp = pyotp.TOTP(user.two_fa_secret)
    if totp.verify(code):
        user.two_fa_enabled = True
        db.commit()
        log_audit(db, user.id, "2fa_verify", "users", user.id, {"ip": None})
        return {"message": "2FA enabled"}
    else:
        raise HTTPException(status_code=400, detail="Invalid 2FA code")

@router.post("/2fa/disable", dependencies=[Depends(RateLimiter(times=5, seconds=10))])
def disable_2fa(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.two_fa_enabled:
        raise HTTPException(status_code=404, detail="2FA not enabled for user")
    user.two_fa_enabled = False
    user.two_fa_secret = None
    user.two_fa_method = None
    db.commit()
    log_audit(db, user.id, "2fa_disable", "users", user.id, {"ip": None})
    return {"message": "2FA disabled"}

# Modify login to require 2FA code if enabled
@router.post("/login", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=5, seconds=10))])
async def login_user(user: UserLogin, response: Response, db: Session = Depends(get_db), two_fa_code: str = None, request: Request = None):
    ip = get_client_ip(request)
    if ip in BLOCKED_IPS and BLOCKED_IPS[ip] > time.time():
        raise HTTPException(status_code=429, detail="Too many failed attempts. Try again later.")
    logger.info(f"Attempting to log in user: {user.username}")
    db_user = db.query(User).filter(User.username == user.username).first()
    try:
        if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
            record_failed_attempt(ip)
            log_audit(db, None, "login_failed", "users", None, {"username": user.username, "ip": ip})
            logger.warning(f"Login failed for {user.username}: Invalid credentials")
            raise JobApplierException(
                message="Invalid credentials",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"username": user.username}
            )
        # If 2FA is enabled, require code
        if db_user.two_fa_enabled:
            if not two_fa_code:
                record_failed_attempt(ip)
                raise HTTPException(status_code=401, detail="2FA code required")
            totp = pyotp.TOTP(db_user.two_fa_secret)
            if not totp.verify(two_fa_code):
                record_failed_attempt(ip)
                raise HTTPException(status_code=401, detail="Invalid 2FA code")
        login_counter.inc()
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
    # On success, clear failed attempts
    if ip in FAILED_ATTEMPTS:
        del FAILED_ATTEMPTS[ip]
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username, "user_id": db_user.id},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={"sub": db_user.username, "user_id": db_user.id}
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        samesite="lax",
        secure=True,
    )
    logger.info(f"User {user.username} logged in successfully.")
    log_audit(db, db_user.id, "login", "users", db_user.id, {"ip": ip})
    # After successful login:
    user_id = db_user.id
    today = datetime.utcnow().strftime('%Y-%m-%d')
    week = datetime.utcnow().strftime('%Y-%U')
    month = datetime.utcnow().strftime('%Y-%m')
    redis_client.sadd(f"active_users:daily:{today}", user_id)
    redis_client.sadd(f"active_users:weekly:{week}", user_id)
    redis_client.sadd(f"active_users:monthly:{month}", user_id)
    dau = redis_client.scard(f"active_users:daily:{today}")
    wau = redis_client.scard(f"active_users:weekly:{week}")
    mau = redis_client.scard(f"active_users:monthly:{month}")
    dau_gauge.set(dau)
    wau_gauge.set(wau)
    mau_gauge.set(mau)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def refresh_token_endpoint(refresh_token: Optional[str] = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")
    if refresh_token in REVOKED_REFRESH_TOKENS:
        raise HTTPException(status_code=401, detail="Refresh token revoked")
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("user_id")
        username = payload.get("sub")
        access_token = create_access_token({"sub": username, "user_id": user_id})
        return {"access_token": access_token, "token_type": "bearer"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid refresh token: {e}")


@router.post("/logout", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def logout(response: Response, refresh_token: Optional[str] = Cookie(None)):
    if refresh_token:
        REVOKED_REFRESH_TOKENS.add(refresh_token)
        response.delete_cookie("refresh_token")
        log_audit(None, None, "logout", "users", None, {"ip": None})
    return {"message": "Logged out"}


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

@router.post("/request-password-reset", dependencies=[Depends(RateLimiter(times=3, seconds=60))])
def request_password_reset(email: str, db: Session = Depends(get_db), request: Request = None):
    ip = get_client_ip(request)
    if ip in BLOCKED_IPS and BLOCKED_IPS[ip] > time.time():
        raise HTTPException(status_code=429, detail="Too many failed attempts. Try again later.")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        record_failed_attempt(ip)
        # Do not reveal if email exists
        return {"message": "If the email exists, a reset link has been sent."}
    token = secrets.token_urlsafe(32)
    user.password_reset_token = token
    user.password_reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    reset_link = f"https://your-frontend-domain/reset-password?token={token}"
    send_email(user.email, "Password Reset Request", f"Click the link to reset your password: {reset_link}")
    log_audit(db, user.id, "request_password_reset", "users", user.id, {"ip": ip})
    if ip in FAILED_ATTEMPTS:
        del FAILED_ATTEMPTS[ip]
    return {"message": "If the email exists, a reset link has been sent."}

@router.post("/reset-password", dependencies=[Depends(RateLimiter(times=3, seconds=60))])
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.password_reset_token == token).first()
    if not user or not user.password_reset_token_expiry or user.password_reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    # Enforce password policy
    policy_error = is_strong_password(new_password)
    if policy_error:
        raise HTTPException(status_code=400, detail=policy_error)
    user.password_hash = pwd_context.hash(new_password)
    user.password_reset_token = None
    user.password_reset_token_expiry = None
    db.commit()
    log_audit(db, user.id, "reset_password", "users", user.id, {"ip": None})
    return {"message": "Password has been reset successfully."}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Dummy get_current_user for demo (replace with real JWT/session logic)
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # In production, decode JWT and fetch user
    user = db.query(User).first()  # Replace with real user lookup
    return user

# Dummy is_admin flag for demonstration (replace with real RBAC logic)
def is_admin(user: User) -> bool:
    return getattr(user, 'is_admin', False)

# Example: In any endpoint returning user data, mask PII if the requester is not the user
# For demonstration, update gdpr_export to support masking (add a mask parameter)
@router.get("/gdpr/export")
async def gdpr_export(db: Session = Depends(get_db), user: User = Depends(get_current_user), mask: bool = False, target_user_id: int = None):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # Only allow export for self or admin
    if target_user_id and (user.id != target_user_id and not is_admin(user)):
        raise HTTPException(status_code=403, detail="Forbidden: Cannot export another user's data.")
    export_user = user
    if target_user_id and (user.id == target_user_id or is_admin(user)):
        export_user = db.query(User).filter_by(id=target_user_id).first()
        if not export_user:
            raise HTTPException(status_code=404, detail="User not found")
    def maybe_mask(val, mask_fn):
        return mask_fn(val) if mask else val
    def show_email_logic():
        if user.id == export_user.id or is_admin(user):
            return export_user.email
        if export_user.show_email and export_user.profile_visibility != "private":
            return maybe_mask(export_user.email, mask_email) if mask else export_user.email
        return None
    data = {
        "user": {
            "id": export_user.id,
            "username": export_user.username,
            "email": show_email_logic(),
            "phone": maybe_mask(export_user.phone, mask_phone) if (user.id != export_user.id and not is_admin(user)) else export_user.phone,
            "address": export_user.address,
            "portfolio_url": export_user.portfolio_url,
            "personal_website": export_user.personal_website,
            "linkedin_profile": export_user.linkedin_profile,
            "github_profile": export_user.github_profile,
            "years_of_experience": export_user.years_of_experience,
            "skills": export_user.skills,
            "profile_visibility": export_user.profile_visibility,
            "show_email": export_user.show_email,
        },
        "education": [
            {"degree": e.degree, "university": e.university, "field_of_study": e.field_of_study, "start_date": e.start_date, "end_date": e.end_date, "description": e.description}
            for e in export_user.education
        ],
        "experience": [
            {"title": e.title, "company": e.company, "location": e.location, "start_date": e.start_date, "end_date": e.end_date, "description": e.description}
            for e in export_user.experience
        ],
        "projects": [
            {"name": p.name, "description": p.description, "technologies": p.technologies, "url": p.url}
            for p in export_user.projects
        ],
        "job_preferences": {
            "company_size": export_user.job_preferences.company_size if export_user.job_preferences else None,
            "industry": export_user.job_preferences.industry if export_user.job_preferences else None,
            "job_titles": export_user.job_preferences.job_titles if export_user.job_preferences else None,
            "locations": export_user.job_preferences.locations if export_user.job_preferences else None,
            "remote": export_user.job_preferences.remote if export_user.job_preferences else None,
        } if export_user.job_preferences else {},
        "skills": [
            {"name": s.name, "proficiency": s.proficiency}
            for s in export_user.skills
        ],
        "notifications": [
            {"message": n.message, "details": n.details, "is_read": n.is_read, "created_at": n.created_at}
            for n in db.query(InAppNotification).filter_by(user_id=export_user.id).all()
        ],
    }
    log_audit(db, user.id, "gdpr_export", "users", export_user.id, {})
    return data

@router.post("/gdpr/erase")
async def gdpr_erase(db: Session = Depends(get_db), user: User = Depends(get_current_user), target_user_id: int = None):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # Only allow erasure for self or admin
    if target_user_id and (user.id != target_user_id and not is_admin(user)):
        raise HTTPException(status_code=403, detail="Forbidden: Cannot erase another user's data.")
    erase_user = user
    if target_user_id and (user.id == target_user_id or is_admin(user)):
        erase_user = db.query(User).filter_by(id=target_user_id).first()
        if not erase_user:
            raise HTTPException(status_code=404, detail="User not found")
    user_id = erase_user.id
    db.query(InAppNotification).filter_by(user_id=user_id).delete()
    db.query(Skill).filter_by(user_id=user_id).delete()
    db.query(Project).filter_by(user_id=user_id).delete()
    db.query(Experience).filter_by(user_id=user_id).delete()
    db.query(Education).filter_by(user_id=user_id).delete()
    db.query(JobPreference).filter_by(user_id=user_id).delete()
    db.delete(erase_user)
    db.commit()
    log_audit(db, user.id, "gdpr_erase", "users", user_id, {})
    return {"message": "Account and all associated data deleted as per GDPR request."}
