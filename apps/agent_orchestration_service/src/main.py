from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from packages.errors.custom_exceptions import JobApplierException
from packages.utilities.logging_utils import setup_logging

from src.agent_api import router as agent_router

setup_logging()

app = FastAPI(
    title="Agent Orchestration Service API",
    description="API for orchestrating various job application agents.",
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
    return {"message": "Welcome to the Agent Orchestration Service API"}

app.include_router(agent_router)

# To run the application, use the command: uvicorn main:app --reload --host 0.0.0.0 --port 8002