# Unicorn Agent

## Purpose
The `UnicornAgent` orchestrates the end-to-end job application workflow, from parsing resumes and calculating ATS scores to matching jobs and automating application submissions. It integrates various specialized agents to provide a seamless and robust application process.

## Dependencies
- `packages.notifications.notification_service.NotificationService`: For sending email notifications.
- `packages.errors.custom_exceptions.UnicornError`: Custom exception for UnicornAgent specific errors.
- `packages.utilities.retry_utils.retry_with_exponential_backoff`: Utility for retrying operations with exponential backoff.
- `packages.agents.resume_parser.ResumeParserAgent`: For parsing resume data.
- `packages.agents.ats_scorer.ATSScorerAgent`: For calculating ATS scores.
- `packages.agents.job_matcher.JobMatcherAgent`: For matching user profiles with job postings.
- `packages.agents.application_automation.ApplicationAutomationAgent`: For automating job application submissions.
- `logging`: For logging operational information and errors.

## Key Components
- `UnicornAgent` class: The main orchestrator.
  - `__init__(self, db)`: Initializes the agent with a database connection and NotificationService.
  - `run(self, data: dict) -> dict`: The core asynchronous method that executes the job application workflow. It takes `user_profile` and `job_posting` data as input.
  - `_send_error_notification`: An internal helper function to centralize error notification sending.

## Workflow Steps
The `run` method executes the following steps sequentially, with retry mechanisms and error notifications for each:
1. **Parse Resume**: Uses `ResumeParserAgent` to parse the user's resume data.
2. **ATS Scoring**: Uses `ATSScorerAgent` to calculate an ATS score based on the parsed resume and job posting.
3. **Job Matching**: Uses `JobMatcherAgent` to determine the compatibility between the user's profile and the job posting.
4. **Application Automation**: Uses `ApplicationAutomationAgent` to automate the submission of the job application.

## Error Handling
Each step in the workflow is wrapped in a `try-except` block with `retry_with_exponential_backoff` to ensure robustness. Errors are logged and critical failures trigger notifications via `_send_error_notification`.

## Usage Examples
```python
import asyncio
import logging
from packages.agents.unicorn_agent.unicorn_agent import UnicornAgent

# Assume 'db' is an initialized database connection object
# Assume 'user_profile_data' and 'job_posting_data' are prepared dictionaries

async def main():
    logging.basicConfig(level=logging.INFO)
    unicorn_agent = UnicornAgent(db=None) # Replace None with actual db connection
    data = {
        "user_profile": {
            "email": "user@example.com",
            "resume_data": "base64_encoded_resume_content",
            # ... other user profile details
        },
        "job_posting": {
            "title": "Software Engineer",
            "description": "Job description content",
            # ... other job posting details
        }
    }
    try:
        result = await unicorn_agent.run(data)
        print("Unicorn Agent workflow completed successfully:", result)
    except Exception as e:
        print(f"Unicorn Agent workflow failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Development Setup
To set up the `UnicornAgent` for development, ensure all its dependencies are installed. The agent requires a database connection and proper configuration for the `NotificationService`.

## Testing
Testing involves mocking external agent calls and verifying the orchestration logic, error handling, and notification triggers for each step of the workflow.