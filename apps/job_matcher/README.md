# Job Matcher Service

This FastAPI microservice provides semantic job matching capabilities using SentenceTransformers. It converts job descriptions and resume content into embeddings and computes cosine similarity to find the most relevant job listings for a given resume.

## Features

- Converts text into semantic embeddings.
- Computes cosine similarity between job descriptions and resumes.
- Identifies top matching jobs.

## API Endpoints

### `/match-jobs`

Matches a resume against a job description and returns a similarity score.

- **Method**: `POST`
- **Request Body**:
    ```json
    {
      "job_description": "string",
      "resume_content": "string"
    }
    ```
- **Response**:
    ```json
    [
      {
        "similarity_score": 0.85,
        "matched_keywords": ["Python", "FastAPI"],
        "missing_keywords": ["Docker"]
      }
    ]
    ```

## Running Locally

1.  **Prerequisites**:
    - Python 3.9+
    - `pip`

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the FastAPI application**:
    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000
    ```

## Running with Docker

1.  **Build the Docker image**:
    ```bash
    docker build -t job-matcher-service .
    ```

2.  **Run the Docker container**:
    ```bash
    docker run -p 8000:8000 job-matcher-service
    ```