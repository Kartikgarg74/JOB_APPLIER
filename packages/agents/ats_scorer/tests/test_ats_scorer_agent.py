import unittest
import os
import sys

# Add the parent directory to the sys.path to allow imports of modules at the same level
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, project_root)

print(f"Project Root: {project_root}")
print(f"Current Working Directory: {os.getcwd()}")
print(f"Sys Path: {sys.path}")

from packages.agents.ats_scorer.ats_scorer_agent import ATSScorerAgent
from packages.common_types.common_types import ResumeData

class TestATSScorerAgent(unittest.TestCase):

    def setUp(self):
        self.agent = ATSScorerAgent()

    def test_score_resume_valid_input(self):
        job_description = "We are looking for a software engineer with Python and Java skills."
        resume_text = "Experienced developer with strong Python and Java skills."
        result = self.agent.score_ats(ResumeData(raw_text=resume_text), job_description)
        self.assertIsInstance(result, dict)
        self.assertIn('overall_ats_score', result)
        self.assertIsInstance(result['overall_ats_score'], float)
        self.assertGreaterEqual(result['overall_ats_score'], 0.0)
        self.assertLessEqual(result['overall_ats_score'], 100.0)

    def test_score_resume_no_match(self):
        job_description = "We are looking for a software engineer with C++ skills."
        resume_text = "Experienced developer with strong Python and Java skills."
        result = self.agent.score_ats(ResumeData(raw_text=resume_text), job_description)
        self.assertIsInstance(result, dict)
        self.assertIn('overall_ats_score', result)
        self.assertIsInstance(result['overall_ats_score'], float)
        # Formatting score only (should be 30.0)
        self.assertEqual(result['overall_ats_score'], 30.0)

    def test_score_resume_empty_input(self):
        job_description = ""
        resume_text = ""
        result = self.agent.score_ats(ResumeData(raw_text=resume_text), job_description)
        self.assertIsInstance(result, dict)
        self.assertIn('overall_ats_score', result)
        self.assertIsInstance(result['overall_ats_score'], float)
        # Formatting score only (should be 30.0)
        self.assertEqual(result['overall_ats_score'], 30.0)

    def test_score_resume_partial_match(self):
        job_description = "Looking for a Python developer with Flask experience."
        resume_text = "Experienced Python developer."
        result = self.agent.score_ats(ResumeData(raw_text=resume_text), job_description)
        self.assertIsInstance(result, dict)
        self.assertIn('overall_ats_score', result)
        self.assertIsInstance(result['overall_ats_score'], float)
        self.assertGreater(result['overall_ats_score'], 0.0)
        self.assertLess(result['overall_ats_score'], 100.0)

    def test_score_resume_full_features(self):
        job_description = "We are looking for a Python developer with AWS, SQL, and Docker experience. Must have strong communication skills."
        resume_data = ResumeData(
            raw_text="John Doe\nPython Developer\nSkills: Python, SQL, Docker, Communication\nExperience: Developed cloud solutions using AWS and Docker. Strong communicator.",
            personal_details={"name": "John Doe", "email": "john@example.com"},
            summary="Python developer with cloud and DevOps experience.",
            skills=["Python", "SQL", "Docker", "Communication"],
            experience=[
                {"title": "Cloud Engineer", "company": "CloudCo", "years": "2021-Present", "description": "Built solutions on AWS and Docker."}
            ],
            education=[{"degree": "B.S. Computer Science", "university": "Tech U", "years": "2020"}]
        )
        agent = self.agent
        result = agent.score_ats(resume_data, job_description, industry="tech")
        self.assertIn('keyword_density', result)
        self.assertIn('formatting_issues', result)
        self.assertIn('benchmark_percentile', result)
        self.assertIsInstance(result['keyword_density'], dict)
        self.assertIsInstance(result['formatting_issues'], dict)
        self.assertIsInstance(result['benchmark_percentile'], str)
        # Check that density for 'python' is at least 1
        self.assertGreaterEqual(result['keyword_density'].get('python', 0), 1)
        # Check percentile is a known value
        self.assertIn(result['benchmark_percentile'], ['Top 5%', 'Top 10%', 'Top 20%', 'Top 40%', 'Below 40%'])

if __name__ == '__main__':
    unittest.main()
