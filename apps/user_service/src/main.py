from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Gauge, Histogram
from fastapi import Response as FastAPIResponse
from contextlib import asynccontextmanager
import logging
import time
import json
from dotenv import load_dotenv

load_dotenv()

from packages.errors.custom_exceptions import JobApplierException
from packages.utilities.logging_utils import setup_logging

from .user_api import router as user_router
from .profile_api import router as profile_router

setup_logging()

# Prometheus metrics
user_signup_counter = Counter('user_signups_total', 'Total user signups')
user_login_counter = Counter('user_logins_total', 'Total user logins')
profile_update_counter = Counter('user_profile_updates_total', 'Total profile updates')
file_upload_counter = Counter('user_file_uploads_total', 'Total file uploads')
error_counter = Counter('user_errors_total', 'Total error responses')
uptime_gauge = Gauge('user_uptime_seconds', 'Application uptime in seconds')
startup_time = time.time()
request_count = Counter('user_requests_total', 'Total API requests', ['method', 'endpoint', 'status_code'])
request_latency = Histogram('user_request_latency_seconds', 'API request latency in seconds', ['method', 'endpoint'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    global startup_time
    startup_time = time.time()
    yield

app = FastAPI(
    title="User Service API",
    description="API for managing user authentication, profiles, and related data.",
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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
    - Business metrics (signups, logins, profile updates, file uploads)
    - Request metrics (latency, counts)
    """
    uptime_gauge.set(time.time() - startup_time)
    return FastAPIResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health_check():
    """Health check endpoint for the User Service."""
    return {"status": "ok", "message": "User Service is healthy"}

@app.get("/status")
async def get_status():
    """Get service status and metrics."""
    return {
        "status": "running",
        "uptime_seconds": time.time() - startup_time,
        "service": "User Service"
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
        content={"message": "Validation Error", "details": [err for err in exc.errors()]},
    )

@app.get("/")
async def read_root():
    return {"message": "Welcome to the User Service API"}

app.include_router(user_router)
app.include_router(profile_router)

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

# To run the application, use the command: uvicorn main:app --reload --host 0.0.0.0 --port 8001
