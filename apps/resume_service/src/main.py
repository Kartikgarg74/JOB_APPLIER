from fastapi import FastAPI, File, UploadFile, HTTPException, Response as FastAPIResponse
from fastapi.responses import JSONResponse
import logging
import os
import time
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Gauge, Histogram
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from resume_parser import parse_resume

# Prometheus Metrics
resume_parse_counter = Counter('resume_parser_parses_total', 'Total resume parsing requests')
error_counter = Counter('resume_parser_errors_total', 'Total errors in resume parser service')
uptime_gauge = Gauge('resume_parser_uptime_seconds', 'Application uptime in seconds')
startup_time = time.time()
request_count = Counter('resume_parser_requests_total', 'Total API requests', ['method', 'endpoint', 'status_code'])
request_latency = Histogram('resume_parser_request_latency_seconds', 'API request latency in seconds', ['method', 'endpoint'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    global startup_time
    startup_time = time.time()
    yield

app = FastAPI(
    title="Resume Parser Service",
    description="Microservice for parsing resumes into structured JSON",
    lifespan=lifespan,
)

logger = logging.getLogger(__name__)

@app.get("/metrics")
def metrics():
    """
    Exposes Prometheus metrics for scraping.
    """
    uptime_gauge.set(time.time() - startup_time)
    return FastAPIResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/parse-resume", 
          summary="Parse resume file",
          description="Accepts PDF, DOCX or plain text resumes and returns structured data")
async def parse_resume_endpoint(file: UploadFile = File(...)):
    """
    Endpoint that accepts resume files and returns parsed structured data.
    
    Args:
        file: Uploaded resume file (PDF, DOCX or TXT)
        
    Returns:
        JSONResponse: Parsed resume data or error message
    """
    try:
        # Validate file type
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ['.pdf', '.docx', '.doc', '.txt']:
            raise HTTPException(status_code=400, detail="Unsupported file format")
            
        # Create temp file path
        temp_path = f"/tmp/{file.filename}"
        
        # Save uploaded file temporarily
        with open(temp_path, "wb") as f:
            f.write(await file.read())
            
        # Read file content
        file_content = file.file.read().decode("utf-8")
        
        # Parse the file
        result = parse_resume(file_content)
        
        # Clean up temp file
        os.remove(temp_path)
        
        if not result:
            raise HTTPException(status_code=422, detail="Failed to parse resume")
            
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}", exc_info=True)
        resume_parse_counter.inc()
        # Clean up temp file
        os.remove(temp_path)
        
        if not result:
            raise HTTPException(status_code=422, detail="Failed to parse resume")
            
        return JSONResponse(content=result)
        
    except HTTPException:
        error_counter.inc()
        raise
        
    except Exception as e:
        error_counter.inc()
        logger.error(f"Error processing resume: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)