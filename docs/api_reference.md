# Job Applier Agent API Reference

Base URL: `/v1`

---

## Authentication

### POST `/v1/auth/register`
- **Summary:** Register a new user (password or Google OAuth).
- **Request Body:**
  - `username` (str, required)
  - `email` (str, required)
  - `password` (str, optional)
  - `google_id` (str, optional)
  - `image` (str, optional)
- **Response:**
  - User object
- **Errors:**
  - 400: Invalid input, both password and Google ID provided, or neither provided
  - 409: Username or Google ID already exists

### POST `/v1/auth/login`
- **Summary:** Authenticate user (with optional 2FA).
- **Request Body:**
  - `username` (str, required)
  - `password` (str, required)
  - `two_fa_code` (str, optional)
- **Response:**
  - User object + JWT token

### POST `/v1/auth/google`
- **Summary:** Google OAuth login/register.
- **Request Body:**
  - `id_token` (str, required)
- **Response:**
  - User object + JWT token

### POST `/v1/auth/refresh`
- **Summary:** Refresh JWT token.
- **Request Body:**
  - `refresh_token` (cookie)
- **Response:**
  - New JWT token

### POST `/v1/auth/logout`
- **Summary:** Logout and revoke refresh token.

### POST `/v1/auth/request-password-reset`
- **Summary:** Request password reset email.
- **Request Body:**
  - `email` (str, required)

### POST `/v1/auth/reset-password`
- **Summary:** Reset password using token.
- **Request Body:**
  - `token` (str, required)
  - `new_password` (str, required)

---

## Jobs & Applications

### POST `/v1/apply-job`
- **Summary:** Apply for a job using the Unicorn Agent.
- **Request Body:**
  - `user_profile` (object)
  - `job_posting` (object)
- **Response:**
  - `{ "status": "processing", "message": "...", "task_id": "..." }`

### POST `/v1/upload-resume`
- **Summary:** Upload a resume file (PDF or DOCX).
- **Request:**
  - Multipart/form-data: `file` (PDF/DOCX, max 5MB)
- **Response:**
  - `{ "status": "success", "message": "...", "path": "..." }`

### POST `/v1/ats-score`
- **Summary:** Calculate ATS score for a resume and job description.
- **Request:**
  - Multipart/form-data: `resume_file` (PDF/DOCX), `job_description` (str)
- **Response:**
  - `{ "status": "success", "message": "...", "task_id": "..." }`

### POST `/v1/apply-for-job`
- **Summary:** Apply for a job using the Application Automation Agent.
- **Request:**
  - Form: `job_posting_url` (str)
- **Response:**
  - Status object

### POST `/v1/job-search`
- **Summary:** Search jobs from multiple job boards.
- **Request Body:**
  - `query` (str), `location` (str), `num_results` (int)
- **Response:**
  - `{ "jobs": [ ... ] }`

---

## Notifications

### GET `/v1/notifications/{user_id}`
- **Summary:** Get in-app notifications for a user.
- **Query Params:**
  - `limit` (int), `offset` (int)
- **Response:**
  - List of notifications

### POST `/v1/notifications/{notification_id}/mark-read`
- **Summary:** Mark a notification as read.

### DELETE `/v1/notifications/{notification_id}`
- **Summary:** Delete a notification.

---

## Workflow Management (Agent Orchestration Service)

### GET `/v1/workflow/status`
- **Summary:** Get the current status of the main workflow.
- **Response:**
  - `{ "is_running": true, "last_state_change": 1678886400.0 }`

### PUT `/v1/workflow/status`
- **Summary:** Update the status of the main workflow (e.g., pause or resume).
- **Request Body:**
  - `{ "is_running": false }`
- **Response:**
  - The updated status object.

---

## Configuration

### GET `/v1/config`
- **Summary:** Get current configuration settings.

### PUT `/v1/config`
- **Summary:** Update a configuration setting.
- **Request Body:**
  - `config_key` (str), `config_value` (any)

---

## Health & Metrics

### GET `/v1/health`
- **Summary:** Health check for the service.

### GET `/metrics`
- **Summary:** Prometheus metrics endpoint (not under `/v1`).

---

## Analytics

### POST `/v1/analytics/event`
- **Summary:** Track a custom analytics event.
- **Request Body:**
  - `event_name` (str), `user_id` (int), `properties` (dict)

---

## Miscellaneous

### POST `/v1/document/process`
- **Summary:** Process a document (resume, PDF, image).
- **Request:**
  - Multipart/form-data: `file`, `type` (str)
- **Response:**
  - `{ "status": "...", "text": "...", "metadata": {...}, "message": "..." }`

### POST `/v1/location/autocomplete`
- **Summary:** Address autocomplete (stub).
- **Request Body:**
  - `query` (str)
- **Response:**
  - `{ "suggestions": [ ... ] }`

### POST `/v1/calendar/connect`
- **Summary:** Connect calendar (Google/Outlook) - stub.
- **Request Body:**
  - `provider` (str), `user_id` (int)

---

## Error Handling

- All endpoints return structured error responses:
  - `{ "message": "Error message", "details": { ... } }`
- Common error codes: 400, 401, 404, 409, 422, 429, 500

---

## Live API Docs

- [Swagger UI (local)](http://localhost:8000/docs)
- [ReDoc (local)](http://localhost:8000/redoc)
