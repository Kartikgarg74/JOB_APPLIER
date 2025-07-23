# packages/types/common_types.py

from typing import List, Dict, Any, TypedDict, Optional


class ResumeData(TypedDict):
    raw_text: str
    personal_details: Dict[str, Any]
    summary: str
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: List[str]
    certifications: List[str]
    projects: List[Dict[str, Any]]
    awards: List[str]
    keywords: List[str]
    location: str
    # Add more fields as needed


class JobListing(TypedDict):
    job_id: str
    title: str
    company: str
    description: str
    requirements: str
    application_url: str
    location: str
    job_type: Optional[str]  # e.g., 'full-time', 'part-time', 'contract'
    # Add more fields as needed


class UserProfile(TypedDict):
    preferred_job_roles: List[str]
    location_preferences: Dict[str, Any]  # e.g., {'remote': True, 'on_site': ['NYC']}
    resume_path: str
    cover_letter_template: Optional[str]
    skill_keywords: List[str]
    ats_scoring_weights: Dict[str, float]


class ATSResult(TypedDict):
    score: float
    recommendations: List[str]


class ApplicationStatus(TypedDict):
    job_id: str
    status: str  # e.g., 'applied', 'interview', 'rejected', 'interview_scheduled', 'offer_received', 'rejected'
    date_applied: str
    application_url: str
    confirmation_number: Optional[str]
    follow_up_date: Optional[str]  # Date for next follow-up
    response_received_date: Optional[str]  # Date a response was received
    notes: Optional[str]
    resume_version: Optional[
        str
    ]  # Version or identifier of the resume used for this application


# Add more common types as the project evolves
