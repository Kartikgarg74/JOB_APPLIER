# Cover Letter Generator Agent

## Purpose
This agent is responsible for creating personalized cover letters tailored to specific job applications. It leverages information from the user's resume and the target job description to generate a compelling letter that highlights relevant skills and experiences, aiming to increase the applicant's chances of success.

## Dependencies
- `logging`: Standard Python library for logging.
- `typing`: For type hints.

## Key Components
- `cover_letter_generator_agent.py`:
  - Defines the `CoverLetterGeneratorAgent` class, which contains the `generate_cover_letter` method.
  - The `generate_cover_letter` method takes `resume_data` (structured information from the user's resume) and a `job_description` string as input.
  - It includes placeholder logic for extracting basic information like applicant name, email, and skills from the resume, and attempts to naively extract company name and job title from the job description.
  - It then uses a simple f-string template to construct the cover letter.
  - In a more advanced implementation, this method would utilize natural language generation (NLG) techniques, potentially powered by large language models (LLMs), to:
    - Intelligently parse both resume and job description for key entities and relationships.
    - Dynamically select and rephrase relevant experiences and skills.
    - Adapt the tone and style of the letter based on the job's industry or company culture.
    - Ensure grammatical correctness and coherence.

## Usage Examples
```python
from packages.agents.cover_letter_generator.cover_letter_generator_agent import CoverLetterGeneratorAgent
from packages.utilities.logging_utils import setup_logging

# Setup logging for better output
setup_logging()

# Initialize the CoverLetterGeneratorAgent
generator = CoverLetterGeneratorAgent()

# Dummy resume data
dummy_resume_data = {
    "name": "Alice Smith",
    "email": "alice.smith@example.com",
    "skills": ["Python", "Data Analysis", "Machine Learning", "SQL"],
    "experience": [
        {"title": "Data Scientist", "description": "Developed predictive models."}
    ]
}

# Dummy job description
dummy_job_description = (
    "Job Title: Senior Data Scientist\nCompany: Innovate Solutions\nLocation: Remote\n" 
    "Description: We are seeking a highly skilled Data Scientist with expertise in Python, "
    "Machine Learning, and big data technologies. The ideal candidate will lead projects "
    "and develop innovative solutions."
)

print("\n--- Generating Cover Letter ---")
cover_letter = generator.generate_cover_letter(dummy_resume_data, dummy_job_description)

print("\n--- Generated Cover Letter ---")
print(cover_letter)

# Another example
dummy_job_description_2 = (
    "Role: Software Engineer\nFirm: Tech Giant Inc.\n" 
    "Description: Develop scalable backend systems using Python and SQL. "
    "Experience with cloud platforms is a plus."
)

print("\n--- Generating Cover Letter (Second Example) ---")
cover_letter_2 = generator.generate_cover_letter(dummy_resume_data, dummy_job_description_2)

print("\n--- Generated Cover Letter (Second Example) ---")
print(cover_letter_2)
```

## API Reference

### `CoverLetterGeneratorAgent` Class
- `__init__(self)`: Initializes the agent and its logger.
- `generate_cover_letter(self, resume_data: Dict[str, Any], job_description: str) -> str`:
  - `resume_data`: A dictionary representing the user's structured resume data.
  - `job_description`: A string containing the full text of the job description.
  - Returns a string containing the generated cover letter.

## Development Setup
No special setup is required beyond standard Python environment setup. Ensure all dependencies are installed.

## Testing
To test the `CoverLetterGeneratorAgent`, run `cover_letter_generator_agent.py` directly. It contains an `if __name__ == "__main__":` block with example usage.

## Contributing
Follow the general contribution guidelines for the project. When enhancing the cover letter generation logic, consider integrating advanced NLP models, more sophisticated parsing for job descriptions, and dynamic content generation based on resume strengths and job requirements.