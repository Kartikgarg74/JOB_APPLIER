import logging
import os
from typing import Optional, Dict, Any

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
    extract_awards
)

logger = logging.getLogger(__name__)

class ResumeParserAgent:
    """
    [CONTEXT] Parses a resume to extract structured information using NLP.
    [PURPOSE] Converts resume files (PDF/DOCX) into a standardized ResumeData object.
    """

    def __init__(self, db):
        self.db = db
        logger.info("ResumeParserAgent initialized with NLP capabilities.")

    def parse_resume_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse a resume file (PDF or DOCX) and extract structured information.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None

        try:
            # Extract text based on file type
            if file_path.lower().endswith('.pdf'):
                resume_text = extract_text_from_pdf(file_path)
            elif file_path.lower().endswith(('.docx', '.doc')):
                resume_text = extract_text_from_docx(file_path)
            else:
                logger.error(f"Unsupported file format: {file_path}")
                return None

            if not resume_text:
                logger.error("Failed to extract text from resume file")
                return None

            return self.parse_resume(resume_text)

        except Exception as e:
            logger.error(f"Error parsing resume file: {e}")
            return None

    def parse_resume(self, resume_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse resume text and extract structured information using NLP.
        """
        if not resume_text:
            logger.warning("Empty resume text provided.")
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

            # Create structured resume data
            resume_data = {
                "raw_text": resume_text,
                "personal_details": personal_details,
                "education": education,
                "experience": experience,
                "skills": skills,
                "projects": projects,
                "certifications": certifications,
                "awards": awards,
                "summary": "",  # TODO: Implement summary extraction using NLP
                "keywords": skills,  # Using skills as keywords for now
                "location": personal_details.get("location", "")
            }

            # Validate the extracted data
            if not validate_extracted_data(resume_data):
                logger.warning("Resume data validation failed")
                return None

            return resume_data

        except Exception as e:
            logger.error(f"Error parsing resume text: {e}")
            return None


if __name__ == "__main__":
    # Example Usage
    import json
    from packages.utilities.logging_utils import setup_logging

    setup_logging()

    # Initialize parser
    parser = ResumeParserAgent(None)

    # Example resume text
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

    # Parse resume
    result = parser.parse_resume(example_text)

    if result:
        print("\n=== Parsed Resume Data ===")
        print(json.dumps(result, indent=2))
    else:
        print("Failed to parse resume.")
