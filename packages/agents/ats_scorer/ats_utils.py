import re
from typing import Dict, Any, Tuple
import re


def extract_keywords(text: str) -> list:
    """
    [CONTEXT] Extracts potential keywords from a given text.
    [PURPOSE] Identifies important terms for ATS matching.
    """
    common_tech_keywords = [
        "python",
        "java",
        "javascript",
        "c++",
        "c#",
        "go",
        "ruby",
        "php",
        "sql",
        "nosql",
        "mongodb",
        "postgresql",
        "mysql",
        "aws",
        "azure",
        "google cloud",
        "cloud computing",
        "data science",
        "machine learning",
        "artificial intelligence",
        "deep learning",
        "web development",
        "frontend",
        "backend",
        "fullstack",
        "devops",
        "agile",
        "scrum",
        "project management",
        "api",
        "rest",
        "graphql",
        "docker",
        "kubernetes",
        "ci/cd",
        "git",
        "github",
        "gitlab",
        "react",
        "angular",
        "vue",
        "node.js",
        "django",
        "flask",
        "spring",
        "linux",
        "windows",
        "macos",
        "cybersecurity",
        "networking",
        "communication",
        "leadership",
        "teamwork",
        "problem-solving",
        "analytical",
    ]
    extracted = []
    text_lower = text.lower()
    # Pre-compile regex patterns for efficiency
    compiled_patterns = [
        re.compile(r"\b" + re.escape(keyword) + r"\b")
        for keyword in common_tech_keywords
    ]
    for i, keyword in enumerate(common_tech_keywords):
        if compiled_patterns[i].search(text_lower):
            extracted.append(keyword)
    return list(set(extracted))


def calculate_keyword_score(resume_text: str, job_keywords: list) -> Tuple[float, list]:
    """
    [CONTEXT] Calculates a keyword matching score and identifies missing keywords.
    [PURPOSE] Evaluates how well resume content aligns with job description keywords.
    """
    if not job_keywords:
        return 0.0, []

    matched_keywords = []
    missing_keywords = []

    resume_text_lower = resume_text.lower()
    # Pre-compile regex patterns for efficiency
    compiled_patterns = [
        re.compile(r"\b" + re.escape(keyword) + r"\b")
        for keyword in job_keywords
    ]

    for i, keyword in enumerate(job_keywords):
        if compiled_patterns[i].search(resume_text_lower):
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    score = len(matched_keywords) / len(job_keywords)
    return score, missing_keywords


def calculate_formatting_score(resume_data: Dict[str, Any]) -> float:
    """
    [CONTEXT] Simulates a score based on common ATS-friendly formatting and structure.
    [PURPOSE] Encourages resumes with clear, parsable sections.
    """
    score = 0.0
    required_sections = [
        "name",
        "email",
        "skills",
        "experience",
        "education",
        "summary",
    ]
    present_sections = [
        section for section in required_sections if section in resume_data
    ]

    if len(required_sections) > 0:
        score = len(present_sections) / len(required_sections)

    if "experience" in resume_data and isinstance(resume_data["experience"], list):
        if all(
            isinstance(exp, dict)
            and "title" in exp
            and "company" in exp
            and "description" in exp
            for exp in resume_data["experience"]
        ):
            score += 0.1

    return min(1.0, score)


def identify_optimization_opportunities(
    missing_keywords: list, resume_data: Dict[str, Any]
) -> list:
    """
    [CONTEXT] Identifies specific areas for resume improvement based on ATS analysis.
    [PURPOSE] Provides actionable feedback to the user.
    """
    opportunities = []
    if missing_keywords:
        opportunities.append(
            f"Consider adding or emphasizing the following keywords: {', '.join(missing_keywords)}."
        )

    standard_sections = ["skills", "experience", "education", "summary"]
    for section in standard_sections:
        if section not in resume_data or not resume_data[section]:
            opportunities.append(
                f"Ensure your resume includes a clear '{section.capitalize()}' section."
            )

    if opportunities and len(opportunities) < 3:
        opportunities.append(
            "Review your experience bullet points to naturally integrate job-specific keywords."
        )

    return opportunities


def predict_success_probability(ats_score: float) -> str:
    """
    [CONTEXT] Predicts the likelihood of application success based on the ATS score.
    [PURPOSE] Gives the user an expectation of their application's performance.
    """
    if ats_score >= 90:
        return "Very High (Excellent ATS match, strong candidate)"
    elif ats_score >= 70:
        return "High (Good ATS match, competitive candidate)"
    elif ats_score >= 50:
        return "Medium (Moderate ATS match, may need further optimization)"
    else:
        return "Low (Poor ATS match, significant optimization needed)"
