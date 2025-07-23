# Application Automation Agent

## Purpose
The `ApplicationAutomationAgent` automates the process of applying for jobs on various online platforms. It is designed to programmatically fill out application forms and submit resumes and cover letters, handling different application systems like Workday and Greenhouse, as well as providing a generic fallback for other platforms.

## Dependencies
- `playwright`: A Python library for browser automation, used to interact with web pages.
- `packages.utilities.retry_utils.retry_with_exponential_backoff`: For robust retries of application attempts.
- `packages.agents.application_automation.application_automation_utils.load_user_data`: Utility to load user-specific data required for filling out applications.
- `logging`: For logging operational information and errors.

## Key Components
- `ApplicationAutomationAgent` class: The main agent responsible for automation.
  - `__init__(self, db)`: Initializes the agent with a database connection.
  - `apply_for_job(self, job_data: Dict[str, Any], resume_path: str, cover_letter_path: str) -> bool`: The core method that orchestrates the job application process. It navigates to the job URL and dispatches to platform-specific handlers.
  - `_handle_workday_application(self, page: Any, job_data: Dict[str, Any], resume_path: str, cover_letter_path: str) -> bool`: Handles application submission on Workday platforms.
  - `_handle_greenhouse_application(self, page: Any, job_data: Dict[str, Any], resume_path: str, cover_letter_path: str) -> bool`: Handles application submission on Greenhouse platforms.
  - `_handle_generic_application(self, page: Any, job_data: Dict[str, Any], resume_path: str, cover_letter_path: str) -> bool`: Provides a fallback for generic application forms by attempting to fill common fields and upload documents.

## Workflow
1. The `apply_for_job` method is called with job details, resume path, and cover letter path.
2. It launches a headless browser (using Playwright) and navigates to the job URL.
3. Based on the URL, it identifies the application platform (e.g., Workday, Greenhouse) and calls the appropriate handler method.
4. Each handler method contains logic to interact with the specific platform's forms and elements to fill in user data and upload documents.
5. A generic handler is available for platforms not explicitly supported, attempting to fill common input fields.

## Usage Examples
```python
import asyncio
import logging
from packages.agents.application_automation.application_automation_agent import ApplicationAutomationAgent

# Assume 'db' is an initialized database connection object
# Assume 'job_data', 'resume_file_path', and 'cover_letter_file_path' are prepared

async def main():
    logging.basicConfig(level=logging.INFO)
    automation_agent = ApplicationAutomationAgent(db=None) # Replace None with actual db connection

    job_data = {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "url": "https://example.workday.com/job/123"
    }
    resume_file_path = "/path/to/your/resume.pdf"
    cover_letter_file_path = "/path/to/your/cover_letter.pdf"

    try:
        success = automation_agent.apply_for_job(job_data, resume_file_path, cover_letter_file_path)
        if success:
            print("Job application submitted successfully!")
        else:
            print("Job application failed.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Development Setup
To set up the `ApplicationAutomationAgent` for development, you need to install Playwright and its browser dependencies. Ensure you have the necessary user data loaded for testing form submissions.

## Testing
Testing involves mocking browser interactions and verifying that the agent correctly identifies platforms, fills forms, and handles file uploads. It's crucial to test against various real-world application forms to ensure robustness.