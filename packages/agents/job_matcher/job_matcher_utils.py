from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session
from packages.database.user_data_model import UserDatabase
import difflib
import hashlib
import time

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _st_model = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    _st_model = None
    np = None

_embedding_cache = {}

_skill_taxonomy = {
    "Python": ["Programming", "Scripting"],
    "JavaScript": ["Programming", "Frontend"],
    "Django": ["Python", "Web Framework"],
    "React": ["JavaScript", "Frontend"],
    "AWS": ["Cloud", "DevOps"],
    "Docker": ["DevOps"],
    "Kubernetes": ["DevOps"],
    # ... add more as needed
}

_experience_levels = {
    "intern": 0,
    "junior": 1,
    "mid": 2,
    "senior": 3,
    "lead": 4,
    "principal": 5
}

def normalize_skill(skill: str) -> str:
    return skill.strip().lower()

def expand_skills(skills: List[str]) -> set:
    """Expand skills using the taxonomy for hierarchical matching."""
    expanded = set()
    for skill in skills:
        norm = normalize_skill(skill)
        expanded.add(norm)
        for parent in _skill_taxonomy.get(skill, []):
            expanded.add(normalize_skill(parent))
    return expanded

def get_text_embedding(text: str, max_retries: int = 3) -> Optional[Any]:
    """Get or compute the embedding for a given text, using cache. Handles rate limits."""
    if not _st_model or not np:
        return None
    key = hashlib.sha256(text.encode('utf-8')).hexdigest()
    if key in _embedding_cache:
        return _embedding_cache[key]
    for attempt in range(max_retries):
        try:
            emb = _st_model.encode([text])[0]
            _embedding_cache[key] = emb
            return emb
        except Exception as e:
            if 'rate limit' in str(e).lower() or 'too many requests' in str(e).lower():
                time.sleep(2 ** attempt)
            else:
                break
    return None

def cosine_similarity(vec1, vec2) -> float:
    if not np or vec1 is None or vec2 is None:
        return 0.0
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

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
    [PURPOSE] Quantifies how well a job aligns with user's specified preferences, including fuzzy location matching and remote/hybrid logic.
    """
    preference_score = 0
    MAX_PREFERENCE_SCORE = 15

    # Enhanced Location preference (fuzzy and remote/hybrid logic)
    job_location = job.get("location", "")
    user_job_locations = user_preferences.get("job_locations", [])
    job_remote = job.get("remote")
    user_remote_preference = user_preferences.get("remote")
    location_score = 0
    if user_job_locations:
        for user_loc in user_job_locations:
            # Exact match
            if job_location == user_loc:
                location_score = MAX_PREFERENCE_SCORE * 0.4
                break
            # Fuzzy match (city/region similarity)
            similarity = difflib.SequenceMatcher(None, job_location.lower(), user_loc.lower()).ratio()
            if similarity > 0.8:
                location_score = MAX_PREFERENCE_SCORE * 0.3  # Partial for close match
                break
            elif similarity > 0.6:
                location_score = MAX_PREFERENCE_SCORE * 0.2  # Lesser for somewhat close
        # Remote/hybrid logic
        if (job_remote or ("remote" in job_location.lower() or "hybrid" in job_location.lower())) and (user_remote_preference or "remote" in [l.lower() for l in user_job_locations]):
            location_score = max(location_score, MAX_PREFERENCE_SCORE * 0.4)  # Full points for remote match
    preference_score += location_score

    # Job type preference (e.g., Full-time, Contract)
    job_type = job.get("job_type")
    user_job_types = user_preferences.get("job_types", [])
    if job_type and user_job_types and job_type in user_job_types:
        preference_score += MAX_PREFERENCE_SCORE * 0.3  # 30% of preference score for job type

    # Salary range preference (robust comparison)
    job_salary_normalized = job.get("salary")  # 0-1, where 1 = $200,000
    user_salary_range_str = user_preferences.get("salary_range")
    if job_salary_normalized is not None and user_salary_range_str:
        try:
            min_salary_str, max_salary_str = user_salary_range_str.replace("$", "").replace(",", "").split(" - ")
            min_salary = int(min_salary_str)
            max_salary = int(max_salary_str)
            job_salary_actual = job_salary_normalized * 200000  # Assume 1.0 = $200,000
            (min_salary + max_salary) / 2
            if min_salary <= job_salary_actual <= max_salary:
                preference_score += MAX_PREFERENCE_SCORE * 0.2  # 20% for salary, perfect match
            elif job_salary_actual > max_salary:
                preference_score += MAX_PREFERENCE_SCORE * 0.2  # Still a match if above
            elif min_salary - 10000 <= job_salary_actual < min_salary:
                preference_score += MAX_PREFERENCE_SCORE * 0.1  # Partial if within $10k below min
        except ValueError:
            pass

    # Remote preference (already handled above, but keep for backward compatibility)
    if user_remote_preference is not None and job_remote == user_remote_preference:
        preference_score += MAX_PREFERENCE_SCORE * 0.1  # 10% for remote preference

    return min(preference_score, MAX_PREFERENCE_SCORE)


def calculate_culture_score(user_culture: Dict[str, Any], job_culture: Dict[str, Any]) -> float:
    """
    [CONTEXT] Calculates the company culture matching score.
    [PURPOSE] Quantifies how well a user's culture preferences align with the company's culture attributes.
    [SCHEMA] Both user_culture and job_culture are dicts with keys like 'work_life_balance', 'innovation', 'diversity', 'collaboration', 'growth', each 0-1.
    [RETURNS] Score out of 10.
    """
    if not user_culture or not job_culture:
        return 0.0
    keys = set(user_culture.keys()) & set(job_culture.keys())
    if not keys:
        return 0.0
    score = 0.0
    for k in keys:
        # Score is higher the closer the values are
        diff = abs(float(user_culture[k]) - float(job_culture[k]))
        score += max(0, 1 - diff)  # 1 if perfect match, 0 if opposite
    return round((score / len(keys)) * 10, 2)  # Out of 10

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

def experience_level_to_numeric(level: str) -> int:
    return _experience_levels.get(level.lower(), -1)

def compare_experience_levels(user_level: str, job_level: str) -> float:
    """Return 1.0 if user meets or exceeds job level, else a fraction."""
    user_num = experience_level_to_numeric(user_level)
    job_num = experience_level_to_numeric(job_level)
    if user_num == -1 or job_num == -1:
        return 0.0
    return 1.0 if user_num >= job_num else user_num / (job_num + 0.01)
