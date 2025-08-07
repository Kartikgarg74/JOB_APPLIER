import logging
import re
from typing import List, Dict, Any, Optional

import PyPDF2
import pdfplumber
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ParsedResume(BaseModel):
    contact_info: Dict[str, Optional[str]] = Field(default_factory=dict)
    education: List[Dict[str, Optional[str]]] = Field(default_factory=list)
    experience: List[Dict[str, Optional[str]]] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    raw_text: str

class ResumeParser:
    def __init__(self):
        pass

    def parse_pdf(self, file_path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying PyPDF2: {e}")
            try:
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page_num in range(len(reader.pages)):
                        text += reader.pages[page_num].extract_text() or ""
            except Exception as e:
                logger.error(f"Failed to parse PDF with both pdfplumber and PyPDF2: {e}")
                raise JobApplierException(status_code=500, message="Failed to parse PDF file.")
        return text

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        contact_info = {
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "website": None,
        }

        # Email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match: contact_info["email"] = email_match.group(0)

        # Phone (simple regex, might need refinement)
        phone_match = re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        if phone_match: contact_info["phone"] = phone_match.group(0)

        # LinkedIn
        linkedin_match = re.search(r'(linkedin\.com/in/[A-Za-z0-9_-]+)', text)
        if linkedin_match: contact_info["linkedin"] = "https://" + linkedin_match.group(0)

        # GitHub
        github_match = re.search(r'(github\.com/[A-Za-z0-9_-]+)', text)
        if github_match: contact_info["github"] = "https://" + github_match.group(0)

        # Personal Website
        website_match = re.search(r'(https?:\/\/(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?)', text)
        if website_match: contact_info["website"] = website_match.group(0)

        return contact_info

    def extract_education(self, text: str) -> List[Dict[str, Optional[str]]]:
        education_sections = re.split(r'\n\s*(?:Education|EDUCATIONAL BACKGROUND)\s*\n', text, flags=re.IGNORECASE)
        if len(education_sections) < 2: return []

        education_text = education_sections[1].split('\n\n')[0] # Take the first block after 'Education'
        education_entries = []

        # Simple pattern for university, degree, and year
        # This is a very basic extractor and will need significant NLP for robustness
        matches = re.findall(r'(.+?)\n\s*(.+?)(?:\n|\s*\d{4}\s*[-–]\s*(?:Present|\d{4}))', education_text)
        for match in matches:
            education_entries.append({"degree": match[1].strip(), "university": match[0].strip(), "year": None}) # Year extraction needs improvement

        return education_entries

    def extract_experience(self, text: str) -> List[Dict[str, Optional[str]]]:
        experience_sections = re.split(r'\n\s*(?:Experience|Work Experience|PROFESSIONAL EXPERIENCE)\s*\n', text, flags=re.IGNORECASE)
        if len(experience_sections) < 2: return []

        experience_text = experience_sections[1].split('\n\n')[0] # Take the first block after 'Experience'
        experience_entries = []

        # Simple pattern for job title, company, and dates
        # This is a very basic extractor and will need significant NLP for robustness
        matches = re.findall(r'(.+?)\n\s*(.+?)\n\s*(\w{3} \d{4}\s*[-–]\s*(?:Present|\w{3} \d{4}))', experience_text)
        for match in matches:
            experience_entries.append({"title": match[0].strip(), "company": match[1].strip(), "dates": match[2].strip()})

        return experience_entries

    def infer_skills(self, text: str) -> List[str]:
        # This is a placeholder. A real implementation would use NLP libraries (e.g., spaCy, NLTK)
        # and a pre-defined list of technical skills or a skill extraction model.
        # For demonstration, we'll look for a few hardcoded skills.
        potential_skills = [
            "Python", "Java", "JavaScript", "React", "Angular", "Vue.js",
            "SQL", "NoSQL", "AWS", "Azure", "GCP", "Docker", "Kubernetes",
            "Machine Learning", "Deep Learning", "NLP", "Data Science",
            "FastAPI", "Django", "Flask", "Node.js", "TypeScript",
            "Git", "CI/CD", "Agile", "Scrum", "REST API", "Microservices"
        ]
        found_skills = []
        text_lower = text.lower()

        for skill in potential_skills:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                found_skills.append(skill)
        return found_skills

    def parse_resume(self, file_path: str) -> ParsedResume:
        raw_text = self.parse_pdf(file_path)
        contact_info = self.extract_contact_info(raw_text)
        education = self.extract_education(raw_text)
        experience = self.extract_experience(raw_text)
        skills = self.infer_skills(raw_text)

        return ParsedResume(
            contact_info=contact_info,
            education=education,
            experience=experience,
            skills=skills,
            raw_text=raw_text
        )

# Example Usage (for testing)
if __name__ == "__main__":
    parser = ResumeParser()
    # Create a dummy PDF file for testing
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    c = canvas.Canvas("dummy_resume.pdf", pagesize=letter)
    c.drawString(100, 750, "John Doe")
    c.drawString(100, 730, "john.doe@example.com | 555-123-4567")
    c.drawString(100, 710, "LinkedIn: linkedin.com/in/johndoe")
    c.drawString(100, 690, "GitHub: github.com/johndoe")
    c.drawString(100, 650, "EDUCATION")
    c.drawString(120, 630, "Master of Science in Computer Science")
    c.drawString(120, 610, "University of Example, 2020")
    c.drawString(100, 570, "EXPERIENCE")
    c.drawString(120, 550, "Software Engineer at Tech Corp (Jan 2021 - Present)")
    c.drawString(140, 530, "- Developed and maintained Python applications with FastAPI.")
    c.drawString(140, 510, "- Implemented REST APIs and integrated with SQL databases.")
    c.drawString(100, 470, "SKILLS")
    c.drawString(120, 450, "Python, FastAPI, SQL, Git, AWS, Docker, Machine Learning")
    c.save()

    try:
        parsed_data = parser.parse_resume("dummy_resume.pdf")
        print("Parsed Data:")
        print(parsed_data.model_dump_json(indent=2))
    except JobApplierException as e:
        print(f"Error: {e.message}")

    import os
    os.remove("dummy_resume.pdf")