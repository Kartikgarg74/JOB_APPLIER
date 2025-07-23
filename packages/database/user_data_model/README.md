# User Data Model Module

## Purpose
This module (`user_data_model.py`) provides a `UserDatabase` class that encapsulates all database operations related to user profiles and their associated data, such as education, experience, projects, skills, and job preferences. It acts as a data access layer for managing complex user-centric information.

## Dependencies
- `sqlalchemy.orm.Session`: For type hinting database sessions.
- `sqlalchemy.exc.IntegrityError`, `sqlalchemy.exc.SQLAlchemyError`: For handling database-specific exceptions.
- `packages.database.models`: Imports all ORM models (`User`, `Education`, `Experience`, `Project`, `Skill`, etc.) that this module interacts with.
- `packages.database.config.SessionLocal`: The session factory for creating database sessions.

## Key Components

### `UserDatabase` Class
- **Purpose**: Provides a comprehensive set of methods for managing user data, including CRUD operations for the `User` model and its related models (Education, Experience, Project, Skill, etc.).
- **Methods**:
  - `add_user(session: Session, username, email, hashed_password)`:
    - **Purpose**: Adds a new user with a username, email, and hashed password.
    - **Error Handling**: Raises `ValueError` if username/email already exists, `RuntimeError` for other database errors.
  - `add_user_google(session: Session, username, email, google_id, image_url=None)`:
    - **Purpose**: Adds a new user registered via Google OAuth.
    - **Error Handling**: Raises `ValueError` if email/Google ID already exists, `RuntimeError` for other database errors.
  - `get_user_by_username(session: Session, username)`:
    - **Purpose**: Retrieves a user by their username.
  - `get_user_by_email(session: Session, email)`:
    - **Purpose**: Retrieves a user by their email address.
  - `get_user_by_id(session: Session, user_id)`:
    - **Purpose**: Retrieves a user by their unique ID.
  - `get_user_by_google_id(session: Session, google_id)`:
    - **Purpose**: Retrieves a user by their Google ID.
  - `update_user_profile(session: Session, user_id, profile_data)`:
    - **Purpose**: Updates a user's main profile information (e.g., phone, address, social links).
    - **Returns**: The updated `User` object or `None` if user not found.
  - `add_education(session: Session, user_id, education_data)`:
    - **Purpose**: Adds a new education entry for a user.
  - `get_education(session: Session, user_id)`:
    - **Purpose**: Retrieves all education entries for a user.
  - `update_education(session: Session, education_id, education_data)`:
    - **Purpose**: Updates an existing education entry.
  - `delete_education(session: Session, education_id)`:
    - **Purpose**: Deletes an education entry.
  - `add_experience(session: Session, user_id, experience_data)`:
    - **Purpose**: Adds a new work experience entry for a user.
  - `get_experience(session: Session, user_id)`:
    - **Purpose**: Retrieves all work experience entries for a user.
  - `update_experience(session: Session, experience_id, experience_data)`:
    - **Purpose**: Updates an existing work experience entry.
  - `delete_experience(session: Session, experience_id)`:
    - **Purpose**: Deletes a work experience entry.
  - `add_project(session: Session, user_id, project_data)`:
    - **Purpose**: Adds a new project entry for a user.
  - `get_projects(session: Session, user_id)`:
    - **Purpose**: Retrieves all project entries for a user.
  - `update_project(session: Session, project_id, project_data)`:
    - **Purpose**: Updates an existing project entry.
  - `delete_project(session: Session, project_id)`:
    - **Purpose**: Deletes a project entry.
  - `add_skill(session: Session, user_id, skill_data)`:
    - **Purpose**: Adds a new skill entry for a user.
  - `get_skills(session: Session, user_id)`:
    - **Purpose**: Retrieves all skill entries for a user.
  - `update_skill(session: Session, skill_id, skill_data)`:
    - **Purpose**: Updates an existing skill entry.
  - `delete_skill(session: Session, skill_id)`:
    - **Purpose**: Deletes a skill entry.
  - `add_job_preference(session: Session, user_id, preference_data)`:
    - **Purpose**: Adds or updates a user's job preferences.
  - `get_job_preference(session: Session, user_id)`:
    - **Purpose**: Retrieves a user's job preferences.
  - `update_job_preference(session: Session, user_id, preference_data)`:
    - **Purpose**: Updates a user's job preferences.
  - `delete_job_preference(session: Session, user_id)`:
    - **Purpose**: Deletes a user's job preferences.
  - (Additional methods for Certification, Language, Award, Publication, Patent, VolunteerExperience, Reference, CustomSection, if those models are fully implemented and used.)

## Workflow
1. The `UserDatabase` class is instantiated, providing an interface to user-related data operations.
2. Each method takes a SQLAlchemy `Session` object as an argument, ensuring that operations are performed within a transactional context.
3. Methods interact with the ORM models (`User`, `Education`, etc.) to perform database queries, insertions, updates, and deletions.
4. Error handling is implemented using `try...except...finally` blocks to catch `IntegrityError` (for unique constraints) and `SQLAlchemyError` (for general database issues), rolling back sessions on errors and raising custom `RuntimeError` or `ValueError` exceptions.
5. Sessions are typically managed externally (e.g., by FastAPI dependencies) and passed into these methods.

## Usage
```python
from packages.database.config import SessionLocal
from packages.database.user_data_model import UserDatabase
from datetime import datetime

# Initialize UserDatabase handler
user_db_handler = UserDatabase()

# Get a database session
db_session = SessionLocal()

try:
    # Example: Add a new user
    new_user = user_db_handler.add_user(db_session, "johndoe", "john@example.com", "hashed_password_here")
    print(f"Added user: {new_user.username}")

    # Example: Get user by username
    user = user_db_handler.get_user_by_username(db_session, "johndoe")
    if user:
        print(f"Retrieved user: {user.email}")

    # Example: Update user profile
    updated_user = user_db_handler.update_user_profile(db_session, user.id, {"phone": "123-456-7890"})
    if updated_user:
        print(f"Updated user phone: {updated_user.phone}")

    # Example: Add education
    education_data = {
        "user_id": user.id,
        "degree": "B.Sc. Computer Science",
        "university": "University of Example",
        "field_of_study": "Computer Science",
        "start_date": datetime(2015, 9, 1),
        "end_date": datetime(2019, 5, 30),
    }
    added_education = user_db_handler.add_education(db_session, user.id, education_data)
    print(f"Added education: {added_education.degree}")

    # Example: Get education
    user_education = user_db_handler.get_education(db_session, user.id)
    print(f"User education: {[edu.degree for edu in user_education]}")

    # ... similar examples for experience, projects, skills, job preferences

except (ValueError, RuntimeError) as e:
    print(f"Operation failed: {e}")
finally:
    db_session.close()
```