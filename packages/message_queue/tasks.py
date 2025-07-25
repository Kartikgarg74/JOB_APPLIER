from apps.job_applier_agent.src.celery_app import celery_app
from packages.utilities.parsers.resume_parser import parse_resume
from packages.agents.ats_scorer.ats_scorer_agent import ATSScorerAgent
import os
import logging
from celery import states
from celery.exceptions import Ignore

logger = logging.getLogger(__name__)


@celery_app.task
def process_resume_upload_task(
    file_path: str, file_content_type: str, user_profile_path: str
):
    try:
        # Parse the resume
        resume_data = parse_resume(file_path, file_content_type)
        resume_text_content = resume_data.get("full_text", "")

        if not resume_text_content:
            logger.warning(f"Could not extract text from resume {file_path}")
            return {"status": "error", "message": "Could not extract text from resume."}

        # Update user profile with resume text (simplified for now)
        # In a real scenario, you might want to store parsed data in a DB or more structured way
        from packages.config.user_profile import load_user_profile, save_user_profile

        user_profile = load_user_profile(user_profile_path)
        user_profile["resume_text"] = resume_text_content
        save_user_profile(user_profile, user_profile_path)

        logger.info(
            f"Successfully processed and updated user profile with resume from {file_path}"
        )
        return {
            "status": "success",
            "message": "Resume processed and user profile updated successfully.",
        }
    except Exception as e:
        logger.error(
            f"Error processing resume upload task for {file_path}: {e}", exc_info=True
        )
        return {"status": "error", "message": f"Failed to process resume: {e}"}
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up temporary resume file: {file_path}")


@celery_app.task
def calculate_ats_score_task(
    resume_file_path: str, resume_content_type: str, job_description: str
):
    try:
        resume_data = parse_resume(resume_file_path, resume_content_type)
        resume_text_content = resume_data.get("full_text", "")

        if not resume_text_content:
            logger.warning(f"Could not extract text from resume {resume_file_path}")
            return {"status": "error", "message": "Could not extract text from resume."}

        ats_scorer = ATSScorerAgent()
        ats_result = ats_scorer.score_resume(
            {"full_text": resume_text_content}, job_description
        )
        logger.info(f"Successfully calculated ATS score for {resume_file_path}")
        return {"status": "success", "ats_result": ats_result}
    except Exception as e:
        logger.error(
            f"Error calculating ATS score for {resume_file_path}: {e}", exc_info=True
        )
        return {"status": "error", "message": f"Failed to calculate ATS score: {e}"}
    finally:
        # Clean up the temporary file
        if os.path.exists(resume_file_path):
            os.remove(resume_file_path)
            logger.info(f"Cleaned up temporary resume file: {resume_file_path}")


@celery_app.task(bind=True)
async def run_unicorn_agent_task(self, data: dict):
    from packages.agents.unicorn_agent.unicorn_agent import UnicornAgent
    from packages.notifications.notification_service import NotificationService
    from packages.database.config import get_db

    logger.info(f"UnicornAgent task received data: {data}")
    db_session = next(get_db())
    notification_service = NotificationService(db_session=db_session)
    try:
        db_session = next(get_db())
        unicorn_agent = UnicornAgent(db_session)
        result = await unicorn_agent.run(data)
        logger.info("UnicornAgent task completed successfully.")
        notification_service.send_notification(
            recipient=data.get("user_profile", {}).get("email"),
            message="Your job application process has been completed successfully!",
            notification_type="email",
            details={"subject": "Application Process Complete", "status": "success"}
        )
        return {"status": "success", "message": "UnicornAgent task completed.", "results": result}
    except Exception as e:
        logger.error(f"UnicornAgent task failed: {e}", exc_info=True)
        notification_service.send_notification(
            recipient=data.get("user_profile", {}).get("email"),
            message=f"Your job application process failed: {e}",
            notification_type="email",
            details={"subject": "Application Process Failed", "status": "failed", "error": str(e)}
        )
        # Optionally, retry the task
        # raise self.retry(exc=e, countdown=60)
        return {"status": "error", "message": f"UnicornAgent task failed: {e}"}


@celery_app.task(bind=True, default_retry_delay=60, max_retries=3, queue="high_priority")
def send_email_task(self, to_email, subject, body):
    try:
        # Simulate sending email (replace with real email logic)
        print(f"Sending email to {to_email}: {subject}\n{body}")
        # If you want to simulate a failure, uncomment:
        # raise Exception("Simulated email failure")
        return {"status": "sent", "to": to_email}
    except Exception as exc:
        # Send to dead letter queue after max retries
        if self.request.retries >= self.max_retries:
            from .celery_app import handle_dead_letter
            handle_dead_letter.apply_async(("send_email_task", (to_email, subject, body), {}, str(exc)), queue="dead_letter")
            self.update_state(state=states.FAILURE, meta={"exc": str(exc)})
            raise Ignore()
        raise self.retry(exc=exc)

# Example usage (from app code):
# from packages.message_queue.tasks import send_email_task
# send_email_task.delay("user@example.com", "Welcome!", "Thanks for signing up.")
