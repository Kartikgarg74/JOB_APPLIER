# Job Scraper Service

This FastAPI microservice is responsible for scraping job listings from various platforms like Indeed, LinkedIn, and RemoteOK. It uses BeautifulSoup for parsing and Celery for scheduling and asynchronous task processing. Scraped job data is intended to be stored in a PostgreSQL database.

## Features

- Scrapes job listings from specified platforms.
- Asynchronous job scraping using Celery.
- Returns structured JSON data for each job listing.

## API Endpoints

### `/scrape-jobs`

Initiates the job scraping process for a specified site.

- **Method**: `GET`
- **Query Parameters**:
    - `site` (string, optional): The job site to scrape (e.g., `indeed`). Defaults to `indeed`.
- **Response**:
```json
{
  "task_id": "<celery_task_id>"
}
```

## Running Locally

1.  **Prerequisites**:
    - Python 3.9+
    - `pip`
    - Redis (for Celery broker and backend)
    - PostgreSQL (for storing job data)

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the FastAPI application**:
    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000
    ```

4.  **Run the Celery worker**:
    ```bash
    celery -A src.main.celery worker --loglevel=info
    ```

## Running with Docker

1.  **Build the Docker image**:
    ```bash
    docker build -t job-scraper-service .
    ```

2.  **Run the Docker container**:
    ```bash
    docker run -p 8000:8000 job-scraper-service
    ```

    *Note: You will need to ensure your Redis and PostgreSQL instances are accessible from within the Docker container.*