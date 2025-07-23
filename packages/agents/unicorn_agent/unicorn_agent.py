import logging
from packages.notifications.notification_service import NotificationService
from sqlalchemy.orm import Session
import time
from packages.errors.custom_exceptions import UnicornError
from packages.utilities.retry_utils import retry_with_exponential_backoff
from packages.agents.resume_parser.resume_parser_agent import ResumeParserAgent
from packages.agents.ats_scorer.ats_scorer_agent import ATSScorerAgent
from packages.agents.job_matcher.job_matcher_agent import JobMatcherAgent
from packages.agents.application_automation.application_automation_agent import ApplicationAutomationAgent

logger = logging.getLogger(__name__)

class UnicornAgent:
    """UnicornAgent handles magical tasks related to job applications."""

    def __init__(self, db: Session,
                 resume_parser_agent: ResumeParserAgent,
                 ats_scorer_agent: ATSScorerAgent,
                 job_matcher_agent: JobMatcherAgent,
                 application_automation_agent: ApplicationAutomationAgent):
        # [CONTEXT] Initializes the UnicornAgent with its dependencies.
        self.db = db
        self.notification_service = NotificationService(db_session=self.db)
        self.resume_parser_agent = resume_parser_agent
        self.ats_scorer_agent = ats_scorer_agent
        self.job_matcher_agent = job_matcher_agent
        self.application_automation_agent = application_automation_agent
        logger.info("UnicornAgent initialized.")

    async def run(self, data: dict) -> dict:
        # [CONTEXT] Orchestrates the magical operations of the UnicornAgent.
        logger.info(f"UnicornAgent received data: {data}")
        try:
            # Placeholder for actual magical task implementation
            # [CONTEXT] Orchestrates the job application workflow.
            user_profile = data.get("user_profile")
            job_posting = data.get("job_posting")

            if not user_profile or not job_posting:
                raise UnicornError("Missing user profile or job posting data.")

            async def _send_error_notification(recipient, subject, error_message, details=None):
                await self.notification_service.send_notification(
                    recipient=recipient,
                    message=error_message,
                    notification_type="email",
                    details={"subject": subject, "error": str(error_message), **(details if details else {})}
                )

            # Step 1: Parse Resume
            @retry_with_exponential_backoff(max_retries=3, initial_delay=1, errors=(Exception,))
            async def parse_resume_with_retry(resume_data):
                return await self.resume_parser_agent.run(resume_data)

            try:
                parsed_resume = await parse_resume_with_retry(user_profile.get("resume_data"))
                logger.info("Resume parsed successfully.")
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
                raise UnicornError(f"Resume parsing failed: {e}")

            # Step 2: ATS Scoring
            @retry_with_exponential_backoff(max_retries=3, initial_delay=1, errors=(Exception,))
            async def ats_score_with_retry(parsed_resume_data, job_posting_data):
                return await self.ats_scorer_agent.run(parsed_resume_data, job_posting_data)

            try:
                ats_score_result = await ats_score_with_retry(parsed_resume, job_posting)
                logger.info("ATS scoring completed.")
                await self.notification_service.send_notification(
                    recipient=user_profile.get("email"),
                    message=f"Your resume received an ATS score of {ats_score_result.get('score')}.",
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
                raise UnicornError(f"ATS scoring failed: {e}")

            # Step 3: Job Matching
            @retry_with_exponential_backoff(max_retries=3, initial_delay=1, errors=(Exception,))
            async def job_match_with_retry(user_profile_data, job_posting_data):
                return await self.job_matcher_agent.run(user_profile_data, job_posting_data)

            try:
                job_match_result = await job_match_with_retry(user_profile, job_posting)
                logger.info("Job matching completed.")
                await self.notification_service.send_notification(
                    recipient=user_profile.get("email"),
                    message=f"Job matching score: {job_match_result.get('score')}.",
                    notification_type="email",
                    details={"subject": "Job Matching Complete", "score": job_match_result.get('score')}
                )
            except Exception as e:
                logger.error(f"Job matching failed: {e}", exc_info=True)
                await _send_error_notification(
                    recipient=user_profile.get("email"),
                    subject="Job Matching Failed",
                    error_message=f"Failed to perform job matching: {e}"
                )
                raise UnicornError(f"Job matching failed: {e}")

            # Step 4: Application Automation
            @retry_with_exponential_backoff(max_retries=3, initial_delay=1, errors=(Exception,))
            async def automate_application_with_retry(user_profile_data, job_posting_data, parsed_resume_data):
                return await self.application_automation_agent.run(user_profile_data, job_posting_data, parsed_resume_data)

            try:
                application_result = await automate_application_with_retry(user_profile, job_posting, parsed_resume)
                logger.info("Application submitted successfully.")
                await self.notification_service.send_notification(
                    recipient=user_profile.get("email"),
                    message="Your application has been successfully submitted!",
                    notification_type="email",
                    details={"subject": "Application Submitted", "result": application_result}
                )
            except Exception as e:
                logger.error(f"Application automation failed: {e}", exc_info=True)
                await _send_error_notification(
                    recipient=user_profile.get("email"),
                    subject="Application Submission Failed",
                    error_message=f"Failed to submit your application: {e}"
                )
                raise UnicornError(f"Application automation failed: {e}")

            return {"status": "success", "message": "Job application workflow completed.", "results": {"parsed_resume": parsed_resume, "ats_score": ats_score_result, "job_match_result": job_match_result, "application_result": application_result}}
        except UnicornError as e:
            logger.error(f"UnicornAgent failed to perform magic: {e}", exc_info=True)
            await _send_error_notification(
                recipient="admin@example.com",
                subject="Unicorn Magic Failure",
                error_message=f"Unicorn magic failed for data {data}: {e.message}"
            )
            raise e
        except Exception as e:
            logger.error(f"An unexpected error occurred in UnicornAgent: {e}", exc_info=True)
            await _send_error_notification(
                recipient="admin@example.com",
                subject="Unicorn Agent Unexpected Error",
                error_message=f"An unexpected error occurred in UnicornAgent for data {data}: {e}"
            )
            raise UnicornError(f"Unexpected error during Unicorn operation: {e}")