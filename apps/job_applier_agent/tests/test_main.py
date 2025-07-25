import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from src.main import app
from packages.database.config import SessionLocal, Base, get_database_url

from packages.database.models import (
    User,
    Education,
    Experience,
    Project,
    JobPreference,
)  # Explicitly import all models


# Use a separate test database
os.environ["DATABASE_NAME"] = "test.db"

test_engine = create_engine(
    get_database_url(), connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(name="session")
def session_fixture():
    # Ensure a clean test database for each test
    test_db_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "test.db"
    )
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    Base.metadata.clear()
    Base.metadata.create_all(test_engine)
    with TestingSessionLocal() as session:
        yield session
    Base.metadata.drop_all(test_engine)


@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        yield session

    app.dependency_overrides[SessionLocal] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[SessionLocal]


client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Job Applier API"}


def test_http_exception_handler():
    response = client.get("/nonexistent_route")
    assert response.status_code == 404
    assert response.json() == {"message": "Not Found"}


# Assuming a profile endpoint exists and returns a 404 for a non-existent user
def test_read_profile_nonexistent():
    response = client.get("/profile/99999")  # Using a non-existent user ID
    assert response.status_code == 404
    assert response.json() == {"message": "User not found"}


def test_config_caching():
    r1 = client.get("/v1/config")
    assert r1.status_code == 200
    data1 = r1.json()
    r2 = client.get("/v1/config")
    assert r2.status_code == 200
    data2 = r2.json()
    assert data1 == data2
    assert "status" in data1 and "data" in data1

def test_health_caching():
    r1 = client.get("/v1/health")
    assert r1.status_code == 200
    data1 = r1.json()
    r2 = client.get("/v1/health")
    assert r2.status_code == 200
    data2 = r2.json()
    assert data1 == data2
    assert data1["status"] == "ok"

def test_status_caching():
    r1 = client.get("/v1/status")
    assert r1.status_code == 200
    data1 = r1.json()
    r2 = client.get("/v1/status")
    assert r2.status_code == 200
    data2 = r2.json()
    assert data1 == data2
    assert "status" in data1 and "data" in data1

def test_notifications_caching():
    # This test assumes user_id=1 exists or returns an empty list
    r1 = client.get("/v1/notifications/1")
    assert r1.status_code == 200
    data1 = r1.json()
    r2 = client.get("/v1/notifications/1")
    assert r2.status_code == 200
    data2 = r2.json()
    assert data1 == data2
    assert isinstance(data1, list)

def test_metrics_endpoint():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert b"# HELP" in r.content and b"job_applications_total" in r.content
