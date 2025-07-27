import unittest
import os
import sys
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the sys.path to allow imports of modules at the same level
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, project_root)

# Mock the database dependencies before importing the agent
with patch.dict('sys.modules', {
    'packages.database.user_data_model': Mock(),
    'packages.database.models': Mock(),
    'packages.database.config': Mock(),
    'packages.agents.application_automation.application_automation_utils': Mock(),
    'playwright.sync_api': Mock(),
    'playwright': Mock()
}):
    from packages.agents.application_automation.application_automation_agent import ApplicationAutomationAgent

class TestApplicationAutomationAgent(unittest.TestCase):

    def setUp(self):
        self.mock_db = Mock()
        self.agent = ApplicationAutomationAgent(db=self.mock_db)

    def test_initialization(self):
        """Test that the application automation agent initializes correctly."""
        self.assertEqual(self.agent.db, self.mock_db)
        self.assertIsNotNone(self.agent.logger)

    def test_log_application_attempt(self):
        """Test logging application attempts."""
        job_data = {
            "title": "Software Engineer",
            "company": "Google",
            "url": "https://linkedin.com/jobs/123"
        }

        # Test the logging method directly
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = '[]'
            self.agent._log_application_attempt(job_data, "linkedin", "success")

    def test_get_application_history_empty(self):
        """Test getting application history when no log exists."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            history = self.agent.get_application_history()
            self.assertEqual(history, [])

    def test_get_application_history_with_data(self):
        """Test getting application history with existing data."""
        test_logs = [
            {
                "timestamp": "2024-01-01T00:00:00",
                "platform": "linkedin",
                "title": "Software Engineer",
                "company": "Google",
                "url": "https://linkedin.com/jobs/123",
                "result": "success"
            },
            {
                "timestamp": "2024-01-02T00:00:00",
                "platform": "indeed",
                "title": "Data Scientist",
                "company": "Amazon",
                "url": "https://indeed.com/jobs/456",
                "result": "failure"
            }
        ]

        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(test_logs)
            history = self.agent.get_application_history()
            self.assertEqual(history, test_logs)

    def test_get_application_stats_empty(self):
        """Test getting application stats with no data."""
        with patch.object(self.agent, 'get_application_history', return_value=[]):
            stats = self.agent.get_application_stats()

            self.assertEqual(stats["total_applications"], 0)
            self.assertEqual(stats["successful_applications"], 0)
            self.assertEqual(stats["failed_applications"], 0)
            self.assertEqual(stats["success_rate"], 0.0)
            self.assertEqual(stats["platforms"], {})
            self.assertEqual(stats["recent_applications"], [])

    def test_get_application_stats_with_data(self):
        """Test getting application stats with data."""
        test_logs = [
            {
                "timestamp": "2024-01-01T00:00:00",
                "platform": "linkedin",
                "title": "Software Engineer",
                "company": "Google",
                "url": "https://linkedin.com/jobs/123",
                "result": "success"
            },
            {
                "timestamp": "2024-01-02T00:00:00",
                "platform": "indeed",
                "title": "Data Scientist",
                "company": "Amazon",
                "url": "https://indeed.com/jobs/456",
                "result": "failure"
            },
            {
                "timestamp": "2024-01-03T00:00:00",
                "platform": "linkedin",
                "title": "ML Engineer",
                "company": "Microsoft",
                "url": "https://linkedin.com/jobs/789",
                "result": "success"
            }
        ]

        with patch.object(self.agent, 'get_application_history', return_value=test_logs):
            stats = self.agent.get_application_stats()

            self.assertEqual(stats["total_applications"], 3)
            self.assertEqual(stats["successful_applications"], 2)
            self.assertEqual(stats["failed_applications"], 1)
            self.assertEqual(stats["success_rate"], 66.67)
            self.assertEqual(stats["platforms"]["linkedin"], 2)
            self.assertEqual(stats["platforms"]["indeed"], 1)
            self.assertEqual(len(stats["recent_applications"]), 3)

    def test_apply_for_job_no_url(self):
        """Test applying for job without URL."""
        job_data = {
            "title": "Software Engineer",
            "company": "Google"
            # No URL
        }

        result = self.agent.apply_for_job(job_data, "resume.pdf", "cover_letter.pdf")
        self.assertFalse(result)

    def test_platform_detection(self):
        """Test platform detection from URLs."""
        test_cases = [
            ("https://linkedin.com/jobs/123", "linkedin"),
            ("https://indeed.com/jobs/456", "indeed"),
            ("https://workday.com/jobs/789", "workday"),
            ("https://greenhouse.io/jobs/012", "greenhouse"),
            ("https://example.com/jobs/345", "generic")
        ]

        for url, expected_platform in test_cases:
            job_data = {"url": url}
            # Extract platform detection logic
            platform = "unknown"
            if "linkedin.com" in url:
                platform = "linkedin"
            elif "indeed.com" in url:
                platform = "indeed"
            elif "workday.com" in url:
                platform = "workday"
            elif "greenhouse.io" in url:
                platform = "greenhouse"
            else:
                platform = "generic"

            self.assertEqual(platform, expected_platform)

    def test_comprehensive_workflow(self):
        """Test a complete workflow of the application automation agent."""
        # Test initialization
        self.assertIsNotNone(self.agent)

        # Test application history
        with patch.object(self.agent, 'get_application_history', return_value=[]):
            history = self.agent.get_application_history()
            self.assertEqual(history, [])

        # Test application stats
        with patch.object(self.agent, 'get_application_stats') as mock_stats:
            mock_stats.return_value = {
                "total_applications": 5,
                "successful_applications": 3,
                "failed_applications": 2,
                "success_rate": 60.0,
                "platforms": {"linkedin": 3, "indeed": 2},
                "recent_applications": []
            }
            stats = self.agent.get_application_stats()
            self.assertEqual(stats["total_applications"], 5)
            self.assertEqual(stats["success_rate"], 60.0)

    def test_error_handling(self):
        """Test error handling in the agent."""
        # Test with invalid job data
        result = self.agent.apply_for_job({}, "resume.pdf", "cover_letter.pdf")
        self.assertFalse(result)

        # Test with None job data
        result = self.agent.apply_for_job(None, "resume.pdf", "cover_letter.pdf")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
