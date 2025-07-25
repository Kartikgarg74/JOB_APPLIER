import logging
import os
from typing import Optional, Dict, Any
from types import TracebackType
from packages.agents.resume_parser.resume_utils import (
    extract_personal_details,
    extract_education,
    extract_experience,
    extract_skills,
    extract_projects,
    extract_text_from_pdf,
    extract_text_from_docx,
    validate_extracted_data,
    extract_certifications,
    extract_awards,
    extract_achievements,
    ResumeData
)

class ResumeParserAgent:
    """
    Parses a resume to extract structured information using NLP.

    Args:
        db: Database/session dependency (optional, for future extensibility).
        logger: Logger instance for dependency injection and testability.
    """
    def __init__(self, db: Optional[Any], logger: Optional[logging.Logger] = None) -> None:
        self.db = db
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info("ResumeParserAgent initialized with NLP capabilities.")

    def parse_resume_file(self, file_path: str) -> Optional[ResumeData]:
        """
        Parse a resume file (PDF or DOCX) and extract structured information.

        Args:
            file_path: Path to the resume file.

        Returns:
            ResumeData object if parsing is successful, None otherwise.
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return None

        try:
            # Extract text based on file type
            if file_path.lower().endswith('.pdf'):
                resume_text = extract_text_from_pdf(file_path)
            elif file_path.lower().endswith(('.docx', '.doc')):
                resume_text = extract_text_from_docx(file_path)
            else:
                self.logger.error(f"Unsupported file format: {file_path}")
                return None

            if not resume_text:
                self.logger.error("Failed to extract text from resume file")
                return None

            return self.parse_resume(resume_text)

        except Exception as e:
            self.logger.exception(f"Error parsing resume file: {e}")
            return None

    def parse_resume(self, resume_text: str) -> Optional[ResumeData]:
        """
        Parse resume text and extract structured information using NLP.

        Args:
            resume_text: Raw text of the resume.

        Returns:
            ResumeData object if parsing is successful, None otherwise.
        """
        if not resume_text:
            self.logger.warning("Empty resume text provided.")
            return None

        try:
            # Extract all components
            personal_details = extract_personal_details(resume_text)
            education = extract_education(resume_text)
            experience = extract_experience(resume_text)
            skills = extract_skills(resume_text)
            projects = extract_projects(resume_text)
            certifications = extract_certifications(resume_text)
            awards = extract_awards(resume_text)
            achievements = extract_achievements(resume_text)

            # Create structured resume data
            resume_data = ResumeData(
                raw_text=resume_text,
                personal_details=personal_details,
                education=education,
                experience=experience,
                skills=skills,
                projects=projects,
                certifications=certifications,
                awards=awards,
                achievements=achievements,
                summary="",  # TODO: Implement summary extraction using NLP
                keywords=skills,
                location=personal_details.get("location", "")
            )

            # Validate the extracted data
            if not validate_extracted_data(resume_data.__dict__):
                self.logger.warning("Resume data validation failed")
                return None

            return resume_data

        except Exception as e:
            self.logger.exception(f"Error parsing resume text: {e}")
            return None


if __name__ == "__main__":
    import json
    from packages.utilities.logging_utils import setup_logging

    setup_logging()

    parser = ResumeParserAgent(None)

    example_text = """
    John Doe
    john.doe@example.com | (123) 456-7890
    github.com/johndoe | linkedin.com/in/johndoe

    EDUCATION
    Master of Science in Computer Science
    Stanford University, 2018-2020
    GPA: 3.8

    EXPERIENCE
    Senior Software Engineer | TechCorp
    January 2020 - Present
    - Led development of microservices architecture using Python and Docker
    - Implemented CI/CD pipeline reducing deployment time by 50%
    - Mentored junior developers and conducted code reviews

    Software Engineer | StartupCo
    June 2018 - December 2019
    - Developed RESTful APIs using Node.js and Express
    - Optimized database queries improving response time by 40%

    SKILLS
    Languages: Python, JavaScript, Java, SQL
    Frameworks: React, Node.js, Django, Flask
    Tools: Git, Docker, Kubernetes, AWS

    PROJECTS
    AI-Powered Resume Parser
    - Built using Python, spaCy, and FastAPI
    - Implemented NLP for extracting structured data from resumes
    - Achieved 95% accuracy in information extraction
    """

    result = parser.parse_resume(example_text)

    if result:
        print("\n=== Parsed Resume Data ===")
        print(json.dumps(result.__dict__, indent=2))
    else:
        print("Failed to parse resume.")
