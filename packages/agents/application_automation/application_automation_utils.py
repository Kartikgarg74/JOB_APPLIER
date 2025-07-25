"""
This module may use environment variables for credentials (e.g., LINKEDIN_EMAIL, LINKEDIN_PASSWORD, INDEED_EMAIL, INDEED_PASSWORD) for automation agents.
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from packages.database.user_data_model import UserDatabase

def load_user_data(db: Session) -> Dict[str, Any]:
    """
    [CONTEXT] Loads user profile data from user_profile.json.
    [PURPOSE] Provides user information for form filling.
    """
    user_db = UserDatabase()
    user = user_db.get_user_by_id(db, 1) # Assuming user_id 1 for now
    if user:
        return {
            "name": user.full_name,
            "email": user.email,
            "phone": user.phone_number,
            "address": user.address,
            "linkedin": user.linkedin_profile,
            "github": user.github_profile,
            "portfolio": user.portfolio_url,
            "resume_path": user.resume_path,
            "cover_letter_path": user.cover_letter_path,
        }
    return {}
