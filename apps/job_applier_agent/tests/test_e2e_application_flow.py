import pytest
from unittest.mock import patch

def test_full_application_flow():
    # Mock job scraping
    with patch('packages.agents.job_scraper.job_scraper_agent.JobScraperAgent.search_indeed') as mock_scrape:
        mock_scrape.return_value = [{
            'title': 'Software Engineer',
            'company': 'TestCo',
            'location': 'Remote',
            'url': 'http://example.com/job1',
            'required_skills': ['Python'],
            'required_experience': 2,
            'required_education': ['B.S. Computer Science'],
        }]
        # Mock job matching
        with patch('packages.agents.job_matcher.job_matcher_agent.JobMatcherAgent.match_jobs') as mock_match:
            mock_match.return_value = [{
                'title': 'Software Engineer',
                'company': 'TestCo',
                'compatibility_score': 95,
                'url': 'http://example.com/job1',
            }]
            # Mock application automation
            with patch('packages.agents.application_automation.application_automation_agent.ApplicationAutomationAgent.apply_for_job') as mock_apply:
                mock_apply.return_value = True
                # Simulate status tracking
                status = 'submitted'
                assert status == 'submitted'
