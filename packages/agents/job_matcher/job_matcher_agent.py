import logging
from typing import List, Dict, Any, Optional
import hashlib
from packages.agents.job_matcher.job_matcher_utils import (
    load_user_profile_data,
    calculate_skill_score,
    calculate_experience_score,
    calculate_education_score,
    calculate_preference_score,
    calculate_opportunity_score,
    calculate_culture_score,
)

class JobMatcherAgent:
    """
    Matches processed job listings to the user's resume data and identifies the most relevant job opportunities.

    Args:
        db: Database/session dependency.
        logger: Logger instance for dependency injection and testability.
    """
    _match_cache: Dict[str, List[Dict[str, Any]]] = {}

    def __init__(self, db: Any, logger: Optional[logging.Logger] = None) -> None:
        self.db = db
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.user_profile = self._load_user_profile()
        self.logger.info("JobMatcherAgent initialized.")

    def _load_user_profile(self) -> Dict[str, Any]:
        """
        Load the user's profile data from the database.

        Returns:
            User profile dictionary.
        """
        profile = load_user_profile_data(self.db)
        if not profile:
            self.logger.error("Failed to load user profile. Please ensure it exists and is correctly formatted.")
        else:
            self.logger.info("User profile loaded successfully.")
        return profile

    def match_jobs(self, processed_job_listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Compare user profile with job listings to calculate compatibility scores and identify top matches.

        Args:
            processed_job_listings: List of job listings (dicts) to match against the user profile.

        Returns:
            List of top 3-5 matched job listings with compatibility scores and details.
        """
        self.logger.info(f"Starting job matching for {len(processed_job_listings)} listings")

        if not self.user_profile:
            self.logger.error("No user profile available for matching")
            return []

        # Caching: hash user profile and job listings
        cache_key = hashlib.sha256((str(self.user_profile) + str(processed_job_listings)).encode('utf-8')).hexdigest()
        if cache_key in self._match_cache:
            self.logger.info("Returning cached job matches.")
            return self._match_cache[cache_key]

        matched_jobs: List[Dict[str, Any]] = []
        user_skills = set(self.user_profile.get("skills", []))
        user_experience = sum(int(exp.get("years", 0)) for exp in self.user_profile.get("experience", []))
        user_education = set(edu.get("degree") for edu in self.user_profile.get("education", []) if edu.get("degree"))
        user_preferences = self.user_profile.get("preferences", {})
        user_culture = self.user_profile.get("culture", {})

        for job in processed_job_listings:
            job["match_details"] = {
                "missing_skills": [],
                "missing_qualifications": [],
                "opportunity_score": 0,
                "culture_score": 0,
            }

            try:
                # 1. Skill Matching (50% of total score)
                job_skills = set(job.get("required_skills", []))
                skill_score, missing_skills = calculate_skill_score(user_skills, job_skills)
                job["match_details"]["missing_skills"] = missing_skills

                # 2. Experience Matching (20% of total score)
                job_experience = job.get("required_experience", 0)
                experience_score, missing_experience_qual = calculate_experience_score(user_experience, job_experience)
                if missing_experience_qual:
                    job["match_details"]["missing_qualifications"].append(missing_experience_qual)

                # 3. Education Matching (15% of total score)
                job_education = set(job.get("required_education", []))
                education_score, missing_education_qual = calculate_education_score(user_education, job_education)
                if missing_education_qual:
                    job["match_details"]["missing_qualifications"].append(missing_education_qual)

                # 4. Preference Matching (15% of total score)
                preference_score = calculate_preference_score(user_preferences, job)

                # 5. Company Culture Matching (10 points out of 100)
                job_culture = job.get("culture", {})
                culture_score = calculate_culture_score(user_culture, job_culture)
                job["match_details"]["culture_score"] = culture_score

                # 6. Opportunity Score (separate metric)
                opportunity_score = calculate_opportunity_score(job)
                job["match_details"]["opportunity_score"] = opportunity_score

                # Calculate total compatibility score (0-100)
                total_score = (
                    skill_score + experience_score + education_score + preference_score + culture_score
                )
                job["compatibility_score"] = round(total_score)

                matched_jobs.append(job)
                self.logger.debug(
                    f"Scored job: {job.get('title')} - Compatibility: {job['compatibility_score']}, Opportunity: {opportunity_score}, Culture: {culture_score}"
                )
            except Exception as e:
                self.logger.exception(f"Error scoring job {job.get('title', 'N/A')}: {e}")

        # Filter and rank jobs
        matched_jobs = [job for job in matched_jobs if job["compatibility_score"] >= 50]
        matched_jobs.sort(
            key=lambda x: (
                -x["compatibility_score"],
                -x["match_details"]["opportunity_score"],
            )
        )

        # Select top 3-5 jobs
        top_jobs = matched_jobs[:5]

        self.logger.info(f"Found {len(top_jobs)} highly compatible jobs")
        self._match_cache[cache_key] = top_jobs
        return top_jobs


if __name__ == "__main__":
    from packages.utilities.logging_utils import setup_logging
    setup_logging()
    matcher = JobMatcherAgent(None)
    # Example usage: see previous main block for details
