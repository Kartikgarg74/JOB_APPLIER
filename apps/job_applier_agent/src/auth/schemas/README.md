# Auth Schemas Module

## Purpose
This module defines the Pydantic models (schemas) used for data validation and serialization within the authentication API. These schemas ensure that incoming request data conforms to expected formats and that outgoing response data is structured correctly.

## Dependencies
- `pydantic`: The core library for data validation and settings management.
- `typing.Optional`: For fields that can be `None`.

## Key Components

### `UserCreate`
- **Purpose**: Defines the structure for creating a new user, supporting both traditional password-based registration and Google OAuth registration.
- **Fields**:
  - `username` (str): Required, min 3, max 50 characters.
  - `email` (EmailStr): Required, valid email format.
  - `password` (Optional[str]): Optional, min 8, max 100 characters. Used for traditional registration.
  - `google_id` (Optional[str]): Optional. Used for Google OAuth registration.
  - `image` (Optional[str]): Optional. URL to user's profile image, typically from Google OAuth.

### `UserLogin`
- **Purpose**: Defines the structure for user login requests.
- **Fields**:
  - `username` (str): Required, min 3, max 50 characters.
  - `password` (str): Required, min 8, max 100 characters.

### `UserResponse`
- **Purpose**: Defines the structure for user data returned in API responses.
- **Fields**:
  - `id` (int): The unique identifier for the user.
  - `username` (str): The user's username.
  - `email` (str): The user's email address.
  - `google_id` (Optional[str]): The user's Google ID, if registered via Google OAuth.
  - `image` (Optional[str]): URL to user's profile image.
  - `is_active` (bool): Indicates if the user account is active.
- **Config**: `from_attributes = True` allows mapping from ORM objects.

### `UserUpdate`
- **Purpose**: Defines the structure for updating existing user profile information. All fields are optional, allowing partial updates.
- **Fields**:
  - `username` (Optional[str])
  - `email` (Optional[str])
  - `image` (Optional[str])
  - `phone` (Optional[str])
  - `address` (Optional[str])
  - `portfolio_url` (Optional[str])
  - `personal_website` (Optional[str])
  - `linkedin_profile` (Optional[str])
  - `github_profile` (Optional[str])
  - `years_of_experience` (Optional[int])
  - `skills` (Optional[list[str]])
- **Config**: `from_attributes = True` allows mapping from ORM objects.

### `GoogleAuthCallback`
- **Purpose**: Defines the structure for the Google OAuth callback request, specifically to receive the ID token.
- **Fields**:
  - `id_token` (str): The Google ID token received from the client-side authentication flow.

## Usage
These schemas are primarily used in `auth_api.py` to validate incoming JSON payloads and to serialize Python objects into JSON responses. They ensure data integrity and provide clear documentation of the API's data structures.