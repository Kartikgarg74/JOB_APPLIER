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
from packages.database.models import User

# Use a separate test database
os.environ["DATABASE_NAME"] = "test_user_api.db"

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
        override_get_db  # This line needs to be adjusted based on how get_db is imported and used in user_api.py
    )
    yield TestClient(app)
    del app.dependency_overrides[session.get_bind().url]


def test_register_user_success(client, session):
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert session.query(User).filter(User.username == "testuser").first() is not None


def test_register_user_duplicate_username(client, session):
    # First registration
    client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    # Second registration with same username
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "password456",
        },
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_login_user_success(client, session):
    # Register a user first
    client.post(
        "/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "loginpassword",
        },
    )
    # Attempt to login
    response = client.post(
        "/login", json={"username": "loginuser", "password": "loginpassword"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "loginuser"


def test_login_user_invalid_credentials(client, session):
    response = client.post(
        "/login", json={"username": "nonexistent", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]


# TODO: Add tests for Google OAuth after implementing proper mocking for google.oauth2.id_token.verify_oauth2_token
