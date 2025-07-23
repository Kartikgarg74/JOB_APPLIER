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
from packages.database.config import engine, SessionLocal, Base, get_database_url

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
