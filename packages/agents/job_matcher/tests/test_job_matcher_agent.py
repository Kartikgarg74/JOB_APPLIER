import unittest
import os
import sys

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, project_root)

print(f"Project Root: {project_root}")
print(f"Current Working Directory: {os.getcwd()}")
print(f"Sys Path: {sys.path}")

from packages.agents.job_matcher.job_matcher_agent import JobMatcherAgent
from packages.common_types.common_types import JobListing, ResumeData

class TestJobMatcherAgent(unittest.TestCase):

    def setUp(self):
        self.agent = JobMatcherAgent()

    def test_match_job_valid_input(self):
        processed_job_listings = [
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "location": "Remote",
                "description": "Develop and maintain software.",
                "required_skills": ["Python", "Java"],
                "required_experience": 3,
                "required_education": ["B.S. Computer Science"],
                "salary": 0.7,
                "growth_potential": 0.8,
                "company_reputation": 0.9,
                "benefits": 0.85,
            }
        ]
        matched_jobs = self.agent.match_jobs(processed_job_listings)
        self.assertIsInstance(matched_jobs, list)
        self.assertGreater(len(matched_jobs), 0)
        self.assertIn('compatibility_score', matched_jobs[0])
        self.assertGreaterEqual(matched_jobs[0]['compatibility_score'], 0)
        self.assertLessEqual(matched_jobs[0]['compatibility_score'], 100)

    def test_match_job_no_match(self):
        processed_job_listings = [
            {
                "title": "Data Scientist",
                "company": "Data Co",
                "location": "On-site",
                "description": "Analyze data.",
                "required_skills": ["R", "SQL"],
                "required_experience": 2,
                "required_education": ["M.S. Statistics"],
                "salary": 0.6,
                "growth_potential": 0.7,
                "company_reputation": 0.8,
                "benefits": 0.75,
            }
        ]
        matched_jobs = self.agent.match_jobs(processed_job_listings)
        self.assertIsInstance(matched_jobs, list)
        self.assertEqual(len(matched_jobs), 0)

    def test_match_job_empty_input(self):
        processed_job_listings = []
        matched_jobs = self.agent.match_jobs(processed_job_listings)
        self.assertIsInstance(matched_jobs, list)
        self.assertEqual(len(matched_jobs), 0)

    def test_match_job_partial_match(self):
        processed_job_listings = [
            {
                "title": "Frontend Developer",
                "company": "Web Solutions",
                "location": "Hybrid",
                "description": "Build UIs.",
                "required_skills": ["JavaScript", "React"],
                "required_experience": 1,
                "required_education": ["B.A. Design"],
                "salary": 0.5,
                "growth_potential": 0.6,
                "company_reputation": 0.7,
                "benefits": 0.65,
            }
        ]
        matched_jobs = self.agent.match_jobs(processed_job_listings)
        self.assertIsInstance(matched_jobs, list)
        self.assertGreater(len(matched_jobs), 0)
        self.assertIn('compatibility_score', matched_jobs[0])
        self.assertGreater(matched_jobs[0]['compatibility_score'], 0)
        self.assertLess(matched_jobs[0]['compatibility_score'], 100)

if __name__ == '__main__':
    unittest.main()