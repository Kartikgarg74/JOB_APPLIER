import logging
import logging
from typing import Dict, Any

import openai
import os

from packages.agents.cover_letter_generator.cover_letter_utils import construct_cover_letter_prompt

logger = logging.getLogger(__name__)


class CoverLetterGeneratorAgent:
    """
    [CONTEXT] Generates a personalized cover letter based on resume data and job description.
    [PURPOSE] Creates a compelling cover letter that highlights relevant skills and experiences for a specific job application.
    [USAGE] Supports both OpenAI (GPT-4) and Google Gemini for generation. Set provider='openai' or provider='gemini'.
    [GEMINI] Requires GEMINI_API_KEY in environment or passed to constructor.
    """

    def __init__(self, provider: str = 'openai', gemini_api_key: str = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"CoverLetterGeneratorAgent initialized with provider: {provider}")
        self.provider = provider
        self.gemini_api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
        if self.provider == 'gemini':
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                # Use Gemini 2.5 Flash (gemini-1.5-flash)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini: {e}")
                self.gemini_model = None
        self.system_prompt = """You are a highly capable, production-grade Job Application Agent powered by Gemini 2.5 Flash. Your core responsibility is to automate and optimize the job search and application process for users by intelligently analyzing resumes, matching them to job postings, and executing applications, even under unreliable network conditions or API failures.

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

You are an expert job applier — fast, intelligent, resilient. Think like a recruiter, act like an agent."""

    def generate_cover_letter(
        self, resume_data: Dict[str, Any], job_description: str, user_preferences: Dict[str, Any] = None
    ) -> str:
        """
        [CONTEXT] Crafts a cover letter by integrating information from the user's resume and the job description.
        [PURPOSE] Produces a tailored cover letter to accompany a job application.
        """
        prompt = construct_cover_letter_prompt(resume_data, job_description, user_preferences)
        if self.provider == 'gemini':
            self.logger.info("Starting cover letter generation using Gemini 2.5 Flash (gemini-1.5-flash).")
            try:
                if not self.gemini_model:
                    import google.generativeai as genai
                    genai.configure(api_key=self.gemini_api_key)
                    self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                response = self.gemini_model.generate_content(
                    contents=[{'role':'user', 'parts': [self.system_prompt, prompt]}]
                )
                cover_letter_content = response.text.strip()
                self.logger.info("Cover letter generation completed successfully (Gemini 2.5 Flash).")
                return cover_letter_content
            except Exception as e:
                self.logger.error(f"Gemini API error during cover letter generation: {e}")
                return f"Error generating cover letter (Gemini): {e}"
        else:
            self.logger.info("Starting cover letter generation using OpenAI.")
            try:
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that generates professional cover letters."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7,
                )
                cover_letter_content = response.choices[0].message.content.strip()
                self.logger.info("Cover letter generation completed successfully (OpenAI).")
                return cover_letter_content
            except Exception as e:
                self.logger.error(f"OpenAI API error during cover letter generation: {e}")
                return f"Error generating cover letter (OpenAI): {e}"


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
