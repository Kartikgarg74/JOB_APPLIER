import logging
from typing import List, Dict, Any
import logging
from packages.agents.job_matcher.job_matcher_utils import (
    load_user_profile_data,
    calculate_skill_score,
    calculate_experience_score,
    calculate_education_score,
    calculate_preference_score,
    calculate_opportunity_score,
    calculate_culture_score,  # NEW
)

logger = logging.getLogger(__name__)


class JobMatcherAgent:
    """
    [CONTEXT] Matches processed job listings to the user's resume data.
    [PURPOSE] Identifies the most relevant job opportunities based on skills, experience, and preferences.
    """

    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)
        self.user_profile = self._load_user_profile()
        self.logger.info("JobMatcherAgent initialized.")

    def _load_user_profile(self) -> Dict[str, Any]:
        profile = load_user_profile_data(self.db)
        if not profile:
            self.logger.error(
                "Failed to load user profile. Please ensure it exists and is correctly formatted."
            )
        else:
            self.logger.info("User profile loaded successfully.")
        return profile

    def match_jobs(
        self, processed_job_listings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        [CONTEXT] Compares user profile with job listings to calculate compatibility scores.
        [PURPOSE] Identifies top 3-5 job matches based on skills, qualifications, preferences, and company culture.
        """
        self.logger.info(
            f"Starting job matching for {len(processed_job_listings)} listings"
        )

        if not self.user_profile:
            self.logger.error("No user profile available for matching")
            return []

        matched_jobs = []
        user_skills = set(self.user_profile.get("skills", []))
        user_experience = sum(int(exp.get("years", 0)) for exp in self.user_profile.get("experience", []))
        user_education = set(edu.get("degree") for edu in self.user_profile.get("education", []) if edu.get("degree"))
        user_preferences = self.user_profile.get("preferences", {})
        user_culture = self.user_profile.get("culture", {})  # NEW: expects dict of culture prefs

        for job in processed_job_listings:
            job["match_details"] = {
                "missing_skills": [],
                "missing_qualifications": [],
                "opportunity_score": 0,
                "culture_score": 0,  # NEW
            }

            # Initialize score components
            skill_score = 0
            experience_score = 0
            education_score = 0
            preference_score = 0
            opportunity_score = 0
            culture_score = 0  # NEW

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
            job_culture = job.get("culture", {})  # expects dict of culture attributes
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

        # Filter and rank jobs
        matched_jobs = [job for job in matched_jobs if job["compatibility_score"] >= 50]
        matched_jobs.sort(
            key=lambda x: (
                -x["compatibility_score"],  # Primary sort by compatibility
                -x["match_details"][
                    "opportunity_score"
                ],  # Secondary sort by opportunity
            )
        )

        # Select top 3-5 jobs
        top_jobs = matched_jobs[:5]

        self.logger.info(f"Found {len(top_jobs)} highly compatible jobs")
        return top_jobs


if __name__ == "__main__":
    from packages.utilities.logging_utils import setup_logging

    setup_logging()

    matcher = JobMatcherAgent()

    # Dummy processed job listings with new fields
    dummy_processed_job_listings = [
        {
            "title": "Senior Python Developer",
            "company": "Tech Solutions",
            "location": "Remote",
            "description": "Develop and maintain backend services using Python, Django, and PostgreSQL.",
            "url": "http://example.com/job1",
            "required_skills": ["Python", "Django", "PostgreSQL", "AWS"],
            "required_experience": 5,
            "required_education": ["B.S. Computer Science"],
            "salary": 0.8,
            "growth_potential": 0.9,
            "company_reputation": 0.85,
            "benefits": 0.7,
        },
        {
            "title": "Data Scientist",
            "company": "Data Insights Inc.",
            "location": "New York, NY",
            "description": "Build and deploy machine learning models, analyze large datasets.",
            "url": "http://example.com/job2",
            "required_skills": ["Python", "R", "Machine Learning", "SQL", "Statistics"],
            "required_experience": 3,
            "required_education": ["M.S. Data Science", "Ph.D. Statistics"],
            "salary": 0.7,
            "growth_potential": 0.8,
            "company_reputation": 0.9,
            "benefits": 0.8,
        },
        {
            "title": "Junior Frontend Developer",
            "company": "Web Innovations",
            "location": "San Francisco, CA",
            "description": "Develop responsive user interfaces using React and JavaScript.",
            "url": "http://example.com/job3",
            "required_skills": ["JavaScript", "React", "HTML", "CSS"],
            "required_experience": 1,
            "required_education": ["B.S. Web Development"],
            "salary": 0.5,
            "growth_potential": 0.7,
            "company_reputation": 0.75,
            "benefits": 0.6,
        },
        {
            "title": "DevOps Engineer",
            "company": "Cloud Solutions",
            "location": "Remote",
            "description": "Manage CI/CD pipelines and cloud infrastructure on Azure.",
            "url": "http://example.com/job4",
            "required_skills": ["Azure", "Docker", "Kubernetes", "CI/CD"],
            "required_experience": 4,
            "required_education": ["B.S. Computer Engineering"],
            "salary": 0.85,
            "growth_potential": 0.95,
            "company_reputation": 0.92,
            "benefits": 0.85,
        },
    ]

    print("\n--- Matching Jobs ---")
    matched_jobs = matcher.match_jobs(dummy_processed_job_listings)

    if matched_jobs:
        for job in matched_jobs:
            print(f"\nMatched Job: {job['title']} at {job['company']}")
            print(f"  Compatibility Score: {job['compatibility_score']}")
            print(
                f"  Opportunity Score: {job['match_details']['opportunity_score']:.2f}"
            )
            print(
                f"  Missing Skills: {', '.join(job['match_details']['missing_skills']) if job['match_details']['missing_skills'] else 'None'}"
            )
            print(
                f"  Missing Qualifications: {', '.join(job['match_details']['missing_qualifications']) if job['match_details']['missing_qualifications'] else 'None'}"
            )
    else:
        print("No jobs matched the user profile.")

    print("\n--- Matching complete ---")
