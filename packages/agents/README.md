# Agents Package

## Purpose
This package contains the core autonomous agents that make up the JobApplierAgent system. Each agent is responsible for a specific, well-defined task within the job application workflow, promoting modularity and reusability.

## Dependencies
Agents primarily depend on the `packages/common_types` for common data structures and may utilize functionalities from `packages/utilities` for tasks like parsing, file management, or browser automation.

## Key Components
- `resume_parser_agent.py`: Parses resume documents into structured data.
- `job_scraper_agent.py`: Scrapes job listings from various online sources.
- `job_processor_agent.py`: Cleans, normalizes, and extracts key information from raw job listings.
- `job_matcher_agent.py`: Matches job listings to a user's resume based on skills, experience, and preferences.
- `resume_enhancer_agent.py`: Provides suggestions for enhancing a resume to better match a specific job description.
- `cover_letter_generator_agent.py`: Generates customized cover letters for job applications.
- `ats_scorer_agent.py`: Calculates an ATS (Applicant Tracking System) compatibility score for a resume against a job description.
- `application_automation_agent.py`: Automates the submission of job applications.
- `application_tracker_agent.py`: Tracks the status of submitted job applications.
- `learning_agent.py`: Implements learning mechanisms to analyze application responses, learn from resume modifications, adapt job selection criteria, improve matching accuracy, and personalize application strategies.
- `reporting_agent.py`: Generates summaries, analytics, and alerts related to job applications.
- `scheduler_agent.py`: Manages the scheduling of automated tasks, such as daily job application runs.
- `unicorn_agent.py`: Handles magical tasks related to job applications.

## Core Agents
- **ResumeParserAgent**: Parses resume files to extract structured information.
- `JobScraperAgent`: Handles scraping job listings from various online sources based on user-defined criteria.
- `JobProcessorAgent`: Processes raw job listings to clean, normalize, and enrich the data into a standardized format.
- `JobMatcherAgent`: Matches processed job listings to the user's resume data, identifying the most relevant opportunities.
- `ResumeEnhancerAgent`: Enhances the user's resume based on a specific job description to improve ATS compatibility and relevance.
- `CoverLetterGeneratorAgent`: Generates a personalized cover letter based on resume data and job description.
- `ATSScorerAgent`: Scores the compatibility of a resume with a job description, simulating an ATS.
- `ApplicationAutomationAgent`: Automates the process of applying for jobs on various platforms.
- `JobTrackingAgent`: Manages the tracking and status updates of job applications.
- **JobApplierAgent**: The main orchestrator for the job application process.

## Usage Examples
Agents are typically initialized and orchestrated by the main `JobApplierAgent` application (`apps/job-applier-agent/src/main.py`).

Example of initializing an agent:
```python
from packages.agents.job_scraper_agent import JobScraperAgent

scraper = JobScraperAgent()
job_listings = scraper.scrape(job_roles=["Software Engineer"], locations={'remote': True})
```

## API Reference
Each agent class exposes methods relevant to its functionality. Refer to the individual agent files for detailed method signatures and documentation.

## Development Setup
No specific setup is required for this package beyond the general monorepo setup. Ensure all Python dependencies are installed as per the main application's `requirements.txt`.

## Testing
Unit tests for individual agents should be placed in `apps/job-applier-agent/tests/agents/`.

## Contributing
Refer to the main `README.md` in the monorepo root for general contribution guidelines.