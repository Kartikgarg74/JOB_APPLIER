# apps/job-applier-agent/src/main.py

from dotenv import load_dotenv
load_dotenv()


import logging
import time
import json

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from packages.errors.custom_exceptions import JobApplierException
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Gauge, Histogram
from fastapi import Response as FastAPIResponse
from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from packages.config.settings import settings

from packages.utilities.logging_utils import setup_logging
from apps.job_applier_agent.src.metrics import (
    signup_counter, login_counter, job_apply_counter, profile_update_counter,
    uptime_gauge, error_counter, request_count, request_latency
)

# Import the API router from the local api.py file
from fastapi import APIRouter
from .api import (auth_router, applications_router, resumes_router, profile_router, notifications_router)


setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global startup_time
    startup_time = time.time()
    redis_kwargs = {
        "url": settings.REDIS_URL,
        "encoding": "utf-8",
        "decode_responses": True,
    }
    if settings.REDIS_TOKEN:
        redis_kwargs["password"] = settings.REDIS_TOKEN
    # Assuming Upstash Redis always requires SSL, even with redis:// scheme
    if "upstash.io" in settings.REDIS_URL:
        redis_kwargs["ssl"] = True
    redis_instance = redis.from_url(**redis_kwargs)
    await FastAPILimiter.init(redis_instance)
    yield

app = FastAPI(
    title="Job Applier Agent API",
    description="API for the Job Applier Agent, managing user profiles, job applications, and agent interactions.",
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


# Prometheus metrics


@app.get("/metrics")
def metrics():
    """
    Exposes Prometheus metrics for scraping.
    Includes:
    - System metrics (uptime, errors)
    - Business metrics (signups, logins, job applications, profile updates)
    - File upload/download metrics
    - User activity metrics (DAU, WAU, MAU)
    See Grafana for dashboards and alerting setup.
    """
    uptime_gauge.set(time.time() - startup_time)
    return FastAPIResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


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
    return {"message": "Welcome to the Job Applier API"}


v1_router = APIRouter(prefix="/v1")
v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
v1_router.include_router(applications_router)
v1_router.include_router(resumes_router)
v1_router.include_router(profile_router)
v1_router.include_router(notifications_router)
app.include_router(v1_router)


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


# To run the application, use the command: uvicorn main:app --reload --host 0.0.0.0 --port 8000
