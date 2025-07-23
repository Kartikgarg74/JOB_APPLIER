import pytest
from fastapi.testclient import TestClient
from src.main import app
import io
from docx import Document

client = TestClient(app)


# Test cases for /score_ats endpoint
def test_score_ats_success():
    with TestClient(app) as client:
        resume_text = "Test Resume Content with Python and Java skills."
        job_description = "Software Engineer with strong Python and Java experience."
        response = client.post(
            "/score_ats",
            json={"resume_text": resume_text, "job_description": job_description},
        )
        assert response.status_code == 200
        assert "score" in response.json()
        assert "recommendations" in response.json()


def test_score_ats_missing_resume_text():
    with TestClient(app) as client:
        job_description = "Software Engineer"
        response = client.post("/score_ats", json={"job_description": job_description})
        assert response.status_code == 422  # Unprocessable Entity for missing field


def test_score_ats_missing_job_description():
    with TestClient(app) as client:
        resume_text = "Test Resume Content"
        response = client.post("/score_ats", json={"resume_text": resume_text})
        assert response.status_code == 422  # Unprocessable Entity for missing field
