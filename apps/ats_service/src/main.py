from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Gauge, Histogram
from fastapi import Response as FastAPIResponse
from contextlib import asynccontextmanager
import logging
import time
import json

from packages.errors.custom_exceptions import JobApplierException
from packages.utilities.logging_utils import setup_logging

from .ats_api import router as ats_router
from .metrics import ats_score_counter, job_search_counter, error_counter, uptime_gauge, startup_time, request_count, request_latency

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global startup_time
    startup_time = time.time()
    yield

app = FastAPI(
    title="ATS Service API",
    description="API for ATS (Applicant Tracking System) related functionalities.",
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
    - Business metrics (ATS scores, job searches)
    - Request metrics (latency, counts)
    """
    uptime_gauge.set(time.time() - startup_time)
    return FastAPIResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health_check():
    """Health check endpoint for the ATS Service."""
    return {"status": "ok", "message": "ATS Service is healthy"}

@app.get("/status")
async def get_status():
    """Get service status and metrics."""
    return {
        "status": "running",
        "uptime_seconds": time.time() - startup_time,
        "service": "ATS Service"
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
    return {"message": "Welcome to the ATS Service API"}

app.include_router(ats_router)

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

# To run the application, use the command: uvicorn main:app --reload --host 0.0.0.0 --port 8003
