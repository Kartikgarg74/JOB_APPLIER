from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import uuid
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from requests.exceptions import ConnectionError, Timeout
import os
from supabase import create_client, Client

# Initialize FastAPI app
app = FastAPI(
    title="Job Applier Service",
    description="Automates job applications using Selenium and AI-generated cover letters."
)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class UserProfile(BaseModel):
    id: Optional[str] = None
    data: Dict[str, Any]

async def save_user_profile(user_profile_data: Dict[str, Any]) -> str:
    response = supabase.table("user_profiles").insert({"data": user_profile_data}).execute()
    if response.data:
        return response.data[0]["id"]
    raise Exception("Failed to save user profile to Supabase")

async def get_user_profile(profile_id: str) -> Optional[Dict[str, Any]]:
    response = supabase.table("user_profiles").select("data").eq("id", profile_id).execute()
    if response.data:
        return response.data[0]["data"]
    return None



# Placeholder for data models
class JobApplicationRequest(BaseModel):
    job_url: str
    platform: str  # e.g., Indeed, LinkedIn, Glassdoor
    user_profile_data: Dict[str, Any] # User's resume data, contact info, etc.
    job_description: str

class ApplicationStatus(BaseModel):
    application_id: str
    status: str # e.g., 'pending', 'in_progress', 'completed', 'failed', 'captcha_detected'
    message: Optional[str] = None
    applied_date: datetime = datetime.now()
    platform: str
    job_url: str

# In-memory store for application statuses (replace with Supabase in production)
# application_statuses: Dict[str, ApplicationStatus] = {}

async def save_application_status(status_data: ApplicationStatus):
    response = supabase.table("application_statuses").insert(status_data.dict()).execute()
    if not response.data:
        raise Exception("Failed to save application status to Supabase")

async def get_application_status_from_db(application_id: str) -> Optional[ApplicationStatus]:
    response = supabase.table("application_statuses").select("*").eq("application_id", application_id).execute()
    if response.data:
        return ApplicationStatus(**response.data[0])
    return None

async def update_application_status_in_db(application_id: str, status: str, message: Optional[str] = None):
    update_data = {"status": status}
    if message is not None:
        update_data["message"] = message
    response = supabase.table("application_statuses").update(update_data).eq("application_id", application_id).execute()
    if not response.data:
        raise Exception("Failed to update application status in Supabase")


# Selenium WebDriver setup (ensure chromedriver is in PATH or specify path)
def get_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode for server environments
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Add more options for stealth/anti-detection if needed
    # service = Service('/usr/local/bin/chromedriver') # Specify path if not in PATH
    driver = webdriver.Chrome(options=options)
    return driver

# Function to generate personalized cover letter (placeholder)
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type((ConnectionError, Timeout)))
async def generate_cover_letter(job_description: str, user_profile: Dict[str, Any]) -> str:
    # TODO: Integrate with GPT/Gemini API to generate cover letter
    print(f"Generating cover letter for job description: {job_description[:50]}...")
    return f"Dear Hiring Manager, I am excited to apply for this role based on the description: {job_description}."

# Function to apply for a job (placeholder)
@retry(stop=stop_after_attempt(3), wait=wait_fixed(5), reraise=True)
async def apply_for_job(application_request: JobApplicationRequest, application_id: str, user_profile_id: str):
    try:
        user_profile = await get_user_profile(user_profile_id)
        if not user_profile:
            raise Exception(f"User profile with ID {user_profile_id} not found.")

        driver = get_webdriver()
        driver.get(application_request.job_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        # Simulate human-like delays
        time.sleep(random.uniform(2, 5))

        # TODO: Implement platform-specific application logic (Indeed, LinkedIn, Glassdoor)
        # This will involve finding elements, filling forms, clicking buttons
        print(f"Applying for job on {application_request.platform} at {application_request.job_url}")

        # Generate cover letter
        cover_letter = await generate_cover_letter(application_request.job_description, user_profile)
        print(f"Generated cover letter: {cover_letter[:50]}...")

        # TODO: Handle different application forms and required fields
        # TODO: CAPTCHA detection and manual intervention alerts

        # Update status in Supabase
        await update_application_status_in_db(application_id, 'completed', 'Application submitted successfully (simulated).')

    except Exception as e:
        await update_application_status_in_db(application_id, 'failed', str(e))
        print(f"Application failed: {e}")
    finally:
        if 'driver' in locals() and driver:
            driver.quit()

# API Endpoints
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Job Applier Service"}

@app.post("/apply")
async def submit_application(request: JobApplicationRequest, background_tasks: BackgroundTasks):
    application_id = str(uuid.uuid4()) # Generate unique ID
    user_profile_id = await save_user_profile(request.user_profile_data)

    initial_status = ApplicationStatus(
        application_id=application_id,
        status='pending',
        platform=request.platform,
        job_url=request.job_url
    )
    await save_application_status(initial_status)

    background_tasks.add_task(apply_for_job, request, application_id, user_profile_id)
    return {"message": "Application initiated", "application_id": application_id}

@app.get("/status/{application_id}", response_model=ApplicationStatus)
async def get_application_status(application_id: str):
    status = await get_application_status_from_db(application_id)
    if not status:
        raise HTTPException(status_code=404, detail="Application not found")
    return status

@app.get("/analytics")
async def get_application_analytics():
    # TODO: Implement application analytics and success rate tracking using Supabase
    # This will require querying Supabase for application statuses
    # For now, returning dummy data or adapting to query Supabase
    response = supabase.table("application_statuses").select("status").execute()
    all_statuses = [s["status"] for s in response.data]

    total_applications = len(all_statuses)
    completed_applications = all_statuses.count('completed')
    failed_applications = all_statuses.count('failed')
    success_rate = (completed_applications / total_applications * 100) if total_applications > 0 else 0

    return {
        "total_applications": total_applications,
        "completed_applications": completed_applications,
        "failed_applications": failed_applications,
        "success_rate": f"{success_rate:.2f}%"
    }