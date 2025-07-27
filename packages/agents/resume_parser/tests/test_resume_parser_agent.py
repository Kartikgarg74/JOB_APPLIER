import unittest
import os
from unittest.mock import MagicMock, patch
import tempfile

from packages.agents.resume_parser.resume_parser_agent import ResumeParserAgent

class TestResumeParserAgent(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.parser = ResumeParserAgent(self.mock_db)

        # NOTE: Remove all dummy/test data. Use real data for tests only.

    def test_parse_resume_with_valid_text(self):
        """Test parsing a valid resume text."""
        result = self.parser.parse_resume(self.sample_resume)

        self.assertIsNotNone(result)
        self.assertIn('personal_details', result)
        self.assertIn('education', result)
        self.assertIn('experience', result)
        self.assertIn('skills', result)
        self.assertIn('projects', result)

        # Verify personal details
        personal_details = result['personal_details']
        self.assertEqual(personal_details['name'], 'John Doe')
        self.assertEqual(personal_details['email'], 'john.doe@example.com')
        self.assertEqual(personal_details['phone'], '(123) 456-7890')
        self.assertEqual(personal_details['github'], 'https://www.github.com/johndoe')
        self.assertEqual(personal_details['linkedin'], 'https://www.linkedin.com/in/johndoe')
        self.assertEqual(personal_details['location'], 'San Francisco')

        # Verify education
        education = result['education']
        self.assertEqual(len(education), 2)
        self.assertIn('Master of Science in Computer Science', education[0]['degree'])
        self.assertIn('2020', education[0]['year'])
        self.assertIn('3.8', education[0]['gpa'])

        # Verify experience
        experience = result['experience']
        self.assertEqual(len(experience), 2)
        self.assertIn('Senior Software Engineer', experience[0]['title_and_company'])
        self.assertIn('Present', experience[0]['date_range'])
        self.assertTrue(any('microservices' in resp for resp in experience[0]['responsibilities']))

        # Verify skills
        skills = result['skills']
        expected_skills = {'Python', 'JavaScript', 'Java', 'SQL', 'React', 'Node.js', 'Django', 'Flask',
                         'Git', 'Docker', 'Kubernetes', 'AWS'}
        self.assertTrue(all(skill in skills for skill in expected_skills))

        # Verify projects
        projects = result['projects']
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]['name'], 'AI-Powered Resume Parser')
        self.assertTrue(any('Python' in tech for tech in projects[0]['technologies']))
        self.assertTrue(any('accuracy' in desc for desc in projects[0]['description']))

    def test_parse_resume_with_empty_text(self):
        """Test parsing empty resume text."""
        result = self.parser.parse_resume("")
        self.assertIsNone(result)

    def test_parse_resume_with_minimal_text(self):
        """Test parsing minimal resume text."""
        minimal_resume = """
        Jane Smith
        jane.smith@email.com
        """
        result = self.parser.parse_resume(minimal_resume)
        self.assertIsNotNone(result)
        self.assertEqual(result['personal_details']['name'], 'Jane Smith')
        self.assertEqual(result['personal_details']['email'], 'jane.smith@email.com')

    @patch('packages.agents.resume_parser.resume_parser_agent.extract_text_from_pdf')
    def test_parse_resume_file_pdf(self, mock_extract_pdf):
        """Test parsing a PDF resume file."""
        # Set up mock to return sample resume text
        mock_extract_pdf.return_value = self.sample_resume

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', mode='wb', delete=False) as temp_file:
            temp_file.write(b"Dummy PDF content")
            temp_file_path = temp_file.name

        try:
            # Test the function
            result = self.parser.parse_resume_file(temp_file_path)

            # Verify results
            self.assertIsNotNone(result)
            mock_extract_pdf.assert_called_once_with(temp_file_path)
            self.assertEqual(result['personal_details']['name'], 'John Doe')
            self.assertEqual(result['personal_details']['email'], 'john.doe@example.com')
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    @patch('packages.agents.resume_parser.resume_parser_agent.extract_text_from_docx')
    def test_parse_resume_file_docx(self, mock_extract_docx):
        """Test parsing a DOCX resume file."""
        # Set up mock to return sample resume text
        mock_extract_docx.return_value = self.sample_resume

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.docx', mode='wb', delete=False) as temp_file:
            temp_file.write(b"Dummy DOCX content")
            temp_file_path = temp_file.name

        try:
            # Test the function
            result = self.parser.parse_resume_file(temp_file_path)

            # Verify results
            self.assertIsNotNone(result)
            mock_extract_docx.assert_called_once_with(temp_file_path)
            self.assertEqual(result['personal_details']['name'], 'John Doe')
            self.assertEqual(result['personal_details']['email'], 'john.doe@example.com')
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_parse_resume_file_unsupported_format(self):
        """Test parsing an unsupported file format."""
        with tempfile.NamedTemporaryFile(suffix='.txt') as temp_file:
            result = self.parser.parse_resume_file(temp_file.name)
        self.assertIsNone(result)

    def test_parse_resume_file_nonexistent(self):
        """Test parsing a nonexistent file."""
        result = self.parser.parse_resume_file('nonexistent.pdf')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
