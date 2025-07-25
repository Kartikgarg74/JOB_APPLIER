import logging
from packages.notifications.notification_service import NotificationService
from sqlalchemy.orm import Session
from packages.errors.custom_exceptions import UnicornError
from packages.utilities.retry_utils import retry_with_exponential_backoff
from packages.agents.resume_parser.resume_parser_agent import ResumeParserAgent
from packages.agents.ats_scorer.ats_scorer_agent import ATSScorerAgent
from packages.agents.job_matcher.job_matcher_agent import JobMatcherAgent
from packages.agents.application_automation.application_automation_agent import ApplicationAutomationAgent
import asyncio

logger = logging.getLogger(__name__)

class UnicornAgent:
    """UnicornAgent handles magical tasks related to job applications.
    [BATCH] Supports parallel processing of multiple job applications via run_batch().
    """

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
                    update_progress("job_matching", 70)
                    await self.notification_service.send_notification(
                        recipient=user_profile.get("email"),
                        message=f"Job matching score: {job_match_result.get('score')}",
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
                    update_progress("job_matching", 100)
                    raise UnicornError(f"Job matching failed: {e}")
            else:
                update_progress("job_matching", 100)

            # Step 4: Application Automation
            if workflow_config.get('application_automation', True):
                update_progress("application_automation", 75)
                @retry_with_exponential_backoff(max_retries=3, initial_delay=1, errors=(Exception,))
                async def automate_application_with_retry(user_profile_data, job_posting_data, parsed_resume_data):
                    return await self.application_automation_agent.run(user_profile_data, job_posting_data, parsed_resume_data)
                try:
                    application_result = await automate_application_with_retry(user_profile, job_posting, parsed_resume)
                    logger.info("Application submitted successfully.")
                    update_progress("application_automation", 100)
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
                    update_progress("application_automation", 100)
                    raise UnicornError(f"Application automation failed: {e}")
            else:
                update_progress("application_automation", 100)

            return {"status": "success", "message": "Job application workflow completed.", "results": {"parsed_resume": parsed_resume, "ats_score": ats_score_result, "job_match_result": job_match_result, "application_result": application_result}}
        except UnicornError as e:
            logger.error(f"UnicornAgent failed to perform magic: {e}", exc_info=True)
            if progress_callback:
                progress_callback("error", 100)
            await _send_error_notification(
                recipient="admin@example.com",
                subject="Unicorn Magic Failure",
                error_message=f"Unicorn magic failed for data {data}: {e.message}"
            )
            raise e
        except Exception as e:
            logger.error(f"An unexpected error occurred in UnicornAgent: {e}", exc_info=True)
            if progress_callback:
                progress_callback("error", 100)
            await _send_error_notification(
                recipient="admin@example.com",
                subject="Unicorn Agent Unexpected Error",
                error_message=f"An unexpected error occurred in UnicornAgent for data {data}: {e}"
            )
            raise UnicornError(f"Unexpected error during Unicorn operation: {e}")

    async def run_batch(self, batch_data: list, progress_callback=None, workflow_config=None) -> list:
        """
        Processes multiple job applications in parallel.
        Each item in batch_data should be a dict as expected by run().
        Returns a list of results, one per job application.
        Progress tracking is logged for each job and can be reported via progress_callback.
        workflow_config can be used to customize which steps to run/skip for all jobs.
        """
        total = len(batch_data)
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

        tasks = [run_with_progress(i, data) for i, data in enumerate(batch_data)]
        await asyncio.gather(*tasks)
        return results
