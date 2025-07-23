import pytest
from packages.agents.resume_enhancer.resume_enhancer_agent import ResumeEnhancerAgent

@pytest.fixture
def resume_enhancer_agent():
    return ResumeEnhancerAgent()

def test_enhance_resume_valid_input(resume_enhancer_agent):
    resume_data = {
        "personal_details": {"name": "Jane Doe"},
        "experience": [
            {"title": "Software Engineer", "description": "Developed software."}
        ],
        "skills": ["Python"]
    }
    job_description = {"description": "Seeking a software engineer with Python skills."}
    enhanced_resume = resume_enhancer_agent.enhance_resume(resume_data, job_description)
    assert isinstance(enhanced_resume, dict)
    assert "personal_details" in enhanced_resume
    assert "experience" in enhanced_resume
    assert "skills" in enhanced_resume
    # Add more specific assertions based on expected enhancements

def test_enhance_resume_empty_resume(resume_enhancer_agent):
    resume_data = {}
    job_description = {"description": "Seeking a software engineer with Python skills."}
    enhanced_resume = resume_enhancer_agent.enhance_resume(resume_data, job_description)
    assert isinstance(enhanced_resume, dict)
    # Expect an empty or minimally enhanced resume

def test_enhance_resume_empty_job_description(resume_enhancer_agent):
    resume_data = {
        "personal_details": {"name": "Jane Doe"},
        "experience": [
            {"title": "Software Engineer", "description": "Developed software."}
        ],
        "skills": ["Python"]
    }
    job_description = {}
    enhanced_resume = resume_enhancer_agent.enhance_resume(resume_data, job_description)
    assert isinstance(enhanced_resume, dict)
    assert "personal_details" in enhanced_resume