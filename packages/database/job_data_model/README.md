# Job Data Model Module

## Purpose
This module (`job_data_model.py`) defines the SQLAlchemy ORM model for job listings and provides a `JobDatabase` class for interacting with these job listings in the database. It handles operations such as adding, retrieving, updating, searching, and deleting job entries.

## Dependencies
- `sqlalchemy`: For defining ORM models, columns, and database interactions.
- `sqlalchemy.orm.Session`: For type hinting database sessions.
- `sqlalchemy.exc.SQLAlchemyError`, `sqlalchemy.exc.IntegrityError`: For handling database-specific exceptions.
- `datetime.datetime`: For handling date/time fields.
- `uuid`: For generating unique IDs for job listings.
- `logging`: For logging database operations and errors.
- `packages.database.config.Base`: The declarative base class for ORM models.
- `packages.database.config.SessionLocal`: The session factory for creating database sessions.

## Key Components

### `JobListing` Model
- **Table Name**: `job_listings`
- **Purpose**: Represents a single job listing in the database.
- **Fields**:
  - `id` (String, Primary Key): Unique ID for the job listing (e.g., from a job board, or a generated UUID).
  - `title` (String, Not Null)
  - `company` (String, Not Null)
  - `location` (String, Not Null)
  - `description` (Text, Not Null)
  - `requirements` (Text, Nullable)
  - `salary` (String, Nullable)
  - `posting_date` (DateTime, Nullable)
  - `url` (String, Not Null, Unique): The URL to the job posting.
  - `source` (String, Nullable): The source of the job listing (e.g., Indeed, LinkedIn).
  - `date_discovered` (DateTime, Default: UTC Now): When the job was first discovered.
  - `is_applied` (Boolean, Default: False): Flag indicating if the user has applied to this job.
  - `application_status` (String, Default: 'Pending'): Current status of the application (e.g., 'Pending', 'Applied', 'Interviewing', 'Rejected').

### `JobDatabase` Class
- **Purpose**: Provides a set of methods to perform CRUD (Create, Read, Update, Delete) and search operations on `JobListing` records.
- **Methods**:
  - `__init__()`:
    - Initializes the logger for the class.
  - `add_job_listing(session: Session, job_data: dict)`:
    - **Purpose**: Adds a new job listing to the database.
    - **Logic**: Checks if a job with the same URL already exists to prevent duplicates. Generates a UUID if `id` is not provided. Handles `IntegrityError` for duplicates and general `SQLAlchemyError`.
    - **Returns**: The `JobListing` object if added or already exists.
  - `get_job_listing(session: Session, job_id: str)`:
    - **Purpose**: Retrieves a single job listing by its ID.
    - **Returns**: The `JobListing` object or `None` if not found.
  - `get_all_job_listings(session: Session)`:
    - **Purpose**: Retrieves all job listings from the database.
    - **Returns**: A list of `JobListing` objects.
  - `update_job_listing(session: Session, job_id: str, updated_data: dict)`:
    - **Purpose**: Updates an existing job listing with new data.
    - **Logic**: Finds the job by ID and updates its attributes based on the `updated_data` dictionary. Handles `SQLAlchemyError`.
    - **Returns**: `True` if updated, `False` if job not found.
  - `search_job_listings(session: Session, query: str = None, location: str = None, salary_min: float = None, posting_date_after: datetime = None)`:
    - **Purpose**: Searches for job listings based on various criteria.
    - **Logic**: Filters jobs by title/description query, location, minimum salary (placeholder for string parsing), and posting date.
    - **Returns**: A list of matching `JobListing` objects.
  - `delete_job_listing(session: Session, job_id: str)`:
    - **Purpose**: Deletes a job listing by its ID.
    - **Logic**: Finds the job by ID and deletes it. Handles `SQLAlchemyError`.
    - **Returns**: `True` if deleted, `False` if job not found.

## Workflow
1. The module defines the `JobListing` ORM model, mapping Python attributes to database columns.
2. The `JobDatabase` class encapsulates all database operations related to job listings.
3. Methods within `JobDatabase` utilize SQLAlchemy sessions to perform queries, insertions, updates, and deletions.
4. Error handling is implemented to catch database-related exceptions and provide informative logging.
5. Sessions are closed in `finally` blocks to ensure proper resource management.

## Usage
```python
from packages.database.config import SessionLocal
from packages.database.job_data_model import JobDatabase
from datetime import datetime

# Initialize JobDatabase handler
job_db_handler = JobDatabase()

# Get a database session
db_session = SessionLocal()

try:
    # Example: Add a new job listing
    new_job_data = {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "San Francisco, CA",
        "description": "Develop and maintain software applications.",
        "url": "https://example.com/job/123",
        "requirements": "5+ years experience",
        "salary": "$120,000",
        "posting_date": datetime(2023, 10, 26),
        "source": "LinkedIn"
    }
    added_job = job_db_handler.add_job_listing(db_session, new_job_data)
    print(f"Added job: {added_job.title} at {added_job.company}")

    # Example: Get a job listing
    retrieved_job = job_db_handler.get_job_listing(db_session, added_job.id)
    if retrieved_job:
        print(f"Retrieved job: {retrieved_job.title}")

    # Example: Update a job listing
    updated = job_db_handler.update_job_listing(db_session, added_job.id, {"application_status": "Applied"})
    if updated:
        print(f"Job status updated for {added_job.title}")

    # Example: Search for jobs
    search_results = job_db_handler.search_job_listings(db_session, query="Engineer", location="San Francisco")
    print(f"Found {len(search_results)} jobs matching criteria.")

    # Example: Delete a job listing
    # deleted = job_db_handler.delete_job_listing(db_session, added_job.id)
    # if deleted:
    #     print(f"Deleted job: {added_job.title}")

except RuntimeError as e:
    print(f"Operation failed: {e}")
finally:
    db_session.close()
```