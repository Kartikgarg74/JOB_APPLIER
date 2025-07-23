from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from packages.errors.custom_exceptions import JobApplierException
from packages.utilities.logging_utils import setup_logging

from src.user_api import router as user_router
from src.profile_api import router as profile_router

setup_logging()

app = FastAPI(
    title="User Service API",
    description="API for managing user authentication, profiles, and related data.",
    version="1.0.0",
)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    logging.error(f"HTTP Exception: {exc.status_code} - {exc.detail}", exc_info=True)
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})

@app.exception_handler(JobApplierException)
async def job_applier_exception_handler(request, exc: JobApplierException):
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
    logging.error(f"Validation Error: {exc.errors()}", exc_info=True)
    return JSONResponse(
        status_code=422,
        content={"message": "Validation Error", "details": exc.errors()},
    )

@app.get("/")
async def read_root():
    return {"message": "Welcome to the User Service API"}

app.include_router(user_router)
app.include_router(profile_router)

# To run the application, use the command: uvicorn main:app --reload --host 0.0.0.0 --port 8001