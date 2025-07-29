# Resume Parser Service

A FastAPI microservice that parses resumes (PDF, DOCX, or plaintext) into structured JSON data.

## Features
- Accepts PDF, DOCX and plaintext resumes
- Extracts structured fields (name, email, skills, education, experience, etc.)
- Uses spaCy NLP and regex patterns for robust parsing
- Returns JSON matching the job matcher's expected schema
- Comprehensive error handling

## API Endpoints

### POST `/parse-resume`
Parse a resume file and return structured data.

**Request:**
```
Content-Type: multipart/form-data
File: resume.pdf (or .docx/.txt)
```

**Successful Response (200):**
```json
{
  "personal_details": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "(123) 456-7890"
  },
  "education": [
    {
      "degree": "Master of Science",
      "university": "Stanford",
      "year": "2020"
    }
  ],
  "experience": [
    {
      "title": "Software Engineer",
      "company": "Tech Corp",
      "date_range": "2018-Present"
    }
  ],
  "skills": ["Python", "JavaScript"],
  "projects": [...]
}
```

**Error Responses:**
- 400: Unsupported file format
- 422: Parsing failed
- 500: Server error

## Running Locally
1. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. Start the service:
```bash
uvicorn src.main:app --reload
```

## Docker
```bash
docker build -t resume-parser .
docker run -p 8000:8000 resume-parser
```

## Testing
```bash
curl -X POST -F "file=@resume.pdf" http://localhost:8000/parse-resume
```