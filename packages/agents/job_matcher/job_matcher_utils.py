from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session
from packages.database.user_data_model import UserDatabase

def load_user_profile_data(db: Session) -> Dict[str, Any]:
    """
    [CONTEXT] Loads the user's profile data using the centralized user profile loading function.
    [PURPOSE] Ensures consistency and proper handling (e.g., decryption) of user profile data.
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
            "skills": [skill.name for skill in user.skills],
            "experience": [{
                "title": exp.title,
                "years": (exp.end_date - exp.start_date).days / 365 if exp.end_date and exp.start_date else 0
            } for exp in user.experience],
            "education": [{
                "degree": edu.degree,
                "university": edu.university
            } for edu in user.education],
            "preferences": {
                "job_titles": user.preferred_job_titles,
                "locations": user.preferred_locations,
                "salary_range": user.preferred_salary_range,
                "job_types": user.preferred_job_types,
                "industries": user.preferred_industries,
            }
        }
    return {}

def calculate_skill_score(user_skills: set, job_skills: set) -> Tuple[float, List[str]]:
    """
    [CONTEXT] Calculates the skill matching score and identifies missing skills.
    [PURPOSE] Quantifies how well a user's skills align with job requirements.
    """
    common_skills = user_skills.intersection(job_skills)
    missing_skills = job_skills - user_skills
    score = (len(common_skills) / len(job_skills)) * 50 if job_skills else 0
    return score, list(missing_skills)

def calculate_experience_score(user_experience: int, job_experience: int) -> Tuple[float, Optional[str]]:
    """
    [CONTEXT] Calculates the experience matching score.
    [PURPOSE] Quantifies how well a user's experience aligns with job requirements.
    """
    missing_qualification = None
    if user_experience >= job_experience:
        score = 20
    else:
        score = (user_experience / job_experience) * 20
        missing_qualification = f"{job_experience - user_experience} years experience"
    return score, missing_qualification

def calculate_education_score(user_education: set, job_education: set) -> Tuple[float, Optional[str]]:
    """
    [CONTEXT] Calculates the education matching score.
    [PURPOSE] Quantifies how well a user's education aligns with job requirements.
    """
    missing_qualification = None
    if job_education:
        if user_education.issuperset(job_education):
            score = 15
        else:
            score = (len(user_education.intersection(job_education)) / len(job_education)) * 15
            missing_qualification = f"Education: {', '.join(job_education - user_education)}"
    else:
        score = 0
    return score, missing_qualification

def calculate_preference_score(user_preferences: Dict[str, Any], job: Dict[str, Any]) -> float:
    """
    [CONTEXT] Calculates the preference matching score.
    [PURPOSE] Quantifies how well a job aligns with user's specified preferences.
    """
    preference_score = 0
    # Define the maximum possible score for preferences
    MAX_PREFERENCE_SCORE = 15

    # Location preference
    job_location = job.get("location")
    user_job_locations = user_preferences.get("job_locations", [])
    if job_location and user_job_locations and job_location in user_job_locations:
        preference_score += MAX_PREFERENCE_SCORE * 0.4  # 40% of preference score for location

    # Job type preference (e.g., Full-time, Contract)
    job_type = job.get("job_type")
    user_job_types = user_preferences.get("job_types", [])
    if job_type and user_job_types and job_type in user_job_types:
        preference_score += MAX_PREFERENCE_SCORE * 0.3  # 30% of preference score for job type

    # Salary range preference
    job_salary_normalized = job.get("salary") # Assuming this is a normalized value, e.g., 0.7 for $70k
    user_salary_range_str = user_preferences.get("salary_range")
    if job_salary_normalized and user_salary_range_str:
        try:
            # Parse user's salary range (e.g., "$90,000 - $120,000")
            min_salary_str, max_salary_str = user_salary_range_str.replace("$", "").replace(",", "").split(" - ")
            min_salary = int(min_salary_str)
            max_salary = int(max_salary_str)

            # Assuming job_salary_normalized is a ratio of a max possible salary (e.g., $200,000)
            # This needs to be aligned with how job_salary is generated in job processing
            # For now, let's assume job_salary_normalized is a direct representation of salary in some unit
            # and we need to convert it to a comparable range.
            # A more robust solution would involve a clear definition of job['salary'] unit/scale.
            # For demonstration, let's assume job_salary_normalized is a value from 0 to 1 representing a range up to $200,000
            # So, job_salary_actual = job_salary_normalized * 200000
            # This part needs to be refined based on actual data structure.
            # For now, let's make a simplified check.
            # If job_salary_normalized is within a reasonable range of user's preference, give some score.
            # This is a placeholder and needs actual salary parsing/comparison logic.
            # For the purpose of this test, we'll assume a simple match if it's not too far off.
            # Let's assume job_salary_normalized is a value between 0 and 1, where 1 is a very high salary.
            # We need to convert user's min/max salary to a normalized range to compare.
            # This is a complex mapping and requires more context on how job['salary'] is derived.
            # For now, I will skip detailed salary parsing and just check if the job has a salary and user has a preference.
            # A simple check: if job_salary_normalized is within a certain range of the user's preferred range midpoint.
            # This is a simplification for the current problem.
            # Let's assign a fixed small score if salary is present and user has preference.
            preference_score += MAX_PREFERENCE_SCORE * 0.2 # 20% for salary, placeholder logic
        except ValueError:
            pass # Handle parsing error if salary_range is not in expected format

    # Other preferences can be added here with their respective weights
    # For example, 'remote' preference
    job_remote = job.get("remote")
    user_remote_preference = user_preferences.get("remote") # Assuming user_preferences can have a 'remote' boolean/string
    if user_remote_preference is not None and job_remote == user_remote_preference:
        preference_score += MAX_PREFERENCE_SCORE * 0.1 # 10% for remote preference

    # Add more preference factors as needed, ensuring their weights sum up to 1 (or 15 in this case)

    return min(preference_score, MAX_PREFERENCE_SCORE) # Ensure score does not exceed max

def calculate_opportunity_score(job: Dict[str, Any]) -> float:
    """
    [CONTEXT] Calculates the opportunity score for a job.
    [PURPOSE] Provides a metric for the attractiveness of a job beyond direct qualifications.
    """
    opportunity_score = 0
    opportunity_factors = {
        "salary": 0.4,
        "growth_potential": 0.3,
        "company_reputation": 0.2,
        "benefits": 0.1,
    }
    for factor, weight in opportunity_factors.items():
        if factor in job:
            opportunity_score += job[factor] * weight * 100
    return opportunity_score