# JobApplierAgent Application

## Purpose
This is the main application for the JobApplierAgent, an autonomous agent designed to streamline the job application process. It orchestrates various sub-agents to perform deep job searches, scrape listings, match jobs to a resume, enhance resumes, apply to jobs automatically, track applications, provide ATS scores, and generate customized cover letters.

## Dependencies
This application depends on the shared packages within this monorepo, specifically:
- `packages/agents`: Contains the core logic for each specialized agent (e.g., `ResumeParserAgent`, `JobScraperAgent`).
- `packages/utilities`: Provides common utilities such as parsers, file management, vector matching, and browser automation.
- `packages/common_types`: Defines common data structures and types used across the application.
- `packages/config`: Handles application settings and user profile loading.

External Python dependencies are listed in `requirements.txt`.

## Key Components
- `main.py`: The entry point of the application, responsible for initializing and orchestrating the various agents.
- `requirements.txt`: Lists all Python dependencies required for this application.
- `src/`: Contains the source code for the main application logic.
- `tests/`: Contains unit and integration tests for the application.

## Usage Examples
To run the JobApplierAgent, navigate to the monorepo root directory and execute:

```bash
python apps/job-applier-agent/src/main.py
```

Before running, ensure you have configured your `user_profile.json` and installed all dependencies.

## API Endpoints

- `POST /v1/apply-job`: Initiates the job application workflow using the Unicorn Agent.
- `POST /v1/upload-resume`: Uploads a resume file (PDF or DOCX) for processing and user profile update.
- `GET /v1/notifications/{user_id}`: Retrieves a list of in-app notifications for a specific user.
- `POST /v1/notifications/{notification_id}/mark-read`: Marks a specific in-app notification as read.
- `DELETE /v1/notifications/{notification_id}`: Deletes a specific in-app notification.

## Development Setup
1. Ensure you have Python 3.8+ installed.
2. Navigate to the `apps/job-applier-agent` directory.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure your `user_profile.json` in `packages/config/` is set up correctly.

## Testing
To run tests for this application:

```bash
# Navigate to the monorepo root
pytest apps/job-applier-agent/tests/
```

## Contributing
Refer to the main `README.md` in the monorepo root for general contribution guidelines.