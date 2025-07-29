# User Service

This service handles user authentication, profile management, and related data within the Job Applier platform.

## Features

- **User Authentication**: Signup, login, and session management.
- **User Profiles**: Create, retrieve, update, and delete user profiles.
- **File Uploads**: Manage user-specific file uploads (e.g., resumes).
- **Metrics**: Exposes Prometheus metrics for monitoring.
- **Health Checks**: Provides health and status endpoints.
- **Security**: Implements security headers and CORS middleware.

## API Endpoints

### User Authentication
- `POST /users/signup`: Register a new user.
- `POST /users/login`: Authenticate a user and return a token.
- `POST /users/logout`: Invalidate a user's session.

### User Profiles
- `GET /profiles/{user_id}`: Retrieve a user's profile.
- `PUT /profiles/{user_id}`: Update a user's profile.

### System Endpoints
- `GET /metrics`: Exposes Prometheus metrics.
- `GET /health`: Health check endpoint.
- `GET /status`: Get service status and uptime.

## How to Run Locally

### Prerequisites

- Python 3.9+
- `pip` (Python package installer)

### Installation

1. Navigate to the `user_service` directory:
   ```bash
   cd apps/user_service
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

1. Navigate to the `user_service` directory:
   ```bash
   cd apps/user_service
   ```

2. Build the Docker image:
   ```bash
   docker build -t user-service .
   ```

3. Run the Docker container:
   ```bash
   docker run -p 8000:8000 user-service
   ```

The service will be accessible at `http://localhost:8000`.