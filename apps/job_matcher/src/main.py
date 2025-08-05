from fastapi import FastAPI, HTTPException, Response as FastAPIResponse
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict
import httpx
import os
from tenacity import retry, stop_after_attempt, wait_fixed
import time
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Gauge, Histogram
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware

ATS_SERVICE_URL = os.getenv("ATS_SERVICE_URL", "http://localhost:8003/process-application") # Default to localhost for development

# Prometheus Metrics
job_match_counter = Counter('job_matcher_matches_total', 'Total job matches performed')
job_match_score_gauge = Gauge('job_matcher_last_match_score', 'Last job match score')
ats_score_gauge = Gauge('job_matcher_last_ats_score', 'Last ATS score obtained')
error_counter = Counter('job_matcher_errors_total', 'Total errors in job matcher service')
uptime_gauge = Gauge('job_matcher_uptime_seconds', 'Application uptime in seconds')
startup_time = time.time()
request_count = Counter('job_matcher_requests_total', 'Total API requests', ['method', 'endpoint', 'status_code'])
request_latency = Histogram('job_matcher_request_latency_seconds', 'API request latency in seconds', ['method', 'endpoint'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    global startup_time
    startup_time = time.time()
    yield

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Job Matcher API",
    description="API for matching job descriptions to candidate profiles.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://job-applier-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def _make_api_call(url: str, method: str = "GET", json_data: dict = None):
    async with httpx.AsyncClient() as client:
        try:
            if method == "POST":
                response = await client.post(url, json=json_data)
            else:
                response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            error_counter.inc()
            print(f"Attempt failed: Network error: {exc.request.url} - {exc}")
            raise
        except httpx.HTTPStatusError as exc:
            error_counter.inc()
            print(f"Attempt failed: API error: {exc.response.status_code} - {exc.response.text}")
            raise

# Load a pre-trained SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

@app.get("/metrics")
def metrics():
    """
    Exposes Prometheus metrics for scraping.
    """
    uptime_gauge.set(time.time() - startup_time)
    return FastAPIResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post('/match-jobs')
async def match_jobs(job_descriptions: List[Dict], resume_content: str) -> List[Dict]:
    job_match_counter.inc()
    resume_embedding = model.encode(resume_content, convert_to_tensor=True)
    resume_keywords = set(word.lower() for word in resume_content.split() if len(word) > 2) # Simple keyword extraction

    results = []
    for job in job_descriptions:
        job_description = job.get("description", "")
        job_title = job.get("title", "")
        job_company = job.get("company", "")
        job_link = job.get("link", "")

        job_embedding = model.encode(job_description, convert_to_tensor=True)
        cosine_score = util.pytorch_cos_sim(job_embedding, resume_embedding).item()

        job_keywords = set(word.lower() for word in job_description.split() if len(word) > 2) # Simple keyword extraction

        matched_keywords = list(resume_keywords.intersection(job_keywords))
        missing_keywords = list(job_keywords.difference(resume_keywords))

        ats_score = 0.0
        cover_letter = ""
        application_status = "pending"
        error_handling = {"retry_attempts": 0, "fallback_used": False, "last_known_issue": None}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    ATS_SERVICE_URL,
                    json={
                        "resume_content": resume_content,
                        "job_description": job_description,
                        "user_preferences": {}
                    },
                    timeout=30.0
                )
                response.raise_for_status() # Raise an exception for 4xx or 5xx status codes
                ats_response = response.json()
                ats_score = ats_response.get("ats_score", 0.0)
                cover_letter = ats_response.get("cover_letter", "")
                application_status = ats_response.get("application_status", "processed")
                error_handling = ats_response.get("error_handling", error_handling)
                ats_score_gauge.set(ats_score)
        except httpx.RequestError as exc:
            error_counter.inc()
            application_status = "failed_gracefully"
            error_handling["last_known_issue"] = f"An error occurred while requesting {exc.request.url!r}."
            error_handling["fallback_used"] = True
            print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
        except httpx.HTTPStatusError as exc:
            error_counter.inc()
            application_status = "failed_gracefully"
            error_handling["last_known_issue"] = f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
            error_handling["fallback_used"] = True
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc}")
        except Exception as e:
            error_counter.inc()
            application_status = "failed_gracefully"
            error_handling["last_known_issue"] = f"An unexpected error occurred: {e}"
            error_handling["fallback_used"] = True
            print(f"An unexpected error occurred: {e}")

        results.append({
            "job_match_score": round(cosine_score * 100, 2),
            "ats_score": ats_score,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "cover_letter": cover_letter,
            "application_status": application_status,
            "error_handling": error_handling,
            "job_title": job_title,
            "job_company": job_company,
            "job_link": job_link
        })

    # Sort by job_match_score and return top 5
    return sorted(results, key=lambda x: x["job_match_score"], reverse=True)[:5]

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