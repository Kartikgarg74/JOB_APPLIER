# Job Applier Service

This service automates the job application process using browser automation (Selenium) and AI-powered cover letter generation.

## Features

- Automated application submission on platforms like Indeed, LinkedIn, and Glassdoor.
- Personalized cover letter generation using GPT/Gemini API.
- Handling of various application forms and required fields.
- Rate limiting and human-like delays to avoid detection.
- CAPTCHA detection and alerts for manual intervention.
- Storage of application status and tracking in Supabase.
- Application analytics and success rate tracking.

## Technologies Used

- FastAPI: Web framework for building the API.
- Selenium WebDriver: For browser automation.
- Python: Programming language.
- GPT/Gemini API: For cover letter generation (TODO).
- Supabase: For database storage (TODO).

## Setup

1.  **Clone the repository**:

    ```bash
    git clone <repository_url>
    cd job-applier/apps/job_applier_service
    ```

2.  **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3.  **ChromeDriver Setup**:

    Ensure you have ChromeDriver installed and accessible in your system's PATH, or specify its path in `src/main.py`.

4.  **Environment Variables**:

    Create a `.env` file in the root of this service and add any necessary environment variables (e.g., API keys for GPT/Gemini).

    ```
    # Example .env content
    # GEMINI_API_KEY=your_gemini_api_key
    ```

5.  **Run the application**:

    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000
    ```

## API Endpoints

-   `GET /health`: Health check endpoint.
-   `POST /apply`: Submit a job application request.
-   `GET /status/{application_id}`: Get the status of a specific job application.
-   `GET /analytics`: Get application analytics and success rates.

## TODOs

-   Integrate with GPT/Gemini API for cover letter generation.
-   Implement platform-specific application logic for Indeed, LinkedIn, Glassdoor.
-   Add robust CAPTCHA detection and manual intervention alerts.
-   Integrate with Supabase for persistent storage of application statuses and analytics.
-   Refine application analytics and success rate tracking.