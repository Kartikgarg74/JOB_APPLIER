# Agent Orchestra Service

This service is responsible for coordinating job matching, recommendations, and application automation within the Job Applier platform.

## Features

- **Job Matching**: Implements a job matching algorithm based on user preferences and ATS scores.
- **Personalized Recommendations**: Provides personalized job recommendations using collaborative filtering.
- **Scheduled Matching**: Schedules daily job matching for active users.
- **Notifications**: Sends notifications for high-match jobs (>80% score).
- **Trend Analysis**: Includes job trend analysis and salary insights.
- **Supabase Integration**: Stores matching results in Supabase for dashboard display.

## Technologies Used

- FastAPI
- Celery (for background tasks)
- Redis (as Celery broker and backend)
- Supabase (for data storage)

## Setup and Installation

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/your-repo/job-applier.git
    cd job-applier
    ```

2.  **Navigate to the service directory**:

    ```bash
    cd apps/agent_orchestra_service
    ```

3.  **Create a virtual environment** (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

4.  **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

5.  **Environment Variables**:

    Ensure you have `REDIS_URL` configured in your environment or `.env` file if running locally. For production, configure it in your deployment environment (e.g., Render).

    Example `.env` file:

    ```
    REDIS_URL="redis://localhost:6379/0"
    ```

6.  **Run Redis**: Make sure a Redis instance is running and accessible.

## Running the Service

### FastAPI Application

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Celery Worker

In a separate terminal, start the Celery worker:

```bash
celery -A src.main.celery_app worker --loglevel=info
```

## API Endpoints

-   **GET /health**: Checks the health of the service.
-   **POST /match_jobs/{user_id}**: Initiates a job matching task for a given user.
    -   **Body**: `UserPreferences` (JSON object with `location`, `role`, `domain`, `work_mode`)
-   **GET /recommendations/{user_id}**: Retrieves personalized job recommendations for a user.
-   **GET /job_trends**: Provides job trend analysis and salary insights.

## Development Notes

-   **TODO**: Implement the actual job matching algorithm, integrate with `JOB_SCRAPER`, `ATS_SERVICE`, and `USER_SERVICE`.
-   **TODO**: Implement collaborative filtering for recommendations.
-   **TODO**: Set up scheduled tasks for daily matching.
-   **TODO**: Integrate with a notification service for high-match jobs.
-   **TODO**: Implement Supabase integration for storing and retrieving matching results.