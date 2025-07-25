# JobApplierAgent Monorepo

This monorepo contains the complete autonomous agent for automating the job application process.

## Project Structure

```
project-root/
├── apps/                    # Application packages
│   └── job-applier-agent/   # Main application orchestrating the workflow
├── packages/                # Shared packages
│   ├── agents/              # Core agent implementations
│   ├── utilities/           # Shared utility functions and classes
│   ├── types/               # Shared type definitions
│   ├── config/              # Shared configurations (e.g., user_profile.json)
│   └── database/            # Database schemas and migrations
├── tools/                   # Development tools and scripts
├── docs/                    # Documentation
└── README.md                # Root documentation
```

## Setup and Installation

1.  **Clone the repository**:

    ```bash
    git clone <repository_url>
    cd JOB APPLIER
    ```

2.  **Configure User Profile**:

    Edit the `packages/config/user_profile.json` file with your preferred job roles, location preferences, resume path, skill keywords, and ATS scoring weights.

    ```json
    {
      "preferred_job_roles": [
        "Software Engineer",
        "Data Scientist",
        "DevOps Engineer"
      ],
      "location_preferences": {
        "remote": true,
        "hybrid": false,
        "on_site": [
          "New York, NY",
          "San Francisco, CA"
        ]
      },
      "resume_path": "/path/to/your/resume.pdf",
      "cover_letter_template": "/path/to/your/cover_letter_template.txt",
      "skill_keywords": [
        "Python",
        "Machine Learning",
        "Cloud Computing",
        "React",
        "Docker"
      ],
      "ats_scoring_weights": {
        "keywords_match": 0.4,
        "experience_match": 0.3,
        "skills_match": 0.2,
        "education_match": 0.1
      }
    }
    ```

3.  **Install Dependencies**:

    Navigate to the `apps/job-applier-agent` directory and install the required Python packages.

    ```bash
    pip install -r requirements.txt
    ```

## Running the Agent

Further instructions on running the agent will be provided in `apps/job-applier-agent/README.md`.

## Documentation

Refer to the `docs/` directory for detailed architecture and API references.

## Message Queue (Celery + Redis)

### Running Redis (Docker Compose)
```
docker-compose up redis
```

### Running Celery Workers
```
celery -A packages.message_queue.celery_app worker --loglevel=info
```

### Running Celery Beat (for scheduled jobs)
```
celery -A packages.message_queue.celery_app beat --loglevel=info
```

### Running Flower (Monitoring Dashboard)
```
flower -A packages.message_queue.celery_app --port=5555
```

### Example: Sending a Task
```python
from packages.message_queue.tasks import send_email_task
send_email_task.delay("user@example.com", "Welcome!", "Thanks for signing up.")
```

- Failed tasks are sent to the dead letter queue after max retries.
- Rate limiting, prioritization, and retry logic are built-in.
- Periodic jobs (e.g., file cleanup) are scheduled via Celery Beat.
