from fastapi import FastAPI, BackgroundTasks, HTTPException
from celery import Celery
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Initialize FastAPI app
app = FastAPI(
    title="Agent Orchestra Service",
    description="Coordinates job matching, recommendations, and application automation."
)

# Initialize Celery
celery_app = Celery(
    "agent_orchestra",
    broker="redis://localhost:6379/0",  # Assuming Redis is running locally
    backend="redis://localhost:6379/0"
)

# Placeholder for data models
class UserPreferences(BaseModel):
    location: Optional[str] = None
    role: Optional[str] = None
    domain: Optional[str] = None
    work_mode: Optional[str] = None

class JobPosting(BaseModel):
    job_id: str
    title: str
    description: str
    skills: List[str]
    location: str
    salary: Optional[str] = None
    source: str
    posted_date: datetime = datetime.now()

class MatchedJob(BaseModel):
    job_id: str
    score: float
    recommendation_reason: str

class JobProcessingMetrics(BaseModel):
    total_jobs_processed: int = 0
    new_jobs_scraped: int = 0
    duplicate_jobs_detected: int = 0
    jobs_matched: int = 0
    notifications_sent: int = 0
    old_jobs_cleaned: int = 0

# In-memory store for simplicity. Replace with Supabase/DB in production.
job_processing_metrics: JobProcessingMetrics = JobProcessingMetrics()

# Celery task for processing new jobs
@celery_app.task
def process_new_job_posting(job_data: Dict[str, Any]):
    global job_processing_metrics
    job_processing_metrics.new_jobs_scraped += 1

    job = JobPosting(**job_data)
    print(f"Processing new job: {job.title} from {job.source}")

    # TODO: Implement duplicate job detection
    # For now, assume no duplicates
    if False: # Placeholder for duplicate detection logic
        job_processing_metrics.duplicate_jobs_detected += 1
        print(f"Duplicate job detected: {job.job_id}")
        return {"status": "duplicate", "job_id": job.job_id}

    # TODO: Fetch all active users
    active_users = [{"user_id": "user123", "preferences": {"location": "New York", "role": "Software Engineer"}}]

    for user in active_users:
        user_id = user["user_id"]
        user_preferences = user["preferences"]

        # TODO: Calculate ATS scores for user against new job posting
        ats_score = 0.0 # Placeholder
        print(f"Calculated ATS score for {user_id} on {job.title}: {ats_score}")

        # TODO: Filter and rank jobs based on user preferences
        # For now, a simple score based on ATS
        match_score = ats_score # Placeholder

        if match_score > 80.0:
            # TODO: Store matching results in Supabase
            print(f"High match found for {user_id} and {job.title} with score {match_score}")
            job_processing_metrics.jobs_matched += 1
            # TODO: Send email/push notifications
            job_processing_metrics.notifications_sent += 1

    job_processing_metrics.total_jobs_processed += 1
    return {"status": "processed", "job_id": job.job_id, "metrics": job_processing_metrics.dict()}

# Celery task for daily job matching for active users
@celery_app.task
def perform_daily_job_matching():
    print("Performing daily job matching for active users...")
    # TODO: Fetch all active users
    active_users = [{"user_id": "user123", "preferences": {"location": "New York", "role": "Software Engineer"}}]
    for user in active_users:
        perform_job_matching.delay(user["user_id"], user["preferences"])
    return {"status": "daily_matching_initiated", "users_count": len(active_users)}

# Celery task for job expiry handling and cleanup
@celery_app.task
def cleanup_old_job_postings():
    global job_processing_metrics
    print("Cleaning up old job postings...")
    # TODO: Implement job expiry logic and cleanup
    # Example: Remove jobs older than 30 days
    threshold_date = datetime.now() - timedelta(days=30)
    cleaned_count = 0 # Placeholder
    # For job in all_jobs:
    #   if job.posted_date < threshold_date:
    #       delete job
    #       cleaned_count += 1
    job_processing_metrics.old_jobs_cleaned += cleaned_count
    return {"status": "cleanup_complete", "cleaned_count": cleaned_count}

# API Endpoints
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Agent Orchestra Service"}

@app.post("/jobs/new")
async def receive_new_job(job: JobPosting, background_tasks: BackgroundTasks):
    # Trigger processing of new job posting as a background task
    background_tasks.add_task(process_new_job_posting.delay, job.dict())
    return {"message": "New job received and processing initiated", "job_id": job.job_id}

@app.post("/match_jobs/{user_id}")
async def match_jobs(user_id: str, preferences: UserPreferences, background_tasks: BackgroundTasks):
    # Trigger job matching as a background task
    background_tasks.add_task(perform_job_matching.delay, user_id, preferences.dict())
    return {"message": "Job matching initiated", "user_id": user_id}

@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    # TODO: Implement personalized job recommendations using collaborative filtering
    # - Fetch matching results from Supabase
    # - Apply collaborative filtering
    return {"message": "Recommendations for user", "user_id": user_id, "recommendations": []}

@app.get("/job_trends")
async def get_job_trends():
    # TODO: Implement job trend analysis and salary insights
    return {"message": "Job trends and salary insights", "trends": [], "salary_insights": {}}

@app.get("/admin/metrics", response_model=JobProcessingMetrics)
async def get_admin_metrics():
    return job_processing_metrics

# Schedule daily job matching (example, in a real app use Celery Beat or similar)
# celery_app.conf.beat_schedule = {
#     'daily-job-matching': {
#         'task': 'src.main.perform_daily_job_matching',
#         'schedule': timedelta(days=1),
#     },
#     'cleanup-old-jobs': {
#         'task': 'src.main.cleanup_old_job_postings',
#         'schedule': timedelta(days=7), # Run weekly
#     }
# }
# celery_app.conf.timezone = 'UTC'