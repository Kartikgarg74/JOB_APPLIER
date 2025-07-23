# Celery Tasks Module (`tasks.py`)

## Purpose
This module (`tasks.py`) defines the asynchronous tasks that are executed by Celery workers. These tasks handle long-running or resource-intensive operations, such as resume parsing, ATS score calculation, and the execution of the "Unicorn Agent," ensuring that the main application remains responsive.

## Dependencies
- `apps.job_applier_agent.src.celery_app.celery_app`: The Celery application instance to register tasks with.
- `packages.utilities.parsers.resume_parser.parse_resume`: Function for parsing resume files.
- `packages.agents.ats_scorer.ats_scorer_agent.ATSScorerAgent`: Class for calculating ATS scores.
- `os`, `shutil`, `logging`: Standard Python libraries for file operations, logging.
- `packages.config.user_profile.load_user_profile`, `save_user_profile`: Functions for managing user profile data.
- `packages.agents.unicorn_agent.unicorn_agent.UnicornAgent`: Class for the Unicorn Agent.
- `packages.database.config.get_db`: Function to get a database session.
- `packages.notifications.notification_service.NotificationService`: Class for sending notifications.

## Key Components

### `process_resume_upload_task`
- **Purpose**: An asynchronous task to process an uploaded resume file, extract its text content, and update the user's profile with this information.
- **Parameters**:
  - `file_path` (str): The path to the temporary resume file.
  - `file_content_type` (str): The MIME type of the resume file (e.g., `application/pdf`).
  - `user_profile_path` (str): The path to the user's profile data.
- **Workflow**:
  1. Calls `parse_resume` to extract text from the resume.
  2. If text is extracted, it loads the user profile, updates it with the resume text, and saves it.
  3. Logs success or error messages.
  4. Ensures the temporary resume file is cleaned up in a `finally` block.
- **Returns**: A dictionary indicating `status` ("success" or "error") and a `message`.

### `calculate_ats_score_task`
- **Purpose**: An asynchronous task to calculate an Applicant Tracking System (ATS) compatibility score between a resume and a job description.
- **Parameters**:
  - `resume_file_path` (str): The path to the temporary resume file.
  - `resume_content_type` (str): The MIME type of the resume file.
  - `job_description` (str): The text of the job description.
- **Workflow**:
  1. Parses the resume to get its text content.
  2. Initializes an `ATSScorerAgent`.
  3. Calls `score_resume` to get the ATS score.
  4. Logs success or error messages.
  5. Cleans up the temporary resume file.
- **Returns**: A dictionary indicating `status` ("success" or "error") and `ats_result` (if successful).

### `run_unicorn_agent_task`
- **Purpose**: An asynchronous task to execute the "Unicorn Agent," which likely performs complex, multi-step job application processes.
- **Parameters**:
  - `data` (dict): A dictionary containing necessary data for the Unicorn Agent, potentially including user profile information.
- **Workflow**:
  1. Obtains a database session.
  2. Initializes a `UnicornAgent` with the database session.
  3. Calls the `run` method of the `UnicornAgent`.
  4. Sends a success or failure notification to the user via `NotificationService`.
  5. Logs the task's progress and outcome.
  6. Includes error handling and optional task retry logic.
- **Returns**: A dictionary indicating `status` ("success" or "error"), a `message`, and `results` (if successful).

## Usage
These tasks are designed to be called asynchronously from other parts of the application (e.g., FastAPI endpoints) using Celery's `delay()` or `apply_async()` methods.

### Example: Calling a Task
```python
from packages.message_queue.tasks import process_resume_upload_task

# In your FastAPI endpoint or other application logic:
@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    # Save file temporarily
    temp_file_path = "/tmp/uploaded_resume.pdf"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Asynchronously process the resume
    process_resume_upload_task.delay(temp_file_path, file.content_type, "/path/to/user_profile.json")

    return {"message": "Resume upload initiated. Processing in background."}
```

## Error Handling and Retries
Each task includes `try...except` blocks for robust error handling, logging any exceptions that occur. The `run_unicorn_agent_task` also demonstrates how Celery's `retry` mechanism can be used to re-attempt failed tasks after a specified countdown.