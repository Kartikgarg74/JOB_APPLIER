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


def calculate_keyword_score_and_density(resume_data: dict, job_keywords: list) -> tuple:
    """
    Calculates keyword matching score, missing keywords, and keyword density.
    Weights skills, experience, and summary separately.
    Also highlights underrepresented keywords (present only once).
    """
    if not job_keywords:
        return 0.0, [], {}, []

    # Gather text from relevant sections
    skills_text = ' '.join(resume_data.get('skills', []))
    experience_text = ' '.join([
        (exp.get('title', '') + ' ' + exp.get('description', ''))
        for exp in resume_data.get('experience', []) if isinstance(exp, dict)
    ])
    summary_text = resume_data.get('summary', '')
    raw_text = resume_data.get('raw_text', '')
    full_text = f"{skills_text} {experience_text} {summary_text} {raw_text}"
    full_text_lower = full_text.lower()

    matched_keywords = []
    missing_keywords = []
    keyword_density = {}
    underrepresented_keywords = []
    for keyword in job_keywords:
        count = full_text_lower.count(keyword.lower())
        keyword_density[keyword] = count
        if count > 0:
            matched_keywords.append(keyword)
            if count == 1:
                underrepresented_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
    # Weight: skills 0.5, experience 0.3, summary 0.2
    skills_score = sum([skills_text.lower().count(k.lower()) for k in job_keywords]) / max(1, len(job_keywords))
    experience_score = sum([experience_text.lower().count(k.lower()) for k in job_keywords]) / max(1, len(job_keywords))
    summary_score = sum([summary_text.lower().count(k.lower()) for k in job_keywords]) / max(1, len(job_keywords))
    score = 0.5 * skills_score + 0.3 * experience_score + 0.2 * summary_score
    score = min(score, 1.0)
    return score, missing_keywords, keyword_density, underrepresented_keywords

def check_ats_unfriendly_formatting(resume_text: str) -> dict:
    """
    Simulate formatting checks for ATS-unfriendly elements: tables, columns, images, font size, color, bullet points.
    Returns a dict with flags and a penalty score (0-1, where 1 is perfect formatting).
    """
    issues = {}
    penalty = 0.0
    # Simulate table detection (lines with lots of | or tabs)
    if re.search(r'\|\s*\|', resume_text) or re.search(r'\t{2,}', resume_text):
        issues['tables_or_columns'] = True
        penalty += 0.2
    # Simulate image detection (common image file extensions)
    if re.search(r'\.(jpg|jpeg|png|gif|bmp|svg)', resume_text, re.IGNORECASE):
        issues['images'] = True
        penalty += 0.2
    # Simulate font/formatting issues (all caps lines)
    if re.search(r'^[A-Z\s]{10,}$', resume_text, re.MULTILINE):
        issues['all_caps_lines'] = True
        penalty += 0.1
    # Simulate font size (look for 'font-size' or numbers in px/pt)
    if re.search(r'font-size\s*:\s*\d{1,2}(px|pt)', resume_text):
        issues['font_size_explicit'] = True
        penalty += 0.05
    # Simulate color (look for 'color:' or hex codes)
    if re.search(r'color\s*:\s*#[0-9a-fA-F]{3,6}', resume_text):
        issues['font_color'] = True
        penalty += 0.05
    # Simulate bullet points (should have at least 3 in experience)
    bullet_count = len(re.findall(r'\n\s*[-•]', resume_text))
    if bullet_count < 3:
        issues['few_bullet_points'] = True
        penalty += 0.05
    # Clamp penalty
    penalty = min(penalty, 0.5)
    return {'issues': issues, 'penalty': penalty, 'formatting_score': 1.0 - penalty}

def get_industry_weights(industry: str) -> dict:
    """
    Return scoring weights for different industries, with more granularity.
    """
    industry = (industry or '').lower()
    if industry == 'tech':
        return {'keywords': 0.6, 'formatting': 0.2, 'skills': 0.1, 'experience': 0.1}
    elif industry == 'finance':
        return {'keywords': 0.5, 'formatting': 0.2, 'certifications': 0.2, 'skills': 0.1}
    elif industry == 'healthcare':
        return {'keywords': 0.4, 'formatting': 0.2, 'certifications': 0.3, 'skills': 0.1}
    elif industry == 'data science':
        return {'keywords': 0.5, 'formatting': 0.2, 'skills': 0.2, 'experience': 0.1}
    elif industry == 'marketing':
        return {'keywords': 0.5, 'formatting': 0.2, 'skills': 0.2, 'summary': 0.1}
    else:
        return {'keywords': 0.7, 'formatting': 0.3}

def benchmark_score(score: float, industry: str = None) -> str:
    """
    Simulate benchmarking by returning a percentile string based on score, with more granularity.
    """
    import random
    # Add a small random noise to simulate real-world variation
    score = score + random.uniform(-2, 2)
    if score >= 95:
        return 'Top 2%'
    elif score >= 90:
        return 'Top 5%'
    elif score >= 80:
        return 'Top 10%'
    elif score >= 70:
        return 'Top 20%'
    elif score >= 60:
        return 'Top 30%'
    elif score >= 50:
        return 'Top 40%'
    else:
        return 'Below 40%'
