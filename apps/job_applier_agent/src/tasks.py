from apps.job_applier_agent.src.celery_app import celery_app
from packages.utilities.parsers.resume_parser import parse_resume
from packages.agents.ats_scorer.ats_scorer_agent import ATSScorerAgent
import os
import shutil
import logging

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
