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
        self.assertEqual(result['overall_ats_score'], 0.0)

    def test_score_resume_empty_input(self):
        job_description = ""
        resume_text = ""
        result = self.agent.score_ats(ResumeData(raw_text=resume_text), job_description)
        self.assertIsInstance(result, dict)
        self.assertIn('overall_ats_score', result)
        self.assertIsInstance(result['overall_ats_score'], float)
        self.assertEqual(result['overall_ats_score'], 0.0)

    def test_score_resume_partial_match(self):
        job_description = "Looking for a Python developer with Flask experience."
        resume_text = "Experienced Python developer."
        result = self.agent.score_ats(ResumeData(raw_text=resume_text), job_description)
        self.assertIsInstance(result, dict)
        self.assertIn('overall_ats_score', result)
        self.assertIsInstance(result['overall_ats_score'], float)
        self.assertGreater(result['overall_ats_score'], 0.0)
        self.assertLess(result['overall_ats_score'], 100.0)

if __name__ == '__main__':
    unittest.main()