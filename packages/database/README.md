# Database Package

This package is responsible for all database-related operations within the Job Applier Agent. It handles data storage, retrieval, and management for various components of the system.

## Purpose

The primary purpose of the database package is to provide a persistent storage layer for job application data, user profiles, scraped job listings, and any other information that needs to be stored and retrieved across sessions.

## Key Components

- <mcfile name="job_data_model.py" path="packages/database/job_data_model.py"></mcfile>: Defines the data model for job listings and provides the <mcsymbol name="JobDatabase" filename="job_data_model.py" path="packages/database/job_data_model.py" startline="20" type="class"></mcsymbol> class for interacting with the job listings database.
- `models.py`: Defines other database schemas using SQLAlchemy ORM. This includes models for `JobApplication`, `UserProfile`, etc.
- `migrations/`: Contains database migration scripts (e.g., using Alembic) to manage schema changes over time.
- `database.py`: Provides utility functions for database connection, session management, and common CRUD operations.

## Usage

To interact with the database, you would typically import the necessary models and database utility functions:

```python
from packages.database import JobDatabase, JobListing
from datetime import datetime

# Example: Adding a new job listing
db = JobDatabase()
new_job_data = {
    "id": "unique_job_id_123",
    "title": "Software Engineer",
    "company": "Example Corp",
    "location": "Remote",
    "description": "Develop and maintain software.",
    "url": "https://example.com/job/123",
    "source": "LinkedIn",
    "posting_date": datetime.utcnow()
}
db.add_job_listing(new_job_data)

# Example: Searching for jobs
found_jobs = db.search_jobs(query="Software Engineer", location="Remote")
for job in found_jobs:
    print(f"Found: {job.title} at {job.company}")

# Example: Updating job status
job_to_update = db.get_job_by_id("unique_job_id_123")
if job_to_update:
    db.update_job_status(job_to_update.id, "Applied")
```

## Development Setup

1. **Install Dependencies**: Ensure you have SQLAlchemy and any chosen database drivers (e.g., `sqlite3` for SQLite, `psycopg2` for PostgreSQL) installed.
   ```bash
   pip install SQLAlchemy
   # pip install psycopg2-binary # if using PostgreSQL
   ```
2. **Database URL**: Configure your database connection string in `packages/config/settings.py`.
3. **Migrations**: If using Alembic, initialize and manage migrations:
   ```bash
   alembic init migrations
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

## Testing

Database interactions should be tested using a dedicated test database or an in-memory SQLite database to ensure isolation and repeatability. Mocking database calls can also be useful for unit testing components that interact with the database.

## Contributing

When contributing to the database package, please ensure:
- All new models are properly defined in `models.py` or <mcfile name="job_data_model.py" path="packages/database/job_data_model.py"></mcfile>.
- Corresponding migration scripts are created and tested.
- Database interactions are efficient and handle errors gracefully.
- Sensitive data is handled securely.