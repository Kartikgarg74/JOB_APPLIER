from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def load_user_resume(file_manager) -> Dict[str, Any]:
    """
    [CONTEXT] Loads the user's resume data from a JSON file.
    [PURPOSE] Ensures the agent has access to the user's current resume for enhancement.
    """
    resume_data = file_manager.read_json("user_resume.json")
    if resume_data:
        logger.info("User resume loaded successfully.")
        return resume_data
    else:
        logger.error(
            "Failed to load user resume. Please ensure 'user_resume.json' exists and is correctly formatted."
        )
        return {}

def extract_keywords_from_job_description(job_description: str) -> list:
    """
    [CONTEXT] Extracts key skills and keywords from the job description.
    [PURPOSE] Identifies important terms to be used for resume enhancement.
    """
    common_tech_keywords = [
        "python", "java", "javascript", "c++", "c#", "go", "ruby", "php",
        "sql", "nosql", "mongodb", "postgresql", "mysql", "aws", "azure",
        "google cloud", "cloud computing", "data science", "machine learning",
        "artificial intelligence", "deep learning", "web development", "frontend",
        "backend", "fullstack", "devops", "agile", "scrum", "project management",
        "api", "rest", "graphql", "docker", "kubernetes", "ci/cd", "git",
        "github", "gitlab", "react", "angular", "vue", "node.js", "django",
        "flask", "spring", "linux", "windows", "macos", "cybersecurity",
        "networking",
    ]
    extracted_keywords = []
    job_description_lower = job_description.lower()

    for keyword in common_tech_keywords:
        if keyword in job_description_lower:
            extracted_keywords.append(keyword.capitalize())
    return list(set(extracted_keywords))

def highlight_experience_and_add_keywords(
    resume_data: Dict[str, Any], job_keywords: list
) -> Dict[str, Any]:
    """
    [CONTEXT] Modifies the resume to highlight relevant experience and integrate keywords.
    [PURPOSE] Makes the resume more appealing to recruiters and ATS by emphasizing alignment with job requirements.
    """
    current_skills = set(resume_data.get("skills", []))
    for keyword in job_keywords:
        if keyword not in current_skills:
            current_skills.add(keyword)
            logger.info(f"Added keyword '{keyword}' to skills section.")
    resume_data["skills"] = list(current_skills)

    for experience in resume_data.get("experience", []):
        original_description = experience.get("description", "")
        new_description = original_description
        for keyword in job_keywords:
            if keyword.lower() not in original_description.lower():
                new_description += f" (Familiar with {keyword})"
                logger.info(
                    f"Attempted to add '{keyword}' to experience description."
                )
        experience["description"] = new_description

    return resume_data

def adjust_for_ats_compatibility(
    resume_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    [CONTEXT] Adjusts the resume formatting for Applicant Tracking System (ATS) compatibility.
    [PURPOSE] Ensures the resume can be easily parsed by automated systems.
    """
    logger.info("Applying ATS compatibility adjustments (placeholder).")
    return resume_data