from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Gauge, Histogram
from fastapi import APIRouter
from fastapi import Response as FastAPIResponse
from contextlib import asynccontextmanager
import logging
import time
import json

from packages.errors.custom_exceptions import JobApplierException
from pydantic import BaseModel
from packages.utilities.logging_utils import setup_logging

from .agent_api import router as agent_router

setup_logging()

# Prometheus metrics
agent_execution_counter = Counter('agent_orchestration_executions_total', 'Total agent executions')
job_application_counter = Counter('agent_orchestration_job_applications_total', 'Total job applications')
workflow_counter = Counter('agent_orchestration_workflows_total', 'Total workflows executed')
error_counter = Counter('agent_orchestration_errors_total', 'Total error responses')
uptime_gauge = Gauge('agent_orchestration_uptime_seconds', 'Application uptime in seconds')
startup_time = time.time()
request_count = Counter('agent_orchestration_requests_total', 'Total API requests', ['method', 'endpoint', 'status_code'])
request_latency = Histogram('agent_orchestration_request_latency_seconds', 'API request latency in seconds', ['method', 'endpoint'])

# In-memory store for workflow status
workflow_status = {
    "is_running": True,
    "last_state_change": time.time()
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global startup_time
    startup_time = time.time()
    yield

app = FastAPI(
    title="Agent Orchestration Service API",
    description="API for orchestrating various job application agents.",
    version="1.0.0",
    lifespan=lifespan,
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

app.add_middleware(SecurityHeadersMiddleware)

class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logging.info(json.dumps({
            "event": "request",
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time_ms": int(process_time * 1000)
        }))
        return response

app.add_middleware(PerformanceLoggingMiddleware)

@app.get("/metrics")
def metrics():
    """
    Exposes Prometheus metrics for scraping.
    Includes:
    - System metrics (uptime, errors)
    - Business metrics (agent executions, job applications, workflows)
    - Request metrics (latency, counts)
    """
    uptime_gauge.set(time.time() - startup_time)
    return FastAPIResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health_check():
    """Health check endpoint for the Agent Orchestration Service."""
    return {"status": "ok", "message": "Agent Orchestration Service is healthy"}

@app.get("/status")
async def get_status():
    """Get service status and metrics."""
    return {
        "status": "running",
        "uptime_seconds": time.time() - startup_time,
        "service": "Agent Orchestration Service"
    }

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code >= 500:
        error_counter.inc()
    logging.error(f"HTTP Exception: {exc.status_code} - {exc.detail}", exc_info=True)
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})

@app.exception_handler(JobApplierException)
async def job_applier_exception_handler(request, exc: JobApplierException):
    if exc.status_code >= 500:
        error_counter.inc()
    logging.error(f"Job Applier Exception: {exc.status_code} - {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "details": exc.details
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    error_counter.inc()
    logging.error(f"Validation Error: {exc.errors()}", exc_info=True)
    return JSONResponse(
        status_code=422,
        content={"message": "Validation Error", "details": exc.errors()},
    )

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Agent Orchestration Service API"}

app.include_router(agent_router)

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        method = request.method
        endpoint = request.url.path
        start_time = time.time()
        response = await call_next(request)
        latency = time.time() - start_time
        status_code = response.status_code
        request_count.labels(method, endpoint, status_code).inc()
        request_latency.labels(method, endpoint).observe(latency)
        return response

app.add_middleware(PrometheusMiddleware)

# --- Workflow Management CRUD ---

class WorkflowStatusResponse(BaseModel):
    is_running: bool
    last_state_change: float

class WorkflowStatusUpdate(BaseModel):
    is_running: bool

workflow_router = APIRouter(prefix="/workflow", tags=["Workflow Management"])

@workflow_router.get("/status", response_model=WorkflowStatusResponse, summary="Read workflow status")
async def get_workflow_status():
    """Get the current status of the main workflow."""
    return workflow_status

@workflow_router.put("/status", response_model=WorkflowStatusResponse, summary="Update workflow status")
async def update_workflow_status(update: WorkflowStatusUpdate):
    """Update the status of the main workflow (e.g., pause or resume)."""
    workflow_status["is_running"] = update.is_running
    workflow_status["last_state_change"] = time.time()
    return workflow_status

app.include_router(workflow_router)

# --- Application Management --- #

class ApplicationSubmissionRequest(BaseModel):
    job_id: str
    user_id: str
    resume_id: str
    cover_letter_content: str = None
    application_url: str
    additional_data: dict = {}

class ApplicationSubmissionResponse(BaseModel):
    status: str
    message: str
    application_id: str = None
    details: dict = {}

application_router = APIRouter(prefix="/applications", tags=["Application Management"])

@application_router.post("/submit", response_model=ApplicationSubmissionResponse, summary="Submit a job application")
async def submit_application(request: ApplicationSubmissionRequest):
    """Endpoint to submit a job application."""
    logging.info(f"Received application submission request for job_id: {request.job_id}")
    job_application_counter.inc()
    # Here, you would integrate with the actual application submission logic.
    # This might involve calling other services (e.g., a service to fill out forms, or an agent to interact with a website).
    # For now, we'll return a mock success response.
    try:
        # Simulate application processing
        # In a real scenario, this would involve complex logic, potentially asynchronous tasks
        # and interaction with external job boards.
        application_id = f"app_{int(time.time())}" # Generate a simple unique ID
        logging.info(f"Application {application_id} submitted successfully for job {request.job_id}")
        return ApplicationSubmissionResponse(
            status="success",
            message="Application submitted successfully.",
            application_id=application_id,
            details={
                "job_id": request.job_id,
                "user_id": request.user_id
            }
        )
    except Exception as e:
        error_counter.inc()
        logging.error(f"Error submitting application for job_id {request.job_id}: {e}", exc_info=True)
        raise JobApplierException(
            status_code=500,
            message="Failed to submit application",
            details={"error": str(e), "job_id": request.job_id}
        )

app.include_router(application_router)

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        method = request.method
        endpoint = request.url.path
        start_time = time.time()
        response = await call_next(request)
        latency = time.time() - start_time
        status_code = response.status_code
        request_count.labels(method, endpoint, status_code).inc()
        request_latency.labels(method, endpoint).observe(latency)
        return response

app.add_middleware(PrometheusMiddleware)

# To run the application, use the command: uvicorn main:app --reload --host 0.0.0.0 --port 8002
