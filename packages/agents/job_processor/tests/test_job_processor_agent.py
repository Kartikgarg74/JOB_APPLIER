import pytest
from packages.agents.job_processor.job_processor_agent import JobProcessorAgent

@pytest.fixture
def job_processor_agent():
    return JobProcessorAgent()

def test_process_job_listing_valid_input(job_processor_agent):
    job_listing = {
        "title": "Software Engineer",
        "company": "Example Corp",
        "description": "We are looking for a skilled software engineer...",
        "url": "http://example.com/job/123"
    }
    processed_job = job_processor_agent.process_job_listing(job_listing)
    assert isinstance(processed_job, dict)
    assert "title" in processed_job
    assert "company" in processed_job
    assert "description" in processed_job
    assert "url" in processed_job
    assert "processed_date" in processed_job

def test_process_job_listing_empty_input(job_processor_agent):
    job_listing = {}
    processed_job = job_processor_agent.process_job_listing(job_listing)
    assert isinstance(processed_job, dict)
    assert "processed_date" in processed_job

def test_process_job_listing_missing_fields(job_processor_agent):
    job_listing = {
        "title": "Software Engineer",
        "company": "Example Corp",
    }
    processed_job = job_processor_agent.process_job_listing(job_listing)
    assert isinstance(processed_job, dict)
    assert "title" in processed_job
    assert "company" in processed_job
    assert "processed_date" in processed_job
    assert "description" not in processed_job