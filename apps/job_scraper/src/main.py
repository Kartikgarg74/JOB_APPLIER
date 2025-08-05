from fastapi import FastAPI, HTTPException, Response as FastAPIResponse
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import time
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Gauge, Histogram
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware

# Prometheus Metrics
job_scrape_counter = Counter('job_scraper_scrapes_total', 'Total job scrape requests')
error_counter = Counter('job_scraper_errors_total', 'Total errors in job scraper service')
uptime_gauge = Gauge('job_scraper_uptime_seconds', 'Application uptime in seconds')
startup_time = time.time()
request_count = Counter('job_scraper_requests_total', 'Total API requests', ['method', 'endpoint', 'status_code'])
request_latency = Histogram('job_scraper_request_latency_seconds', 'API request latency in seconds', ['method', 'endpoint'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    global startup_time
    startup_time = time.time()
    yield

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Job Scraper Service",
    description="Microservice for scraping job postings from various platforms.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://job-applier-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/metrics")
def metrics():
    """
    Exposes Prometheus metrics for scraping.
    """
    uptime_gauge.set(time.time() - startup_time)
    return FastAPIResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(requests.exceptions.RequestException))
def scrape_indeed(search_term: str = "software engineer", location: str = "remote") -> List[Dict]:
    jobs = []
    base_url = "https://www.indeed.com/jobs?q={}&l={}"

    url = base_url.format(search_term, location)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')

    job_cards = soup.find_all('div', class_='job_seen_beacon')

    for card in job_cards:
        title_element = card.find('h2', class_='jobTitle')
        title = title_element.text.strip() if title_element else 'N/A'

        company_element = card.find('span', class_='companyName')
        company = company_element.text.strip() if company_element else 'N/A'

        location_element = card.find('div', class_='companyLocation')
        location = location_element.text.strip() if location_element else 'N/A'

        link_element = card.find('a', class_='jcs-JobTitle')
        link = "https://www.indeed.com" + link_element['href'] if link_element else 'N/A'

        description = 'N/A'
        skills = []

        if link_element:
            job_page_url = link
            @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(requests.exceptions.RequestException))
            def get_job_page():
                return requests.get(job_page_url, headers=headers)
            job_page_response = get_job_page()
            job_page_soup = BeautifulSoup(job_page_response.content, 'lxml')

            description_element = job_page_soup.find('div', class_='jobsearch-JobComponent-description')
            if description_element:
                description = description_element.text.strip()

            # Simple skill extraction (can be improved with NLP later)
            skills_text = description.lower()
            possible_skills = ["python", "java", "c++", "javascript", "react", "angular", "node.js", "aws", "azure", "gcp", "docker", "kubernetes", "sql", "nosql", "machine learning", "deep learning", "nlp", "fastapi", "django", "flask", "spring", "agile", "scrum"]
            skills = [skill for skill in possible_skills if skill in skills_text]

        jobs.append({
            "title": title,
            "company": company,
            "description": description,
            "skills": skills,
            "location": location,
            "link": link
        })
    job_scrape_counter.inc()
    try:
        url = base_url.format(search_term, location)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        job_cards = soup.find_all('div', class_='job_seen_beacon')

        for card in job_cards:
            title_element = card.find('h2', class_='jobTitle')
            title = title_element.text.strip() if title_element else 'N/A'

            company_element = card.find('span', class_='companyName')
            company = company_element.text.strip() if company_element else 'N/A'

            location_element = card.find('div', class_='companyLocation')
            location = location_element.text.strip() if location_element else 'N/A'

            link_element = card.find('a', class_='jcs-JobTitle')
            link = "https://www.indeed.com" + link_element['href'] if link_element else 'N/A'

            description = 'N/A'
            skills = []

            if link_element:
                job_page_url = link
                @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(requests.exceptions.RequestException))
                def get_job_page():
                    return requests.get(job_page_url, headers=headers)
                job_page_response = get_job_page()
                job_page_soup = BeautifulSoup(job_page_response.content, 'lxml')

                description_element = job_page_soup.find('div', class_='jobsearch-JobComponent-description')
                if description_element:
                    description = description_element.text.strip()

                # Simple skill extraction (can be improved with NLP later)
                skills_text = description.lower()
                possible_skills = ["python", "java", "c++", "javascript", "react", "angular", "node.js", "aws", "azure", "gcp", "docker", "kubernetes", "sql", "nosql", "machine learning", "deep learning", "nlp", "fastapi", "django", "flask", "spring", "agile", "scrum"]
                skills = [skill for skill in possible_skills if skill in skills_text]

            jobs.append({
                "title": title,
                "company": company,
                "description": description,
                "skills": skills,
                "location": location,
                "link": link
            })
        return jobs
    except requests.exceptions.RequestException as e:
        error_counter.inc()
        raise e

def scrape_linkedin(search_term: str = "software engineer", location: str = "remote") -> List[Dict]:
    # Placeholder for LinkedIn scraping logic
    print(f"Scraping LinkedIn for {search_term} in {location}")
    return []

def scrape_remoteok(search_term: str = "software engineer", location: str = "remote") -> List[Dict]:
    # Placeholder for RemoteOK scraping logic
    print(f"Scraping RemoteOK for {search_term} in {location}")
    return []

@app.get("/scrape-jobs")
async def scrape_jobs(site: Optional[str] = None, search_term: str = "software engineer", location: str = "remote"):
    if site == "indeed":
        return scrape_indeed(search_term, location)
    elif site == "linkedin":
        return scrape_linkedin(search_term, location)
    elif site == "remoteok":
        return scrape_remoteok(search_term, location)
    elif site is None:
        # Scrape all sites if no specific site is provided
        all_jobs = []
        all_jobs.extend(scrape_indeed(search_term, location))
        all_jobs.extend(scrape_linkedin(search_term, location))
        all_jobs.extend(scrape_remoteok(search_term, location))
        return all_jobs
    else:
        raise HTTPException(status_code=400, detail="Invalid site specified. Supported sites: indeed, linkedin, remoteok")

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