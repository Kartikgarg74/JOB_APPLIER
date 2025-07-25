import os
import shutil
import logging
from typing import Dict, Any, List
import json
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, Depends, Body
from fastapi import HTTPException # Keep HTTPException for standard HTTP errors
from packages.errors.custom_exceptions import JobApplierException, NotificationError
from packages.notifications.notification_service import NotificationService
from packages.database.config import get_db
from pydantic import BaseModel, Field
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis
from fastapi_limiter.depends import RateLimiter

from packages.utilities.file_management.file_operations import FileManagement
from packages.agents.agent_manager import AgentManager

from packages.config.settings import settings

from packages.message_queue.tasks import (
    process_resume_upload_task,
    calculate_ats_score_task,
    run_unicorn_agent_task,
)
from auth.auth_api import router as auth_router

from sqlalchemy.orm import Session
from packages.agents.unicorn_agent.unicorn_agent import UnicornAgent
from packages.notifications.in_app_notifications.in_app_notification_manager import InAppNotificationManager
from packages.agents.ats_scorer.ats_scorer_agent import ATSScorerAgent
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError
from packages.agents.application_automation.application_automation_agent import ApplicationAutomationAgent
from packages.utilities.encryption_utils import fernet
from prometheus_client import Counter
from packages.agents.job_scraper.job_scraper_agent import JobScraperAgent
from packages.utilities.parsers.resume_parser import extract_text_from_resume
from fastapi.responses import JSONResponse

# Redis cache setup
REDIS_URL = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
redis_cache = Redis.from_url(REDIS_URL, decode_responses=True)

CACHE_TTL = 60  # seconds

def cache_key_builder(prefix: str, *args):
    return f"{prefix}:" + ":".join(str(a) for a in args)

async def get_or_set_cache(key: str, fetch_func, ttl: int = CACHE_TTL):
    cached = await redis_cache.get(key)
    if cached is not None:
        return json.loads(cached)
    value = await fetch_func()
    await redis_cache.set(key, json.dumps(value), ex=ttl)
    return value

logger = logging.getLogger(__name__)

app = FastAPI()

v1_router = FastAPI(prefix="/v1")

v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

app.include_router(v1_router)


@v1_router.on_event("startup")
async def startup():
    redis_instance = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, password=settings.REDIS_PASSWORD)
    await FastAPILimiter.init(redis_instance)


# Placeholder for the JobApplierAgent instance
# In a real application, you would initialize and manage the agent here.
# For now, we'll simulate its state.
job_applier_agent_status = {
    "workflow_running": False,
    "last_run": None,
    "next_run": None,
}

file_upload_counter = Counter('file_uploads_total', 'Total number of file uploads')
file_download_counter = Counter('file_downloads_total', 'Total number of file downloads')
job_apply_counter = Counter('job_applications_total', 'Total number of job applications')


# Dependency to get FileManagement instance
def get_file_manager():
    return FileManagement(base_output_dir=os.path.join(os.getcwd(), "output"))


from packages.database.config import SessionLocal

# Dependency to get ATSScorerAgent instance
def get_ats_scorer_agent(db: Session = Depends(lambda: SessionLocal())):
    agent_manager = AgentManager(db)
    return agent_manager.get_ats_scorer_agent()

# Dependency to get ApplicationAutomationAgent instance
def get_application_automation_agent(db: Session = Depends(lambda: SessionLocal())):
    agent_manager = AgentManager(db)
    return agent_manager.get_application_automation_agent()

# Dependency to get NotificationService instance
def get_notification_service():
    db_session = next(get_db())
    return NotificationService(db_session=db_session)

# Dependency to get UnicornAgent instance
def get_unicorn_agent(db: Session = Depends(lambda: SessionLocal())):
    return UnicornAgent(db)

# Dependency to get InAppNotificationManager instance
def get_in_app_notification_manager(db: Session = Depends(lambda: SessionLocal())):
    return InAppNotificationManager(db)


# Define request body models


class UploadResumeResponse(BaseModel):
    status: str = Field(..., example="success")
    message: str = Field(
        ...,
        example="Resume uploaded successfully and processing started for: my_resume.pdf",
    )
    path: str = Field(..., example="/app/output/resumes/my_resume.pdf")

class UnicornAgentRequest(BaseModel):
    user_profile: Dict[str, Any]
    job_posting: Dict[str, Any]


class UnicornAgentResponse(BaseModel):
    status: str = Field(..., example="processing")
    response_model=UnicornAgent,
    summary="Apply for Job using Unicorn Agent",
    description="Initiates the job application workflow using the Unicorn Agent.",
    dependencies=[Depends(RateLimiter(times=1, seconds=5))]
async def apply_job(
    request: UnicornAgentRequest,
    notification_service: NotificationService = Depends(get_notification_service),
):
    logger.info(f"Received request to apply for job with Unicorn Agent.")
    try:
        # Offload to Celery task
        task = run_unicorn_agent_task.delay(request.dict())

        # Send initial notification that processing has started
        await notification_service.send_notification(
            recipient=request.user_profile.get("email"),
            message="Your job application workflow has started processing.",
            notification_type="email",
            details={"subject": "Job Application Started", "task_id": task.id}
        )

        return {
            "status": "processing",
            "message": "Job application workflow has been queued for processing.",
            "task_id": task.id
        }
    except Exception as e:
        logger.error(f"Failed to queue job application: {e}", exc_info=True)
        await notification_service.send_notification(
            recipient=request.user_profile.get("email"),
            message=f"Failed to queue job application: {e}",
            notification_type="email",
            details={"subject": "Job Application Queue Failed", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


class InAppNotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    details: Dict[str, Any]
    is_read: bool
    created_at: str


@v1_router.post(
    "/apply-job",
    response_model=UnicornAgentResponse,
    summary="Apply for Job using Unicorn Agent",
    description="Initiates the job application workflow using the Unicorn Agent.",
    tags=["Jobs"],
    dependencies=[Depends(RateLimiter(times=1, seconds=5))],
    responses={
        200: {"description": "Job application queued successfully.", "content": {"application/json": {"example": {"status": "processing", "message": "Job application workflow has been queued for processing.", "task_id": "abc123"}}}},
        400: {"description": "Invalid input or business logic error.", "content": {"application/json": {"example": {"status": "error", "message": "Invalid job posting URL."}}}},
        500: {"description": "Internal server error.", "content": {"application/json": {"example": {"status": "error", "message": "Internal server error."}}}},
    },
)
async def apply_job(
    request: UnicornAgentRequest = Body(..., example={"user_profile": {"email": "user@example.com"}, "job_posting": {"url": "https://example.com/job/123"}}),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Queue a job application workflow using the Unicorn Agent."""
    logger.info(f"Received request to apply for job with Unicorn Agent.")
    try:
        # Offload to Celery task
        task = run_unicorn_agent_task.delay(request.dict())

        # Send initial notification that processing has started
        await notification_service.send_notification(
            recipient=request.user_profile.get("email"),
            message="Your job application workflow has started processing.",
            notification_type="email",
            details={"subject": "Job Application Started", "task_id": task.id}
        )

        job_apply_counter.inc()

        return {
            "status": "processing",
            "message": "Job application workflow has been queued for processing.",
            "task_id": task.id
        }
    except Exception as e:
        logger.error(f"Failed to queue job application: {e}", exc_info=True)
        await notification_service.send_notification(
            recipient=request.user_profile.get("email"),
            message=f"Failed to queue job application: {e}",
            notification_type="email",
            details={"subject": "Job Application Queue Failed", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


class InAppNotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    details: Dict[str, Any]
    is_read: bool
    created_at: str


@v1_router.post(
    "/apply-job",
    response_model=UnicornAgentResponse,
    summary="Apply for Job using Unicorn Agent",
    description="Initiates the job application workflow using the Unicorn Agent.",
    dependencies=[Depends(RateLimiter(times=1, seconds=5))]
)
async def apply_job(
    request: UnicornAgentRequest,
    notification_service: NotificationService = Depends(get_notification_service),
):
    logger.info(f"Received request to apply for job with Unicorn Agent.")
    try:
        # Offload to Celery task
        task = run_unicorn_agent_task.delay(request.dict())

        # Send initial notification that processing has started
        await notification_service.send_notification(
            recipient=request.user_profile.get("email"),
            message="Your job application workflow has started processing.",
            notification_type="email",
            details={"subject": "Job Application Started", "task_id": task.id}
        )

        return {
            "status": "processing",
            "message": "Job application workflow has been queued for processing.",
            "task_id": task.id
        }
    except Exception as e:
        logger.error(f"Failed to queue job application: {e}", exc_info=True)
        await notification_service.send_notification(
            recipient=request.user_profile.get("email"),
            message=f"Failed to queue job application: {e}",
            notification_type="email",
            details={"subject": "Job Application Queue Failed", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")





@v1_router.post(
    "/upload-resume",
    response_model=UploadResumeResponse,
    summary="Upload Resume",
    description="Uploads a resume file (PDF or DOCX) for processing and user profile update.",
    dependencies=[Depends(RateLimiter(times=1, seconds=5))]
)
async def upload_resume(
    file: UploadFile = File(
        ...,
        description="The resume file to upload (PDF or DOCX).",
        max_size=5 * 1024 * 1024,  # 5 MB limit
    ),
    file_manager: FileManagement = Depends(get_file_manager),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Upload a resume file (PDF or DOCX)."""
    file_upload_counter.inc()
    logger.info(f"Received request to upload resume: {file.filename}")
    allowed_extensions = ["pdf", "docx"]
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        logger.warning(f"Invalid file format for {file.filename}: {file_extension}")
        error_message = "Invalid file format. Only PDF and DOCX are allowed."
        await notification_service.send_notification(
            recipient="user@example.com",  # Replace with actual user email/ID
            message=f"Resume upload failed: {error_message}",
            notification_type="email",
            subject="Resume Upload Failed",
        )
        raise JobApplierException(
            message=error_message,
            status_code=400,
            details={"file_extension": file_extension, "allowed_extensions": allowed_extensions}
        )

    try:
        # Define a secure location to store resumes. Using settings.OUTPUT_DIR
        resume_dir = os.path.join(settings.OUTPUT_DIR, "resumes")
        os.makedirs(resume_dir, exist_ok=True)

        file_location = os.path.join(resume_dir, file.filename)
        logger.info(f"Saving encrypted resume to {file_location}")
        # Encrypt file before saving
        file_bytes = await file.read()
        encrypted_bytes = fernet.encrypt(file_bytes)
        with open(file_location, "wb") as buffer:
            buffer.write(encrypted_bytes)

        # Offload resume processing to a background task
        process_resume_upload_task.delay(
            file_location, file.content_type, settings.USER_PROFILE_PATH
        )
        logger.info(
            f"Resume upload received and processing offloaded for: {file.filename}"
        )
        await notification_service.send_notification(
            recipient="user@example.com",  # Replace with actual user email/ID
            message=f"Your resume '{file.filename}' has been uploaded successfully and is being processed.",
            notification_type="email",
            subject="Resume Upload Successful",
        )

        return {
            "status": "success",
            "message": f"Resume uploaded successfully and processing started for: {file.filename}",
            "path": file_location,
        }
    except JobApplierException as e:
        await notification_service.send_notification(
            recipient="user@example.com",  # Replace with actual user email/ID
            message=f"Resume upload failed: {e.message}",
            notification_type="email",
            subject="Resume Upload Failed",
        )
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Failed to upload resume: {e}", exc_info=True)
        await notification_service.send_notification(
            recipient="user@example.com",  # Replace with actual user email/ID
            message=f"Resume upload failed due to an internal server error: {e}",
            notification_type="email",
            subject="Resume Upload Failed",
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@v1_router.get(
    "/notifications/{user_id}",
    response_model=List[InAppNotificationResponse],
    summary="Get In-App Notifications",
    description="Retrieves a list of in-app notifications for a specific user.",
    dependencies=[Depends(RateLimiter(times=5, seconds=10))]
)
async def get_in_app_notifications(
    user_id: int,
    limit: int = 10,
    offset: int = 0,
    in_app_notification_manager: InAppNotificationManager = Depends(get_in_app_notification_manager),
):
    key = cache_key_builder("notifications", user_id, limit, offset)
    async def fetch():
        notifications = in_app_notification_manager.get_notifications_for_user(user_id, limit, offset)
        return [
            InAppNotificationResponse(
                id=n.id,
                user_id=n.user_id,
                message=n.message,
                details=n.details,
                is_read=n.is_read,
                created_at=n.created_at.isoformat()
            ).dict() for n in notifications
        ]
    result = await get_or_set_cache(key, fetch)
    response = JSONResponse(content=result)
    response.headers["Cache-Control"] = f"public, max-age={CACHE_TTL}"
    return response


@v1_router.post(
    "/notifications/{notification_id}/mark-read",
    summary="Mark In-App Notification as Read",
    description="Marks a specific in-app notification as read.",
    dependencies=[Depends(RateLimiter(times=5, seconds=10))]
)
async def mark_in_app_notification_read(
    notification_id: int,
    in_app_notification_manager: InAppNotificationManager = Depends(get_in_app_notification_manager),
):
    logger.info(f"Received request to mark in-app notification {notification_id} as read.")
    try:
        success = in_app_notification_manager.mark_as_read(notification_id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found.")
        return {"status": "success", "message": f"Notification {notification_id} marked as read."}
    except Exception as e:
        logger.error(f"Failed to mark in-app notification {notification_id} as read: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@v1_router.delete(
    "/notifications/{notification_id}",
    summary="Delete In-App Notification",
    description="Deletes a specific in-app notification.",
    dependencies=[Depends(RateLimiter(times=5, seconds=10))]
)
async def delete_in_app_notification(
    notification_id: int,
    in_app_notification_manager: InAppNotificationManager = Depends(get_in_app_notification_manager),
):
    logger.info(f"Received request to delete in-app notification {notification_id}.")
    try:
        success = in_app_notification_manager.delete_notification(notification_id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found.")
        return {"status": "success", "message": f"Notification {notification_id} deleted."}
    except Exception as e:
        logger.error(f"Failed to delete in-app notification {notification_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
        await notification_service.send_notification(
            recipient="user@example.com",
            message=f"Resume upload failed: {e.message}",
            notification_type="email",
            subject="Resume Upload Failed",
        )
        raise e
    except IOError as e:
        logger.error(
            f"File operation error during resume upload for {File.filename}: {e}",
            exc_info=True,
        )
        error_message = f"File operation error: {e}"
        await NotificationService.send_notification(
            recipient="user@example.com",
            message=f"Resume upload failed: {error_message}",
            notification_type="email",
            subject="Resume Upload Failed",
        )
        raise JobApplierException(
            message=error_message,
            status_code=500,
            details={"filename": File.filename, "error": str(e)}
        )
    except NotificationError as e:
        logger.error(
            f"Notification error during resume upload for {File.filename}: {e}",
            exc_info=True,
        )
        # Do not re-raise NotificationError as it's a secondary concern to the main operation
        raise JobApplierException(
            message="Resume uploaded, but notification failed.",
            status_code=200, # Still a success from the user's perspective for the upload
            details={"filename": File.filename, "notification_error": str(e)}
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during resume upload for {File.filename}: {e}",
            exc_info=True,
        )
        error_message = f"An unexpected error occurred: {e}"
        await NotificationService.send_notification(
            recipient="user@example.com",
            message=f"Resume upload failed: {error_message}",
            notification_type="email",
            subject="Resume Upload Failed",
        )
        raise JobApplierException(
            message=error_message,
            status_code=500,
            details={"filename": File.filename, "error": str(e)}
        )


class ATSScoreResponse(BaseModel):
    status: str = Field(..., example="success")
    message: str = Field(..., example="ATS score calculation started in background.")
    task_id: str = Field(..., example="<celery_task_id>")


class StatusResponse(BaseModel):
    status: str = Field(..., example="success")
    data: Dict[str, Any]


class WorkflowControlResponse(BaseModel):
    status: str = Field(..., example="success")
    message: str = Field(..., example="Workflow paused.")


class ConfigUpdate(BaseModel):
    config_key: str = Field(..., example="LOG_LEVEL", min_length=1)
    config_value: Any = Field(..., example="DEBUG")


class ConfigResponse(BaseModel):
    status: str = Field(..., example="success")
    data: Dict[str, Any]


class HealthCheckResponse(BaseModel):
    status: str = Field(..., example="ok")
    message: str = Field(..., example="Job Applier Agent is healthy")


@v1_router.get(
    "/status",
    response_model=StatusResponse,
    summary="Get Workflow Status",
    description="Retrieves the current operational status of the Job Applier Agent workflow, including its running state and last/next run times.",
)
async def get_status() -> StatusResponse:
    async def fetch():
        return StatusResponse(status="success", data=job_applier_agent_status).dict()
    key = cache_key_builder("status")
    result = await get_or_set_cache(key, fetch)
    response = JSONResponse(content=result)
    response.headers["Cache-Control"] = f"public, max-age={CACHE_TTL}"
    return response


@v1_router.post(
    "/workflow/pause",
    response_model=WorkflowControlResponse,
    summary="Pause Workflow",
    description="Pauses the ongoing Job Applier Agent workflow.",
    dependencies=[Depends(RateLimiter(times=5, seconds=10))]
)
async def pause_workflow() -> WorkflowControlResponse:
    job_applier_agent_status["workflow_running"] = False
    return WorkflowControlResponse(status="success", message="Workflow paused.")


@v1_router.post(
    "/workflow/resume",
    response_model=WorkflowControlResponse,
    summary="Resume Workflow",
    description="Resumes a paused Job Applier Agent workflow.",
    dependencies=[Depends(RateLimiter(times=5, seconds=10))]
)
async def resume_workflow() -> WorkflowControlResponse:
    job_applier_agent_status["workflow_running"] = True
    return WorkflowControlResponse(status="success", message="Workflow resumed.")


@v1_router.post(
    "/workflow/stop",
    response_model=WorkflowControlResponse,
    summary="Stop Workflow",
    description="Stops the Job Applier Agent workflow entirely.",
    dependencies=[Depends(RateLimiter(times=5, seconds=10))]
)
async def stop_workflow() -> WorkflowControlResponse:
    job_applier_agent_status["workflow_running"] = False
    # Additional logic to truly stop the workflow would go here
    return WorkflowControlResponse(status="success", message="Workflow stopped.")


@v1_router.put(
    "/config",
    response_model=ConfigResponse,
    summary="Update Configuration",
    description="Updates a specific configuration setting for the Job Applier Agent.",
    dependencies=[Depends(RateLimiter(times=5, seconds=10))]
)
async def update_config(update: ConfigUpdate) -> ConfigResponse:
    """Update a specific configuration setting."""
    # This is a simplified example. Real config management would be more robust.
    print(f"Config '{update.config_key}' updated to '{update.config_value}'")
    return ConfigResponse(status="success", data={"config_key": update.config_key, "config_value": update.config_value, "message": f"Config '{update.config_key}' updated." })


@v1_router.get(
    "/config",
    response_model=ConfigResponse,
    summary="Get Configuration",
    description="Retrieves the current configuration settings of the Job Applier Agent.",
)
async def get_config() -> ConfigResponse:
    async def fetch():
        return ConfigResponse(status="success", data={"example_setting": "example_value"}).dict()
    key = cache_key_builder("config")
    result = await get_or_set_cache(key, fetch)
    response = JSONResponse(content=result)
    response.headers["Cache-Control"] = f"public, max-age={CACHE_TTL}"
    return response


@v1_router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health Check",
    description="Performs a health check to ensure the Job Applier Agent is running and responsive.",
)
async def health_check() -> HealthCheckResponse:
    async def fetch():
        return HealthCheckResponse(status="ok", message="Job Applier Agent is healthy").dict()
    key = cache_key_builder("health")
    result = await get_or_set_cache(key, fetch)
    response = JSONResponse(content=result)
    response.headers["Cache-Control"] = f"public, max-age={CACHE_TTL}"
    return response


@v1_router.post(
    "/ats-score",
    response_model=ATSScoreResponse,
    summary="Calculate ATS Score",
    description="Calculates an ATS (Applicant Tracking System) compatibility score for a given resume against a job description.",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))]
)
async def get_ats_score(
    resume_file: UploadFile = File(
        ..., description="The resume file (PDF or DOCX) to score."
    ),
    job_description: str = Form(
        ..., description="The job description text to compare against the resume."
    ),
    ats_scorer_agent: ATSScorerAgent = Depends(get_ats_scorer_agent),
    notification_service: NotificationService = Depends(get_notification_service),
) -> ATSScoreResponse:

    logger.info(f"Received request for ATS score for resume: {resume_file.filename}")
    if resume_file.content_type not in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]:
        logger.warning(
            f"Invalid file type for ATS score: {resume_file.filename} ({resume_file.content_type})"
        )
        error_message = "Invalid file type. Only PDF and DOCX are supported."
        await notification_service.send_notification(
            recipient="user@example.com",  # Replace with actual user email/ID
            message=f"ATS score calculation failed: {error_message}",
            notification_type="email",
            details={
                "subject": "ATS Score Calculation Failed",
                "error_message": error_message
            },
        )
        raise JobApplierException(
            message=error_message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"file_type": resume_file.content_type, "allowed_types": ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]}
        )

    temp_resume_path = None  # Initialize to None
    try:
        # Save the uploaded resume temporarily to process it
        temp_dir = os.path.join(settings.OUTPUT_DIR, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        if resume_file.filename is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume filename is missing."
            )
        temp_resume_path = os.path.join(temp_dir, resume_file.filename)
        logger.info(f"Saving temporary resume for ATS scoring to {temp_resume_path}")
        with open(temp_resume_path, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)

        # Offload ATS scoring to a background task
        task = calculate_ats_score_task.delay(
            temp_resume_path, resume_file.content_type, job_description
        )
        logger.info(
            f"ATS score calculation started in background for {resume_file.filename} with task ID: {task.id}"
        )

        await notification_service.send_notification(
            recipient="user@example.com",  # Replace with actual user email/ID
            message=f"ATS score calculation for '{resume_file.filename}' started successfully. Task ID: {task.id}",
            notification_type="email",
            details={
                "subject": "ATS Score Calculation Started",
                "task_id": task.id
            },
        )

        # Return a response indicating that the task has been accepted
        return ATSScoreResponse(
            status="success",
            message="ATS score calculation started in background.",
            task_id=str(task.id),
        )
    except SQLAlchemyError as e:
        logger.error(
            f"Database error during ATS scoring for {resume_file.filename}: {e}",
            exc_info=True,
        )
        error_message = "Failed to calculate ATS score due to a database error."
        await notification_service.send_notification(
            recipient="user@example.com",
            message=f"ATS score calculation failed: {error_message}",
            notification_type="email",
            details={
                "subject": "ATS Score Calculation Failed",
                "error_message": error_message
            },
        )
        raise JobApplierException(
            message=error_message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
    except NotificationError as e:
        logger.error(
            f"Notification error during ATS scoring for {resume_file.filename}: {e}",
            exc_info=True,
        )
        # Do not re-raise NotificationError as it's a secondary concern to the main operation
        raise JobApplierException(
            message="ATS score calculation started, but notification failed.",
            status_code=200, # Still a success from the user's perspective
            details={"filename": resume_file.filename, "notification_error": str(e)}
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during ATS scoring for {resume_file.filename}: {e}",
            exc_info=True,
        )
        error_message = "An unexpected error occurred during ATS scoring."
        await notification_service.send_notification(
            recipient="user@example.com",
            message=f"ATS score calculation failed: {error_message}",
            notification_type="email",
            details={
                "subject": "ATS Score Calculation Failed",
                "error_message": error_message
            },
        )
        raise JobApplierException(
            message=error_message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )
    finally:
        # The temporary file cleanup is handled by the Celery task now
        pass


@v1_router.post(
    "/apply-for-job",
    summary="Apply for Job",
    description="Initiates the job application process using the Application Automation Agent.",
    dependencies=[Depends(RateLimiter(times=1, seconds=30))]
)
async def apply_for_job(
    job_posting_url: str = Form(..., description="The URL of the job posting."),
    application_automation_agent: ApplicationAutomationAgent = Depends(get_application_automation_agent),
    notification_service: NotificationService = Depends(get_notification_service),
) -> StatusResponse:

    logger.info(f"Received request to apply for job at: {job_posting_url}")
    try:
        application_automation_agent.apply_to_job(job_posting_url)
        await notification_service.send_notification(
            recipient="user@example.com",
            message=f"Application process initiated successfully for: {job_posting_url}",
            notification_type="email",
            details={
                "subject": "Job Application Initiated",
                "job_posting_url": job_posting_url
            },
        )
        return StatusResponse(
            status="success",
            data={"message": f"Application process initiated for: {job_posting_url}"}
        )
    except JobApplierException as e:
        await notification_service.send_notification(
            recipient="user@example.com",
            message=f"Job application failed: {e.message}",
            notification_type="email",
            details={
                "subject": "Job Application Failed",
                "error_message": e.message
            },
        )
        raise e
    except NotificationError as e:
        logger.error(
            f"Notification error during job application for {job_posting_url}: {e}",
            exc_info=True,
        )
        raise JobApplierException(
            message="Job application initiated, but notification failed.",
            status_code=200,
            details={"job_posting_url": job_posting_url, "notification_error": str(e)},
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during job application for {job_posting_url}: {e}",
            exc_info=True,
        )
        error_message = f"An unexpected error occurred: {e}"
        await notification_service.send_notification(
            recipient="user@example.com",
            message=f"Job application failed: {error_message}",
            notification_type="email",
            details={
                "subject": "Job Application Failed",
                "error_message": error_message
            },
        )
        raise JobApplierException(
            message=error_message,
            status_code=500,
            details={"job_posting_url": job_posting_url, "error": str(e)},
        )


class JobSearchRequest(BaseModel):
    query: str
    location: str = ""
    num_results: int = 10

class JobListing(BaseModel):
    title: str = None
    company: str = None
    location: str = None
    summary: str = None
    url: str = None

class JobSearchResponse(BaseModel):
    jobs: list[JobListing]

@v1_router.post(
    "/job-search",
    response_model=JobSearchResponse,
    summary="Search jobs from multiple job boards",
    description="Aggregates job listings from Indeed, LinkedIn, Google Jobs, and Glassdoor.",
    tags=["Jobs"],
    dependencies=[Depends(RateLimiter(times=3, seconds=10))],
    responses={
        200: {"description": "Job search results (cached for 60s)", "content": {"application/json": {"example": {"jobs": [{"title": "Software Engineer", "company": "Acme Corp", "location": "Remote", "summary": "Work on cool stuff", "url": "https://example.com/job/1"}]}}}},
    },
)
async def job_search(request: JobSearchRequest):
    agent = JobScraperAgent()
    jobs = []
    # Aggregate from all sources
    jobs += agent.search_indeed(request.query, request.location, request.num_results)
    jobs += agent.search_linkedin(request.query, request.location, request.num_results)
    jobs += agent.search_google_jobs(request.query, request.location, request.num_results)
    if hasattr(agent, 'search_glassdoor'):
        jobs += agent.search_glassdoor(request.query, request.location, request.num_results)
    # Remove duplicates by URL
    seen = set()
    unique_jobs = []
    for job in jobs:
        url = job.get('url')
        if url and url not in seen:
            seen.add(url)
            unique_jobs.append(job)
    response = JSONResponse(content=JobSearchResponse(jobs=[JobListing(**job) for job in unique_jobs]).dict())
    response.headers["Cache-Control"] = "public, max-age=60"
    return response


class AnalyticsEventRequest(BaseModel):
    event_name: str
    user_id: int = None
    properties: dict = {}

class AnalyticsEventResponse(BaseModel):
    status: str
    message: str

@v1_router.post(
    "/analytics/event",
    response_model=AnalyticsEventResponse,
    summary="Track a custom analytics event",
    description="Receives a custom analytics event from frontend or other clients. Logs to file for analysis.",
    dependencies=[Depends(RateLimiter(times=10, seconds=10))]
)
async def track_analytics_event(event: AnalyticsEventRequest):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_name": event.event_name,
        "user_id": event.user_id,
        "properties": event.properties,
    }
    with open("output/analytics_events.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    return AnalyticsEventResponse(status="success", message="Event logged.")


class CalendarConnectRequest(BaseModel):
    provider: str  # 'google' or 'outlook'
    user_id: int

class CalendarConnectResponse(BaseModel):
    status: str
    message: str

@v1_router.post(
    "/calendar/connect",
    response_model=CalendarConnectResponse,
    summary="Connect calendar (Google/Outlook) - stub",
    description="Stub endpoint for future calendar OAuth integration. Accepts provider and user_id.",
    dependencies=[Depends(RateLimiter(times=5, seconds=10))]
)
async def connect_calendar(request: CalendarConnectRequest):
    # In the future, redirect to OAuth flow and store tokens
    return CalendarConnectResponse(
        status="pending",
        message=f"Calendar integration for {request.provider} coming soon. OAuth flow will be implemented here."
    )


class DocumentProcessResponse(BaseModel):
    status: str
    text: str = None
    metadata: dict = {}
    message: str = None

@v1_router.post(
    "/document/process",
    response_model=DocumentProcessResponse,
    summary="Process a document (resume, PDF, image)",
    description="Extracts text and metadata from uploaded documents. Supports PDF, DOCX, and images (placeholder).",
    dependencies=[Depends(RateLimiter(times=3, seconds=10))]
)
async def process_document(file: UploadFile = File(...), type: str = Form("resume")):
    try:
        if type in ["resume", "pdf", "docx"]:
            # Save file temporarily
            temp_path = f"/tmp/{file.filename}"
            with open(temp_path, "wb") as f_out:
                f_out.write(await file.read())
            text = extract_text_from_resume(temp_path)
            os.remove(temp_path)
            return DocumentProcessResponse(status="success", text=text, metadata={"filename": file.filename, "type": type})
        elif type == "image":
            # Placeholder for OCR
            return DocumentProcessResponse(status="pending", text=None, metadata={"filename": file.filename, "type": type}, message="Image OCR coming soon.")
        else:
            return DocumentProcessResponse(status="error", message="Unsupported document type.")
    except Exception as e:
        return DocumentProcessResponse(status="error", message=str(e))


class LocationAutocompleteRequest(BaseModel):
    query: str

class LocationAutocompleteResponse(BaseModel):
    suggestions: list[str]

@v1_router.post(
    "/location/autocomplete",
    response_model=LocationAutocompleteResponse,
    summary="Address autocomplete (stub)",
    description="Returns placeholder address suggestions for a query. Integrate with Google/Mapbox later.",
    dependencies=[Depends(RateLimiter(times=10, seconds=10))]
)
async def location_autocomplete(request: LocationAutocompleteRequest):
    # Placeholder suggestions
    suggestions = [
        f"{request.query} Street, City, Country",
        f"{request.query} Avenue, City, Country",
        f"{request.query} Road, City, Country"
    ]
    return LocationAutocompleteResponse(suggestions=suggestions)
