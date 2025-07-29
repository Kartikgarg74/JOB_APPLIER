# ATS Scoring Service

This service provides an ATS (Applicant Tracking System) scoring mechanism to evaluate the compatibility of a resume with a given job description. It leverages natural language processing (NLP) techniques to extract keywords, calculate relevance scores, and identify missing terms.

## Features

- **Keyword Extraction**: Identifies key terms from both resume content and job descriptions.
- **TF-IDF Vectorization**: Converts text into numerical representations for similarity calculations.
- **Cosine Similarity**: Measures the semantic similarity between resume and job description.
- **Matched/Missing Keywords**: Highlights keywords present in both and those missing from the resume.
- **Readability and Formatting Scores (Placeholder)**: Future enhancements to include these metrics.

## API Endpoints

### `/ats-score` (POST)

Calculates the ATS score, matched keywords, and missing keywords based on the provided resume content and job description.

**Request Body:**

```json
{
  "resume_content": "Your resume content as a string...",
  "job_description": "The job description as a string..."
}
```

**Response Body (Example):**

```json
{
  "ats_score": 85.5,
  "matched_keywords": ["Python", "FastAPI", "Machine Learning"],
  "missing_keywords": ["Docker", "Kubernetes"],
  "readability_score": 0.0, // Placeholder
  "formatting_score": 0.0 // Placeholder
}
```

## How to Run Locally

### Prerequisites

- Python 3.9+
- `pip` (Python package installer)

### Installation

1. Navigate to the `ats_service` directory:
   ```bash
   cd apps/ats_service
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Service

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

The service will be accessible at `http://localhost:8000`.

## How to Run with Docker

1. Navigate to the `ats_service` directory:
   ```bash
   cd apps/ats_service
   ```

2. Build the Docker image:
   ```bash
   docker build -t ats-service .
   ```

3. Run the Docker container:
   ```bash
   docker run -p 8000:8000 ats-service
   ```

The service will be accessible at `http://localhost:8000`.