import logging
import logging
from typing import Dict, Any

import openai

from packages.agents.cover_letter_generator.cover_letter_utils import construct_cover_letter_prompt

logger = logging.getLogger(__name__)


class CoverLetterGeneratorAgent:
    """
    [CONTEXT] Generates a personalized cover letter based on resume data and job description.
    [PURPOSE] Creates a compelling cover letter that highlights relevant skills and experiences for a specific job application.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("CoverLetterGeneratorAgent initialized.")

    def generate_cover_letter(
        self, resume_data: Dict[str, Any], job_description: str
    ) -> str:
        """
        [CONTEXT] Crafts a cover letter by integrating information from the user's resume and the job description.
        [PURPOSE] Produces a tailored cover letter to accompany a job application.
        """
        self.logger.info("Starting cover letter generation using OpenAI.")

        prompt = construct_cover_letter_prompt(resume_data, job_description)

        try:
            response = openai.chat.completions.create(
                model="gpt-4",  # Or another suitable model like "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates professional cover letters."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7,
            )
            cover_letter_content = response.choices[0].message.content.strip()
            self.logger.info("Cover letter generation completed successfully.")
            return cover_letter_content
        except openai.APIError as e:
            self.logger.error(f"OpenAI API error during cover letter generation: {e}")
            return f"Error generating cover letter: {e}"
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during cover letter generation: {e}")
            return f"Error generating cover letter: {e}"


if __name__ == "__main__":
    from packages.utilities.logging_utils import setup_logging

    setup_logging()

    generator = CoverLetterGeneratorAgent()

    # Dummy resume data
    dummy_resume_data = {
        "name": "Alice Smith",
        "email": "alice.smith@example.com",
        "skills": ["Python", "Data Analysis", "Machine Learning", "SQL"],
        "experience": [
            {"title": "Data Scientist", "description": "Developed predictive models."}
        ],
    }

    # Dummy job description
    dummy_job_description = (
        "Job Title: Senior Data Scientist\nCompany: Innovate Solutions\nLocation: Remote\n"
        "Description: We are seeking a highly skilled Data Scientist with expertise in Python, "
        "Machine Learning, and big data technologies. The ideal candidate will lead projects "
        "and develop innovative solutions."
    )

    print("\n--- Generating Cover Letter ---")
    cover_letter = generator.generate_cover_letter(
        dummy_resume_data, dummy_job_description
    )

    print("\n--- Generated Cover Letter ---")
    print(cover_letter)

    # Another example
    dummy_job_description_2 = (
        "Role: Software Engineer\nFirm: Tech Giant Inc.\n"
        "Description: Develop scalable backend systems using Python and SQL. "
        "Experience with cloud platforms is a plus."
    )

    print("\n--- Generating Cover Letter (Second Example) ---")
    cover_letter_2 = generator.generate_cover_letter(
        dummy_resume_data, dummy_job_description_2
    )

    print("\n--- Generated Cover Letter (Second Example) ---")
    print(cover_letter_2)
