from typing import Dict, Any, Optional
import re
import requests
from packages.utilities.logging_utils import get_logger

logger = get_logger(__name__)

def fetch_company_info(company_name: str) -> str:
    """
    Fetches a brief summary or recent news about the company using a web search API (or fallback to Google search snippet scraping).
    Returns a string with company info or an empty string if not found.
    """
    try:
        # Use a simple web search (DuckDuckGo Instant Answer API or similar)
        # For production, use a paid API like SerpAPI, Bing, or Gemini web search.
        # Here, we use DuckDuckGo as a free fallback.
        url = f"https://api.duckduckgo.com/?q={company_name}+company&format=json&no_redirect=1&no_html=1"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            abstract = data.get("Abstract", "")
            if abstract:
                return abstract
            related = data.get("RelatedTopics", [])
            if related and isinstance(related, list):
                for topic in related:
                    if isinstance(topic, dict) and topic.get("Text"):
                        return topic["Text"]
        # Fallback: just return empty string
        return ""
    except Exception as e:
        logger.warning(f"Failed to fetch company info for {company_name}: {e}")
        return ""


def construct_cover_letter_prompt(
    resume_data: Dict[str, Any], job_description: str, style: str = 'formal', company_name: Optional[str] = None, company_info: Optional[str] = None, tone: str = 'professional'
) -> str:
    """
    [CONTEXT] Constructs the prompt for generating a personalized cover letter.
    [PURPOSE] Formats applicant and job description data into a prompt for the AI model, with advanced personalization, explicit skill/requirement matching, company research, and tone adjustment.
    [TEMPLATES] Available styles: 'formal', 'creative', 'concise'.
    [TONES] Available tones: 'professional', 'friendly', 'enthusiastic', 'confident', 'humble', etc.
    [COMPANY RESEARCH] If company_info is not provided, fetches a summary or news for company_name and includes it in the prompt.
    """
    applicant_name = resume_data.get("name", "")
    applicant_email = resume_data.get("email", "")
    applicant_phone = resume_data.get("phone", "")
    applicant_skills = set(resume_data.get("skills", []))
    applicant_experience = "\n".join(
        [f"- {exp['title']}: {exp['description']}" for exp in resume_data.get("experience", [])]
    )
    applicant_education = "\n".join(
        [f"- {edu['degree']} in {edu.get('field_of_study', edu.get('field', ''))} from {edu.get('institution', edu.get('university', ''))}" for edu in resume_data.get("education", [])]
    )

    job_keywords = set(re.findall(r"[A-Za-z0-9\-\+\.]{2,}", job_description))
    matched_skills = applicant_skills.intersection(job_keywords)
    matched_skills_str = ", ".join(matched_skills) if matched_skills else "(AI: Please infer and match relevant skills from resume and job description)"
    unique_strengths = resume_data.get("unique_strengths", "(AI: Please highlight unique strengths from resume)")

    # Template instructions based on style
    if style == 'formal':
        style_instructions = "Use a professional, formal tone."
    elif style == 'creative':
        style_instructions = "Use a creative, engaging, and slightly informal tone. Feel free to use metaphors or storytelling."
    elif style == 'concise':
        style_instructions = "Be extremely concise and direct. Limit the cover letter to 150 words or less."
    else:
        style_instructions = "Use a professional, formal tone."

    # Tone instructions
    if tone == 'friendly':
        tone_instructions = "The tone should be friendly and approachable."
    elif tone == 'enthusiastic':
        tone_instructions = "The tone should be enthusiastic and energetic."
    elif tone == 'confident':
        tone_instructions = "The tone should be confident and assertive."
    elif tone == 'humble':
        tone_instructions = "The tone should be humble and modest."
    else:
        tone_instructions = "The tone should be professional."

    # Company research integration
    company_section = ""
    if company_info:
        company_section = f"\nCompany Information (for deeper personalization):\n{company_info}\n"
    elif company_name:
        fetched_info = fetch_company_info(company_name)
        if fetched_info:
            company_section = f"\nCompany Information (for deeper personalization):\n{fetched_info}\n"

    prompt = f"""
Generate a highly personalized cover letter for a job application.

Applicant Information:
Name: {applicant_name}
Email: {applicant_email}
Phone: {applicant_phone}
Skills: {', '.join(applicant_skills)}
Experience:
{applicant_experience}
Education:
{applicant_education}

Job Description:
{job_description}
{company_section}
Matched Skills/Experiences:
{matched_skills_str}

Why I'm a Great Fit (expand on these points):
{unique_strengths}

The cover letter should:
1. Be professional and enthusiastic.
2. Explicitly highlight the skills and experiences from the applicant's resume that match the job description.
3. Express genuine interest in the company and the specific role.
4. Be concise and to the point.
5. Sound unique and tailored, not generic.
6. {style_instructions}
7. {tone_instructions}
    """
    return prompt
