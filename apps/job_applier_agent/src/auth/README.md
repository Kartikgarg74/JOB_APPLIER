# Auth API Module

## Purpose
This module provides API endpoints for user authentication, including traditional username/password registration and login, as well as Google OAuth integration. It handles user creation, authentication, and token generation.

## Dependencies
- `fastapi`: For building the API endpoints.
- `sqlalchemy`: For database interactions with user models.
- `passlib`: For password hashing and verification (bcrypt).
- `jose`: For JWT (JSON Web Token) creation and encoding.
- `google.oauth2.id_token`, `google.auth.transport.requests`: For Google OAuth ID token verification.
- `fastapi_limiter`: For rate limiting API requests.
- `logging`: For logging events and errors.
- `packages.errors.custom_exceptions.JobApplierException`: Custom exception handling.
- `packages.database.config.SessionLocal`: Database session management.
- `packages.database.models.User`: User model definition.
- `packages.config.config`: Configuration variables like `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`.
- `.schemas`: Pydantic models for request and response data (`UserCreate`, `UserLogin`, `UserResponse`, `GoogleAuthCallback`).

## Key Components

### `router` (APIRouter)
An instance of FastAPI's `APIRouter` to define and group authentication-related endpoints.

### `GOOGLE_CLIENT_ID`
Environment variable storing the Google OAuth client ID, essential for verifying Google ID tokens.

### `pwd_context` (CryptContext)
An instance of `passlib.context.CryptContext` configured for bcrypt hashing, used for securely storing and verifying user passwords.

### `get_db()`
A dependency function that provides a SQLAlchemy database session to API endpoints, ensuring proper session management (opening and closing).

### `create_access_token(data: dict, expires_delta: Optional[timedelta] = None)`
Generates a JWT access token. It encodes user data with an expiration time using the configured `SECRET_KEY` and `ALGORITHM`.

### Endpoints
- `POST /register`:
  - **Purpose**: Registers a new user. Supports both password-based registration and Google ID-based registration.
  - **Request Body**: `UserCreate` schema (username, email, optional password, optional google_id, optional image).
  - **Response**: `UserResponse` schema (details of the newly created user).
  - **Error Handling**: Handles existing usernames/Google IDs, invalid registration attempts (e.g., providing both password and Google ID), and database errors.
  - **Rate Limiting**: 5 requests per 10 seconds.

- `POST /login`:
  - **Purpose**: Authenticates an existing user with username and password.
  - **Request Body**: `UserLogin` schema (username, password).
  - **Response**: A dictionary containing `access_token` and `token_type`.
  - **Error Handling**: Handles invalid credentials and database errors.
  - **Rate Limiting**: 5 requests per 10 seconds.

- `POST /auth/google`:
  - **Purpose**: Handles the callback for Google OAuth authentication. Verifies the Google ID token and either logs in an existing Google-registered user or registers a new one.
  - **Request Body**: `GoogleAuthCallback` schema (id_token).
  - **Response**: A dictionary containing `access_token` and `token_type`.
  - **Error Handling**: Handles invalid Google ID tokens, and database errors.
  - **Rate Limiting**: 5 requests per 10 seconds.

## Workflow
1. **Initialization**: The module sets up logging, initializes the password context, and retrieves the Google Client ID from environment variables.
2. **Database Session**: `get_db` dependency ensures each request gets a fresh database session.
3. **User Registration (`/register`)**:
   - Validates input: ensures either password or Google ID is provided, but not both.
   - Checks for existing users based on username (for password) or Google ID (for Google OAuth).
   - Hashes password if provided.
   - Creates a new `User` entry in the database.
   - Returns the created user's details.
4. **User Login (`/login`)**:
   - Retrieves user from the database by username.
   - Verifies the provided password against the stored hash.
   - If successful, generates an access token using `create_access_token`.
   - Returns the access token.
5. **Google OAuth (`/auth/google`)**:
   - Verifies the Google ID token using Google's `id_token.verify_oauth2_token`.
   - Extracts user information (google_id, email, name, image).
   - Checks if a user with the extracted `google_id` already exists in the database.
   - If not, creates a new user entry with the Google details.
   - Generates and returns an access token for the user.

## Usage Examples

### Registering a new user with password
```python
import requests

url = "http://localhost:8000/auth/register"
headers = {"Content-Type": "application/json"}
data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### Logging in a user
```python
import requests

url = "http://localhost:8000/auth/login"
headers = {"Content-Type": "application/json"}
data = {
    "username": "testuser",
    "password": "securepassword123"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### Google OAuth (client-side flow)
(This example assumes you have obtained the `id_token` from the Google client-side authentication flow)
```python
import requests

url = "http://localhost:8000/auth/google"
headers = {"Content-Type": "application/json"}
data = {
    "id_token": "YOUR_GOOGLE_ID_TOKEN_HERE"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

## Security Considerations
- **Environment Variables**: `GOOGLE_CLIENT_ID`, `SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES` are loaded from environment variables, which is a good practice for sensitive information.
- **Password Hashing**: Passwords are hashed using bcrypt via `passlib`, ensuring they are not stored in plain text.
- **JWT Security**: Access tokens are signed with a `SECRET_KEY` to prevent tampering. Ensure this key is strong and kept confidential.
- **Rate Limiting**: `fastapi_limiter` is used to prevent brute-force attacks on registration and login endpoints.
- **Error Handling**: Custom exceptions (`JobApplierException`) are used to provide controlled error responses without exposing sensitive internal details.
- **Token Expiration**: Access tokens have a defined expiration time to limit the window of opportunity for token misuse.

## Error Handling
- `JobApplierException` is raised for business logic errors (e.g., username already exists, invalid credentials) with appropriate HTTP status codes and details.
- `SQLAlchemyError` and general `Exception` handling are in place to catch unexpected database or runtime errors, providing generic 500 responses to the client while logging detailed errors internally.