import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
sys.path.insert(0, project_root)

from src.main import app
from packages.database.config import Base, get_database_url
from packages.database.models import (
    User,
)  # Assuming User model is needed for token verification

# Use a separate test database
os.environ["DATABASE_NAME"] = "test_agent_api.db"

test_engine = create_engine(
    get_database_url(), connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(name="session")
def session_fixture():
    # Ensure a clean test database for each test
    test_db_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        os.environ["DATABASE_NAME"],
    )
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    Base.metadata.clear()
    Base.metadata.create_all(test_engine)
    with TestingSessionLocal() as session:
        yield session
    Base.metadata.drop_all(test_engine)
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        yield session

    app.dependency_overrides[session.get_bind().url] = (
        override_get_db  # This line needs to be adjusted based on how get_db is imported and used in agent_api.py
    )
    yield TestClient(app)
    del app.dependency_overrides[session.get_bind().url]


# Mock data for agents (replace with more sophisticated mocks as needed)
class MockResumeParserAgent:
    def __init__(self, db):
        pass

    def parse_resume(self, resume_text):
        return {"name": "John Doe", "email": "john.doe@example.com"}


class MockATSScorerAgent:
    def __init__(self, db):
        pass

    def score_ats(self, job_description, resume_text):
        return 85


class MockJobMatcherAgent:
    def __init__(self, db):
        pass

    def match_jobs(self, user_profile):
        return [{"title": "Software Engineer", "company": "Tech Corp"}]


class MockApplicationAutomationAgent:
    def __init__(self, db):
        pass

    def apply_for_job(self, application_data):
        return {"status": "success", "message": "Application submitted"}


class MockCoverLetterGeneratorAgent:
    def __init__(self, db):
        pass

    def generate_cover_letter(self, cover_letter_data):
        return "Dear Hiring Manager, ..."


# Override agent dependencies for testing
@pytest.fixture(autouse=True)
def override_agents():
    from packages.agents.resume_parser_agent import ResumeParserAgent
    from packages.agents.ats_scorer_agent import ATSScorerAgent
    from packages.agents.job_matcher_agent import JobMatcherAgent
    from packages.agents.application_automation_agent import ApplicationAutomationAgent
    from packages.agents.cover_letter_generator_agent import CoverLetterGeneratorAgent

    app.dependency_overrides[ResumeParserAgent] = MockResumeParserAgent
    app.dependency_overrides[ATSScorerAgent] = MockATSScorerAgent
    app.dependency_overrides[JobMatcherAgent] = MockJobMatcherAgent
    app.dependency_overrides[ApplicationAutomationAgent] = (
        MockApplicationAutomationAgent
    )
    app.dependency_overrides[CoverLetterGeneratorAgent] = MockCoverLetterGeneratorAgent
    yield
    del app.dependency_overrides[ResumeParserAgent]
    del app.dependency_overrides[ATSScorerAgent]
    del app.dependency_overrides[JobMatcherAgent]
    del app.dependency_overrides[ApplicationAutomationAgent]
    del app.dependency_overrides[CoverLetterGeneratorAgent]


# Helper for authenticated requests
def authenticated_client(client):
    # In a real scenario, this would involve generating a valid token
    # For now, we use the dummy token expected by verify_token
    return client.headers({"Authorization": "Bearer dummy_token"})


def test_parse_resume_endpoint(client):
    response = client.post(
        "/parse_resume",
        json={"resume_text": "This is a test resume."},  # Use json= for body
        headers={"Authorization": "Bearer dummy_token"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Resume parsed successfully"
    assert "name" in response.json()["parsed_data"]


def test_score_ats_endpoint(client):
    response = client.post(
        "/score_ats",
        json={
            "job_description": "Software Engineer",
            "resume_text": "My resume content.",
        },
        headers={"Authorization": "Bearer dummy_token"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "ATS score generated successfully"
    assert response.json()["score"] == 85


def test_match_jobs_endpoint(client):
    response = client.post(
        "/match_jobs",
        json={"user_profile": {"skills": ["Python", "FastAPI"]}},
        headers={"Authorization": "Bearer dummy_token"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Jobs matched successfully"
    assert len(response.json()["matched_jobs"]) > 0


def test_apply_for_job_endpoint(client):
    response = client.post(
        "/apply",
        json={"application_data": {"job_id": "123", "user_id": "abc"}},
        headers={"Authorization": "Bearer dummy_token"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Application process initiated"
    assert response.json()["result"]["status"] == "success"


def test_generate_cover_letter_endpoint(client):
    response = client.post(
        "/coverletter/generate",
        json={"cover_letter_data": {"job_title": "Developer", "company": "XYZ"}},
        headers={"Authorization": "Bearer dummy_token"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Cover letter generated successfully"
    assert "Dear Hiring Manager" in response.json()["cover_letter"]


# Test for unauthorized access
def test_unauthorized_access(client):
    response = client.post(
        "/parse_resume",
        json={"resume_text": "This is a test resume."},  # Use json= for body
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401
    assert "Invalid authentication credentials" in response.json()["detail"]
