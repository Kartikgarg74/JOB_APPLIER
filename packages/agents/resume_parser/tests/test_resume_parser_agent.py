import unittest
from unittest.mock import MagicMock, patch
import logging

from packages.agents.resume_parser.resume_parser_agent import ResumeParserAgent
from packages.common_types.common_types import ResumeData
from packages.agents.resume_parser.resume_utils import extract_personal_details, extract_skills

# Suppress logging during tests for cleaner output
logging.disable(logging.CRITICAL)

class TestResumeParserAgent(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        self.agent = ResumeParserAgent(self.mock_db)

    def test_parse_resume_empty_text(self):
        # Test with empty resume text
        result = self.agent.parse_resume("")
        self.assertIsNone(result)

    def test_parse_resume_valid_text(self):
        # Test with valid resume text
        resume_text = "John Doe\njohn.doe@example.com\nSkills: Python, Java"
        result = self.agent.parse_resume(resume_text)
        self.assertIsInstance(result, dict)
        self.assertIn('raw_text', result)
        self.assertIn('personal_details', result)
        self.assertIn('skills', result)
        self.assertEqual(result['raw_text'], resume_text)
        self.assertIn('Python', result['skills'])
        self.assertIn('Java', result['skills'])
        self.assertEqual(result['personal_details']['name'], 'John Doe')
        self.assertEqual(result['personal_details']['email'], 'john.doe@example.com')

    @patch('packages.agents.resume_parser.resume_parser_agent.extract_personal_details')
    @patch('packages.agents.resume_parser.resume_parser_agent.extract_skills')
    def test_structure_resume_data(self, mock_extract_skills, mock_extract_personal_details):
        # Mock utility functions
        mock_extract_personal_details.return_value = {"name": "Jane Doe", "email": "jane.doe@example.com"}
        mock_extract_skills.return_value = ["C++", "SQL"]

        raw_text = "Jane Doe\njane.doe@example.com\nExperience: Developed software\nSkills: C++, SQL"
        result = self.agent._structure_resume_data(raw_text)

        self.assertIsInstance(result, dict)
        self.assertIn('raw_text', result)
        self.assertIn('personal_details', result)
        self.assertIn('skills', result)
        self.assertEqual(result['raw_text'], raw_text)
        self.assertEqual(result['personal_details']['name'], 'Jane Doe')
        self.assertIn('C++', result['skills'])
        self.assertIn('SQL', result['skills'])
        mock_extract_personal_details.assert_called_once_with(raw_text)
        mock_extract_skills.assert_called_once_with(raw_text)

    def test_extract_personal_details(self):
        # Test the standalone utility function
        text = "Name: Alice Smith\nEmail: alice@example.com\nPhone: 123-456-7890"
        details = extract_personal_details(text)
        self.assertEqual(details['name'], 'Alice Smith')
        self.assertEqual(details['email'], 'alice@example.com')
        self.assertEqual(details['phone'], '123-456-7890')

        text_no_email = "Name: Bob Johnson\nPhone: 987-654-3210"
        details_no_email = extract_personal_details(text_no_email)
        self.assertEqual(details_no_email['name'], 'Bob Johnson')
        self.assertIsNone(details_no_email.get('email'))

    def test_extract_skills(self):
        # Test the standalone utility function
        text = "Skills: Python, JavaScript, HTML, CSS\nExperience: Developed web apps."
        skills = extract_skills(text)
        self.assertIn('Python', skills)
        self.assertIn('JavaScript', skills)
        self.assertIn('HTML', skills)
        self.assertIn('CSS', skills)

        text_no_skills = "Just some random text without a skills section."
        skills_no_skills = extract_skills(text_no_skills)
        self.assertEqual(skills_no_skills, [])

if __name__ == '__main__':
    unittest.main()