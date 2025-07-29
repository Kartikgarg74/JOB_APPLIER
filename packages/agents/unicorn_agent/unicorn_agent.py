import logging
from packages.notifications.notification_service import NotificationService
from sqlalchemy.orm import Session
from packages.errors.custom_exceptions import UnicornError
from packages.utilities.retry_utils import retry_with_exponential_backoff
from packages.agents.resume_parser.resume_parser_agent import ResumeParserAgent
from packages.agents.ats_scorer.ats_scorer_agent import ATSScorerAgent
from packages.agents.job_matcher.job_matcher_agent import JobMatcherAgent
from packages.agents.application_automation.application_automation_agent import ApplicationAutomationAgent
from packages.agents.cover_letter_generator.cover_letter_generator_agent import CoverLetterGeneratorAgent
import asyncio
from typing import List
import logging
logger = logging.getLogger(__name__)

class UnicornAgent:
    """UnicornAgent handles magical tasks related to job applications.
    [BATCH] Supports parallel processing of multiple job applications via run_batch().
    """

    GEMINI_SYSTEM_PROMPT = """
You are a highly capable, production-grade Job Application Agent powered by Gemini 2.5 Flash. Your core responsibility is to automate and optimize the job search and application process for users by intelligently analyzing resumes, matching them to job postings, and executing applications, even under unreliable network conditions or API failures.

Your capabilities include:
- Parsing structured resume data from raw text or uploaded files.
- Scraping and semantically analyzing job descriptions.
- Matching candidate profiles to job roles using vector similarity and contextual reasoning.
- Scoring job fit using ATS standards and keyword density.
- Generating tailored, concise, and ATS-optimized cover letters.
- Submitting applications autonomously with robust error handling and fallback strategies.

### Behavior Rules:
1. **Resilience First**: Handle API fetch errors using retries (max 3), cache fallback, or graceful degradation. Never crash or produce null outputs.
2. **High Match Accuracy**: Prioritize context-aware matching — match by job title, skills, tools, experience, and domain.
3. **Personalization**: Adapt tone and content based on job level, company type, and role description.
4. **Structured Output**: Always respond with structured JSON that can be directly used by the backend or frontend services.
5. **Security & Privacy**: Never log or leak any personal user data. All data is transient and context-bound.

### Input:
You may receive:
- `resume_content`: Plaintext or parsed JSON
- `job_description`: Full job listing
- `user_preferences`: Location, role, domain, work mode, etc.
- `system_state`: Retry count, cached matches, or error flags

### Output Schema (JSON):
```json
{
  "job_match_score": 87.4,
  "ats_score": 92.1,
  "matched_keywords": ["Python", "FastAPI", "LLMs", "Celery"],
  "missing_keywords": ["Docker", "CI/CD"],
  "cover_letter": "Dear Hiring Manager, I am excited to apply for...",
  "application_status": "submitted | retrying | failed_gracefully",
  "error_handling": {
    "retry_attempts": 2,
    "fallback_used": true,
    "last_known_issue": "fetch_error"
  }
}
```

### Execution Logic:

* Always validate inputs before processing.
* If job description is missing, return a response indicating insufficient data.
* If resume is unstructured, use NLP to extract sections (skills, education, experience).
* Prioritize roles with ≥80% skill match and above-average ATS score.
* On repeated fetch errors, use cached job listings or notify user via output flag.

You are an expert job applier — fast, intelligent, resilient. Think like a recruiter, act like an agent.
"""

    def __init__(self, db: Session,
                 resume_parser_agent: ResumeParserAgent,
                 ats_scorer_agent: ATSScorerAgent,
                 job_matcher_agent: JobMatcherAgent,
                 application_automation_agent: ApplicationAutomationAgent,
                 cover_letter_generator_agent: CoverLetterGeneratorAgent):
        # [CONTEXT] Initializes the UnicornAgent with its dependencies.
        self.db = db
        self.notification_service = NotificationService(db_session=self.db)
        self.resume_parser_agent = resume_parser_agent
        self.ats_scorer_agent = ats_scorer_agent
        self.job_matcher_agent = job_matcher_agent
        self.application_automation_agent = application_automation_agent
        self.cover_letter_generator_agent = cover_letter_generator_agent
        logger.info("UnicornAgent initialized.")

    async def run(self, data: dict, progress_callback=None, workflow_config=None) -> dict:
        # [CONTEXT] Orchestrates the magical operations of the UnicornAgent.
        logger.info(f"UnicornAgent received data: {data}")
        try:
            user_profile = data.get("user_profile")
            job_posting = data.get("job_posting")

            if not user_profile or not job_posting:
                raise UnicornError("Missing user profile or job posting data.")

            # Default config: run all steps
            default_config = {
                'parse_resume': True,
                'ats_scoring': True,
                'job_matching': True,
                'application_automation': True
            }
            if workflow_config is None:
                workflow_config = default_config
            else:
                # Fill in missing keys with defaults
                for k, v in default_config.items():
                    if k not in workflow_config:
                        workflow_config[k] = v

            async def _send_error_notification(recipient, subject, error_message, details=None):
                await self.notification_service.send_notification(
                    recipient=recipient,
                    message=error_message,
                    notification_type="email",
                    details={"subject": subject, "error": str(error_message), **(details if details else {})}
                )

            def update_progress(step, percent):
                msg = f"Step: {step}, {percent}% complete"
                logger.info(msg)
                if progress_callback:
                    progress_callback(step, percent)

            parsed_resume = None
            ats_score_result = None
            job_match_result = None
            application_result = None

            # Step 1: Parse Resume
            if workflow_config.get('parse_resume', True):
                update_progress("parse_resume", 10)
                @retry_with_exponential_backoff(max_retries=3, initial_delay=1, errors=(Exception,))
                async def parse_resume_with_retry(resume_data):
                    return await self.resume_parser_agent.run(resume_data)
                try:
                    parsed_resume = await parse_resume_with_retry(user_profile.get("resume_data"))
                    logger.info("Resume parsed successfully.")
                    update_progress("parse_resume", 25)
                    await self.notification_service.send_notification(
                        recipient=user_profile.get("email"),
                        message="Your resume has been successfully parsed.",
                        notification_type="email",
                        details={"subject": "Resume Parsing Success"}
                    )
                except Exception as e:
                    logger.error(f"Resume parsing failed: {e}", exc_info=True)
                    await _send_error_notification(
                        recipient=user_profile.get("email"),
                        subject="Resume Parsing Failed",
                        error_message=f"Failed to parse your resume: {e}"
                    )
                    update_progress("parse_resume", 100)
                    raise UnicornError(f"Resume parsing failed: {e}")
            else:
                update_progress("parse_resume", 100)

            # Step 2: ATS Scoring
            if workflow_config.get('ats_scoring', True):
                update_progress("ats_scoring", 30)
                @retry_with_exponential_backoff(max_retries=3, initial_delay=1, errors=(Exception,))
                async def ats_score_with_retry(parsed_resume_data, job_posting_data):
                    return await self.ats_scorer_agent.run(parsed_resume_data, job_posting_data)
                try:
                    ats_score_result = await ats_score_with_retry(parsed_resume, job_posting)
                    logger.info("ATS scoring completed.")
                    update_progress("ats_scoring", 50)
                    await self.notification_service.send_notification(
                        recipient=user_profile.get("email"),
                        message=f"Your resume received an ATS score of {ats_score_result.get('score')}",
                        notification_type="email",
                        details={"subject": "ATS Scoring Complete", "score": ats_score_result.get('score')}
                    )
                except Exception as e:
                    logger.error(f"ATS scoring failed: {e}", exc_info=True)
                    await _send_error_notification(
                        recipient=user_profile.get("email"),
                        subject="ATS Scoring Failed",
                        error_message=f"Failed to perform ATS scoring: {e}"
                    )
                    update_progress("ats_scoring", 100)
                    raise UnicornError(f"ATS scoring failed: {e}")
            else:
                update_progress("ats_scoring", 100)

            # Step 3: Job Matching
            if workflow_config.get('job_matching', True):
                update_progress("job_matching", 55)
                @retry_with_exponential_backoff(max_retries=3, initial_delay=1, errors=(Exception,))
                async def job_match_with_retry(user_profile_data, job_posting_data):
                    return await self.job_matcher_agent.run(user_profile_data, job_posting_data)
                try:
                    job_match_result = await job_match_with_retry(user_profile, job_posting)
                    logger.info("Job matching completed.")
                    update_progress("job_matching", 75)
                    await self.notification_service.send_notification(
                        recipient=user_profile.get("email"),
                        message=f"Found {len(job_match_result)} matching jobs.",
                        notification_type="email",
                        details={"subject": "Job Matching Complete", "matches": job_match_result}
                    )
                except Exception as e:
                    logger.error(f"Job matching failed: {e}", exc_info=True)
                    await _send_error_notification(
                        recipient=user_profile.get("email"),
                        subject="Job Matching Failed",
                        error_message=f"Failed to perform job matching: {e}"
                    )
                    update_progress("job_matching", 100)
                    raise UnicornError(f"Job matching failed: {e}")
            else:
                update_progress("job_matching", 100)

            # Step 4: Generate Cover Letter
            cover_letter_content = None
            if workflow_config.get('generate_cover_letter', True):
                update_progress("generate_cover_letter", 80)
                @retry_with_exponential_backoff(max_retries=3, initial_delay=1, errors=(Exception,))
                async def generate_cover_letter_with_retry(resume_data, job_description):
                    return self.cover_letter_generator_agent.generate_cover_letter(resume_data, job_description)
                try:
                    cover_letter_content = await generate_cover_letter_with_retry(parsed_resume, job_posting.get("description"))
                    logger.info("Cover letter generated successfully.")
                    update_progress("generate_cover_letter", 90)
                    await self.notification_service.send_notification(
                        recipient=user_profile.get("email"),
                        message="Your cover letter has been generated.",
                        notification_type="email",
                        details={"subject": "Cover Letter Generated"}
                    )
                except Exception as e:
                    logger.error(f"Cover letter generation failed: {e}", exc_info=True)
                    await _send_error_notification(
                        recipient=user_profile.get("email"),
                        subject="Cover Letter Generation Failed",
                        error_message=f"Failed to generate cover letter: {e}"
                    )
                    update_progress("generate_cover_letter", 100)
                    raise UnicornError(f"Cover letter generation failed: {e}")
            else:
                update_progress("generate_cover_letter", 100)

            # Step 5: Application Automation (if enabled)
            if workflow_config.get('application_automation', True):
                update_progress("application_automation", 95)
                @retry_with_exponential_backoff(max_retries=3, initial_delay=1, errors=(Exception,))
                async def apply_job_with_retry(job_data, resume_data, cover_letter):
                    return await self.application_automation_agent.run(job_data, resume_data, cover_letter)
                try:
                    application_result = await apply_job_with_retry(job_posting, parsed_resume, cover_letter_content)
                    logger.info("Job application automated successfully.")
                    update_progress("application_automation", 100)
                    await self.notification_service.send_notification(
                        recipient=user_profile.get("email"),
                        message="Your job application has been submitted.",
                        notification_type="email",
                        details={"subject": "Job Application Submitted"}
                    )
                except Exception as e:
                    logger.error(f"Job application automation failed: {e}", exc_info=True)
                    await _send_error_notification(
                        recipient=user_profile.get("email"),
                        subject="Job Application Failed",
                        error_message=f"Failed to automate job application: {e}"
                    )
                    update_progress("application_automation", 100)
                    raise UnicornError(f"Job application automation failed: {e}")
            else:
                update_progress("application_automation", 100)

            return {
                "parsed_resume": parsed_resume,
                "ats_score_result": ats_score_result,
                "job_match_result": job_match_result,
                "cover_letter": cover_letter_content,
                "application_result": application_result,
                "status": "success"
            }

        except UnicornError as ue:
            logger.error(f"Unicorn workflow failed: {ue}")
            return {"status": "failed", "error": str(ue)}
        except Exception as e:
            logger.error(f"An unexpected error occurred in Unicorn workflow: {e}", exc_info=True)
            return {"status": "failed", "error": f"An unexpected error occurred: {e}"}

    async def run_batch(self, data_list: List[dict], progress_callback=None, workflow_config=None) -> List[dict]:
        """
        Processes multiple job applications in parallel.
        Each item in batch_data should be a dict as expected by run().
        Returns a list of results, one per job application.
        Progress tracking is logged for each job and can be reported via progress_callback.
        workflow_config can be used to customize which steps to run/skip for all jobs.
        """
        total = len(data_list)
        results = [None] * total

        async def run_with_progress(idx, data):
            def batch_progress_callback(step, percent):
                logger.info(f"[Job {idx+1}/{total}] {percent}%: {step}")
                if progress_callback:
                    progress_callback(idx, step, percent)
            try:
                result = await self.run(data, progress_callback=batch_progress_callback, workflow_config=workflow_config)
                results[idx] = result
            except Exception as e:
                results[idx] = {"status": "failure", "error": str(e)}
                batch_progress_callback("error", 100)

        tasks = [run_with_progress(i, data) for i, data in enumerate(data_list)]
        await asyncio.gather(*tasks)
        logger.info("Batch processing completed.")
        return results


if __name__ == "__main__":

    from packages.utilities.logging_utils import setup_logging
    from packages.database.config import get_db
    from packages.common_types.common_types import UserProfile, ResumeData

    import json

    setup_logging()

    # Initialize agents (dummy instances for testing)
    class MockResumeParserAgent:
        async def run(self, resume_data):
            logger.info("MockResumeParserAgent: Parsing resume...")
            return {"text": "parsed resume content", "skills": ["Python", "SQL"]}

    class MockATSScorerAgent:
        async def run(self, resume_data, job_description):
            logger.info("MockATSScorerAgent: Scoring ATS...")
            return {"score": 85, "keywords": ["Python", "SQL"]}

    class MockJobMatcherAgent:
        async def run(self, user_profile_data, job_posting_data):
            logger.info("MockJobMatcherAgent: Matching jobs...")
            return [{"title": "Software Engineer", "compatibility_score": 90}]

    class MockApplicationAutomationAgent:
        async def run(self, job_data, resume_data, cover_letter):
            logger.info("MockApplicationAutomationAgent: Automating application...")
            return {"status": "submitted", "platform": "LinkedIn"}

    class MockCoverLetterGeneratorAgent:
        def generate_cover_letter(self, resume_data, job_description):
            logger.info("MockCoverLetterGeneratorAgent: Generating cover letter...")
            return "Dear Hiring Manager, This is a mock cover letter."

    mock_resume_parser = MockResumeParserAgent()
    mock_ats_scorer = MockATSScorerAgent()
    mock_job_matcher = MockJobMatcherAgent()
    mock_application_automation = MockApplicationAutomationAgent()
    mock_cover_letter_generator = MockCoverLetterGeneratorAgent()

    # Mock DB session
    class MockDBSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def query(self, *args, **kwargs):
            return self

        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return UserProfile(id=1, email="test@example.com", preferences={"tone": "formal"})

        def add(self, *args, **kwargs):
            pass

        def commit(self):
            pass

        def refresh(self, *args, **kwargs):
            pass

    db_session = MockDBSession()

    unicorn_agent = UnicornAgent(
        db=db_session,
        resume_parser_agent=mock_resume_parser,
        ats_scorer_agent=mock_ats_scorer,
        job_matcher_agent=mock_job_matcher,
        application_automation_agent=mock_application_automation,
        cover_letter_generator_agent=mock_cover_letter_generator
    )

    # Dummy data for testing
    dummy_user_profile = {
        "email": "test@example.com",
        "resume_data": {"raw_text": "My resume content..."},
        "preferences": {"tone": "formal", "domain": "tech"}
    }
    dummy_job_posting = {
        "title": "Software Engineer",
        "description": "We are looking for a skilled software engineer...",
        "url": "http://example.com/job"
    }

    async def main():
        logger.info("Running single job application workflow...")
        result = await unicorn_agent.run(
            data={
                "user_profile": dummy_user_profile,
                "job_posting": dummy_job_posting
            },
            workflow_config={
                'parse_resume': True,
                'ats_scoring': True,
                'job_matching': True,
                'generate_cover_letter': True,
                'application_automation': True
            }
        )
        logger.info(f"Single job application result: {json.dumps(result, indent=2)}")

        logger.info("\nRunning batch job application workflow...")
        batch_data = [
            {
                "user_profile": dummy_user_profile,
                "job_posting": dummy_job_posting
            },
            {
                "user_profile": dummy_user_profile,
                "job_posting": {
                    "title": "Data Scientist",
                    "description": "Seeking a data scientist with ML skills...",
                    "url": "http://example.com/data_job"
                }
            }
        ]
        batch_results = await unicorn_agent.run_batch(
            data_list=batch_data,
            workflow_config={
                'parse_resume': True,
                'ats_scoring': True,
                'job_matching': True,
                'generate_cover_letter': True,
                'application_automation': True
            }
        )
        logger.info(f"Batch job application results: {json.dumps(batch_results, indent=2)}")

    asyncio.run(main())
