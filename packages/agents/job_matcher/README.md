# Job Matcher Agent

## Purpose
The Job Matcher Agent identifies the most relevant job opportunities for a user based on their skills, experience, education, and preferences. It processes job listings and calculates a compatibility score to rank and present the best matches.

## Dependencies
- `packages/agents/job_matcher/job_matcher_utils` for utility functions related to scoring.
- Database connection for loading user profile data.

## Key Components
- `JobMatcherAgent`: The main class responsible for orchestrating the job matching process.
  - `__init__(self, db)`: Initializes the agent and loads the user's profile from the database.
  - `_load_user_profile(self)`: Private method to load the user's profile data.
  - `match_jobs(self, processed_job_listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]`: The core method that takes a list of processed job listings and returns a ranked list of matched jobs.

## Workflow
1. **Load User Profile**: Retrieves the user's skills, experience, education, and job preferences from the database.
2. **Iterate through Job Listings**: For each job listing:
   a. **Skill Matching**: Calculates a score based on the overlap between user skills and required job skills.
   b. **Experience Matching**: Scores based on the user's years of experience versus the job's requirements.
   c. **Education Matching**: Scores based on the user's educational background versus the job's requirements.
   d. **Preference Matching**: Scores based on how well the job aligns with the user's specified preferences (e.g., location, salary, growth potential).
   e. **Opportunity Score**: Calculates a separate metric indicating the overall attractiveness of the job (e.g., salary, growth, company reputation).
   f. **Total Compatibility Score**: Combines skill, experience, education, and preference scores into a single compatibility score (0-100).
3. **Filter and Rank**: Filters out jobs with a compatibility score below 50 and sorts the remaining jobs by compatibility score (descending) and then by opportunity score (descending).
4. **Select Top Matches**: Returns the top 3-5 most compatible job listings.

## Usage Example
```python
from packages.agents.job_matcher.job_matcher_agent import JobMatcherAgent
from packages.utilities.logging_utils import setup_logging

# Assuming 'db' is an initialized database connection object
# For testing purposes, you might mock this or use a dummy object
class MockDB:
    def get_user_profile(self):
        return {
            "skills": ["Python", "SQL", "Machine Learning"],
            "experience": [{"years": 5}],
            "education": [{"degree": "M.S. Data Science"}],
            "preferences": {"location": "Remote", "salary_min": 80000}
        }

setup_logging()
mock_db = MockDB()

matcher = JobMatcherAgent(mock_db)

processed_job_listings = [
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
    }
]

matched_jobs = matcher.match_jobs(processed_job_listings)

for job in matched_jobs:
    print(f"Matched Job: {job['title']} at {job['company']}")
    print(f"  Compatibility Score: {job['compatibility_score']}")
    print(f"  Missing Skills: {job['match_details']['missing_skills']}")
    print(f"  Opportunity Score: {job['match_details']['opportunity_score']}")
```

## Error Handling
The agent logs errors if the user profile cannot be loaded or if no compatible jobs are found. It returns an empty list if matching cannot proceed.

## Testing
To test the `JobMatcherAgent`, run `job_matcher_agent.py` directly. It contains an `if __name__ == "__main__":` block with example usage and dummy data.

## Contributing
When enhancing the job matching logic:
1. Update scoring algorithms in `job_matcher_utils.py`.
2. Add new criteria for matching (e.g., cultural fit, company size).
3. Ensure `_load_user_profile` is robust and handles various database states.