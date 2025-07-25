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

class DummyDB:
    pass

class TestJobMatcherAgent(unittest.TestCase):

    def setUp(self):
        self.agent = JobMatcherAgent(DummyDB())
        self.agent.user_profile = {}  # Prevent DB call, tests set this directly

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

    def test_salary_comparison(self):
        # User prefers $80,000 - $120,000 (simulate via agent's user_profile)
        self.agent.user_profile = {
            "skills": ["Python", "Java"],
            "experience": [{"years": 3}],
            "education": [{"degree": "B.S. Computer Science"}],
            "preferences": {
                "job_locations": ["Remote"],
                "salary_range": "$80,000 - $120,000",
                "job_types": ["Full-time"]
            },
            "culture": {"work_life_balance": 0.8, "innovation": 0.7}
        }
        # Salary below, within, and above range
        jobs = [
            {"title": "Low Salary", "company": "A", "location": "Remote", "required_skills": ["Python"], "required_experience": 3, "required_education": ["B.S. Computer Science"], "salary": 0.3},  # $60k
            {"title": "In Range", "company": "B", "location": "Remote", "required_skills": ["Python"], "required_experience": 3, "required_education": ["B.S. Computer Science"], "salary": 0.5},  # $100k
            {"title": "Above Range", "company": "C", "location": "Remote", "required_skills": ["Python"], "required_experience": 3, "required_education": ["B.S. Computer Science"], "salary": 0.7},  # $140k
        ]
        results = self.agent.match_jobs(jobs)
        titles = [job['title'] for job in results]
        self.assertIn("In Range", titles)
        self.assertIn("Above Range", titles)
        # Low Salary may be filtered out if score < 50

    def test_culture_matching(self):
        self.agent.user_profile = {
            "skills": ["Python"],
            "experience": [{"years": 2}],
            "education": [{"degree": "B.S. Computer Science"}],
            "preferences": {"job_locations": ["Remote"], "salary_range": "$50,000 - $100,000", "job_types": ["Full-time"]},
            "culture": {"work_life_balance": 1.0, "innovation": 0.5, "diversity": 0.8}
        }
        jobs = [
            {"title": "Perfect Culture", "company": "A", "location": "Remote", "required_skills": ["Python"], "required_experience": 2, "required_education": ["B.S. Computer Science"], "salary": 0.5, "culture": {"work_life_balance": 1.0, "innovation": 0.5, "diversity": 0.8}},
            {"title": "Partial Culture", "company": "B", "location": "Remote", "required_skills": ["Python"], "required_experience": 2, "required_education": ["B.S. Computer Science"], "salary": 0.5, "culture": {"work_life_balance": 0.7, "innovation": 0.7, "diversity": 0.6}},
            {"title": "Poor Culture", "company": "C", "location": "Remote", "required_skills": ["Python"], "required_experience": 2, "required_education": ["B.S. Computer Science"], "salary": 0.5, "culture": {"work_life_balance": 0.0, "innovation": 1.0, "diversity": 0.0}},
        ]
        results = self.agent.match_jobs(jobs)
        titles = [job['title'] for job in results]
        self.assertIn("Perfect Culture", titles)
        self.assertIn("Partial Culture", titles)
        # Poor Culture may be filtered out if score < 50

if __name__ == '__main__':
    unittest.main()
