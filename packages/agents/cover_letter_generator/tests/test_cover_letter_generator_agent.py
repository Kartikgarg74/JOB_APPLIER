import pytest
from packages.agents.cover_letter_generator.cover_letter_generator_agent import CoverLetterGeneratorAgent

@pytest.fixture
def cover_letter_agent():
    return CoverLetterGeneratorAgent()

def test_generate_cover_letter_valid_input(cover_letter_agent):
    user_profile = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "123-456-7890",
        "linkedin_profile": "linkedin.com/in/johndoe",
        "github_profile": "github.com/johndoe",
        "experience": [
            {"title": "Software Engineer", "company": "Tech Corp", "years": 5, "description": "Developed and maintained software."}
        ],
        "education": [
            {"degree": "Master's", "field": "Computer Science", "university": "State University", "year": 2018}
        ],
        "skills": ["Python", "Java", "AWS"]
    }
    job_description = {
        "title": "Senior Software Engineer",
        "company": "Innovate Inc.",
        "description": "Seeking a senior software engineer with expertise in Python and cloud technologies."
    }
    cover_letter = cover_letter_agent.generate_cover_letter(user_profile, job_description)
    assert isinstance(cover_letter, str)
    assert len(cover_letter) > 0
    assert "John Doe" in cover_letter
    assert "Innovate Inc." in cover_letter
    assert "Python" in cover_letter

def test_generate_cover_letter_empty_profile(cover_letter_agent):
    user_profile = {}
    job_description = {
        "title": "Senior Software Engineer",
        "company": "Innovate Inc.",
        "description": "Seeking a senior software engineer with expertise in Python and cloud technologies."
    }
    cover_letter = cover_letter_agent.generate_cover_letter(user_profile, job_description)
    assert isinstance(cover_letter, str)
    assert len(cover_letter) > 0 # Should still generate a basic letter

def test_generate_cover_letter_empty_job_description(cover_letter_agent):
    user_profile = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "123-456-7890",
        "linkedin_profile": "linkedin.com/in/johndoe",
        "github_profile": "github.com/johndoe",
        "experience": [
            {"title": "Software Engineer", "company": "Tech Corp", "years": 5, "description": "Developed and maintained software."}
        ],
        "education": [
            {"degree": "Master's", "field": "Computer Science", "university": "State University", "year": 2018}
        ],
        "skills": ["Python", "Java", "AWS"]
    }
    job_description = {}
    cover_letter = cover_letter_agent.generate_cover_letter(user_profile, job_description)
    assert isinstance(cover_letter, str)
    assert len(cover_letter) > 0 # Should still generate a basic letter