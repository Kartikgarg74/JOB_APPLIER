from typing import Optional, List, Dict, Any
import re

from typing import Dict, List, Optional

def extract_personal_details(raw_text: str) -> Dict[str, Optional[str]]:
    """
    [CONTEXT] Extracts personal details (name, email, phone) from raw resume text.
    [PURPOSE] Provides a structured dictionary of personal contact information.
    """
    name_match = re.search(r'(?:Name:\s*)?([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,5})(?:\n|$)', raw_text)
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", raw_text)
    phone_match = re.search(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", raw_text)

    return {
        "name": name_match.group(1).strip() if name_match else None,
        "email": email_match.group(0).strip() if email_match else None,
        "phone": phone_match.group(0).strip() if phone_match else None,
        "linkedin": "",
        "github": "",
        "portfolio": "",
    }

def extract_skills(raw_text: str) -> List[str]:
    """
    [CONTEXT] Extracts skills from raw resume text based on a simple pattern.
    [PURPOSE] Provides a list of skills mentioned in the resume.
    """
    skills_match = re.search(r"Skills:\s*(.*)", raw_text, re.IGNORECASE)
    if skills_match:
        return [s.strip() for s in skills_match.group(1).split(',') if s.strip()]
    return []