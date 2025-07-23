import logging
from typing import Dict, Any
import json

from .resume_enhancer_utils import load_user_resume, extract_keywords_from_job_description, highlight_experience_and_add_keywords, adjust_for_ats_compatibility

logger = logging.getLogger(__name__)


class ResumeEnhancerAgent:
    """
    [CONTEXT] Enhances the user's resume based on a specific job description.
    [PURPOSE] Optimizes the resume content to improve its ATS compatibility and relevance for a target job.
    """

    def __init__(self, file_manager):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.file_manager = file_manager
        self.user_resume = load_user_resume(self.file_manager)
        self.logger.info("ResumeEnhancerAgent initialized.")


    def enhance_resume(self, job_description: str) -> Dict[str, Any]:
        """
        [CONTEXT] Analyzes the job description and enhances the user's loaded resume data.
        [PURPOSE] Generates an optimized version of the resume data tailored for the given job, focusing on ATS compatibility and keyword relevance.
        """
        self.logger.info("Starting resume enhancement process.")
        enhanced_resume_data = self.user_resume.copy()

        # 1. Analyze job description for key requirements and keywords
        job_keywords = extract_keywords_from_job_description(job_description)
        self.logger.info(f"Extracted job keywords: {job_keywords}")

        # 2. Highlight relevant experience and add industry-specific keywords naturally
        enhanced_resume_data = highlight_experience_and_add_keywords(
            enhanced_resume_data, job_keywords
        )

        # 3. Adjust formatting for ATS compatibility (placeholder)
        enhanced_resume_data = adjust_for_ats_compatibility(enhanced_resume_data)

        self.logger.info("Resume enhancement process completed.")
        return enhanced_resume_data





if __name__ == "__main__":
    from packages.utilities.logging_utils import setup_logging
    from packages.utils.file_manager import FileManager

    setup_logging()

    # Create a dummy user_resume.json for testing
    dummy_resume_content = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "skills": ["Python", "Java", "SQL", "Project Management"],
        "experience": [
            {
                "title": "Software Engineer",
                "description": "Developed scalable web applications using Python and Django.",
            },
            {
                "title": "Project Coordinator",
                "description": "Managed agile software development projects.",
            },
        ],
        "education": [
            {"degree": "M.Sc. Computer Science", "university": "Tech University"}
        ],
    }

    file_manager = FileManager()
    resume_file_path = file_manager.get_path("user_resume.json")
    with open(resume_file_path, "w") as f:
        json.dump(dummy_resume_content, f, indent=4)
    print(f"Created dummy user_resume.json at {resume_file_path}")

    enhancer = ResumeEnhancerAgent(file_manager)

    # Dummy job description
    dummy_job_description = (
        "We are seeking a skilled Software Engineer with expertise in Python, AWS, and Machine Learning. "
        "Experience with large-scale data science projects is a plus. "
        "Candidate should be proficient in developing robust and scalable solutions using Agile methodologies."
    )

    print("\n--- Original Resume Data (loaded from file) ---")
    print(enhancer.user_resume)

    print("\n--- Enhancing Resume ---")
    enhanced_resume = enhancer.enhance_resume(dummy_job_description)

    print("\n--- Enhanced Resume Data ---")
    print(enhanced_resume)

    # Another example
    dummy_job_description_2 = (
        "Looking for a Data Scientist with strong Machine Learning skills. "
        "Familiarity with Python, SQL, and statistical modeling is required. Experience with Big Data platforms like Hadoop or Spark is a plus."
    )

    print("\n--- Enhancing Resume (Second Example) ---")
    enhanced_resume_2 = enhancer.enhance_resume(dummy_job_description_2)

    print("\n--- Enhanced Resume Data (Second Example) ---")
    print(enhanced_resume_2)

    # Clean up the dummy resume file
    import os

    os.remove(resume_file_path)
    print(f"Cleaned up dummy user_resume.json at {resume_file_path}")
