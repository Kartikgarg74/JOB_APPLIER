import re
import spacy
from typing import Dict, List, Optional, Any
import logging
from PyPDF2 import PdfReader
from docx import Document
import os
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from dataclasses import dataclass, field

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logging.warning("Downloading spaCy model...")
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    try:
        with open(file_path, 'rb') as file:
            # Create a PDF reader object
            pdf = PdfReader(file)

            # Check if the file is empty
            if len(pdf.pages) == 0:
                logger.warning("PDF file is empty")
                return ""

            # Extract text from all pages
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    try:
        # Create a Document object
        doc = Document(file_path)

        # Extract text from all paragraphs
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        return ""

def extract_certifications(text: str) -> list:
    """Extract certifications from resume text."""
    certs = []
    sections = re.split(r'\n(?=[A-Z][A-Z\s]+:?(?:\n|$))', text)
    for section in sections:
        if re.search(r'CERTIFICATION|CERTIFICATIONS|LICENSE|LICENSES', section.upper()):
            lines = [line.strip() for line in section.split('\n')[1:] if line.strip()]
            for line in lines:
                if not re.match(r'^[A-Z][A-Z\s]+:?$', line):
                    certs.append(line)
    return certs

def extract_awards(text: str) -> list:
    """Extract awards from resume text."""
    awards = []
    sections = re.split(r'\n(?=[A-Z][A-Z\s]+:?(?:\n|$))', text)
    for section in sections:
        if re.search(r'AWARD|HONOR|ACHIEVEMENT', section.upper()):
            lines = [line.strip() for line in section.split('\n')[1:] if line.strip()]
            for line in lines:
                if not re.match(r'^[A-Z][A-Z\s]+:?$', line):
                    awards.append(line)
    return awards

def extract_achievements(text: str) -> list:
    """Extract achievements from resume text."""
    achievements = []
    sections = re.split(r'\n(?=[A-Z][A-Z\s]+:?(?:\n|$))', text)
    for section in sections:
        if re.search(r'ACHIEVEMENT|ACHIEVEMENTS', section.upper()):
            lines = [line.strip() for line in section.split('\n')[1:] if line.strip()]
            for line in lines:
                if not re.match(r'^[A-Z][A-Z\s]+:?$', line):
                    achievements.append(line)
    return achievements

def extract_personal_details(text: str) -> Dict[str, Optional[str]]:
    """
    Extract personal details using NLP and regex patterns.
    """
    # Initialize details
    details = {
        "name": None,
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
        "portfolio": None,
        "location": None
    }

    # Extract email
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    email_match = re.search(email_pattern, text)
    if email_match:
        details["email"] = email_match.group()

    # Extract phone
    phone_patterns = [
        r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",  # (123) 456-7890 or 123-456-7890
        r"\+\d{1,2}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",  # +1 (123) 456-7890
        r"\d{10}"  # 1234567890
    ]

    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            phone = phone_match.group()
            # Normalize phone number format
            digits = re.sub(r'[^\d]', '', phone)  # Extract just the digits
            if len(digits) == 10:
                phone = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) > 10:
                # Format international numbers
                if digits.startswith('1'):
                    phone = f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
                else:
                    phone = f"+{digits[:2]} ({digits[2:5]}) {digits[5:8]}-{digits[8:]}"
            details["phone"] = phone
            break

    # Extract LinkedIn URL
    linkedin_pattern = r"linkedin\.com/in/[\w-]+"
    linkedin_match = re.search(linkedin_pattern, text)
    if linkedin_match:
        details["linkedin"] = "https://www." + linkedin_match.group()

    # Extract GitHub URL
    github_pattern = r"github\.com/[\w-]+"
    github_match = re.search(github_pattern, text)
    if github_match:
        details["github"] = "https://www." + github_match.group()

    # Try spaCy first
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON" and not details["name"]:
            details["name"] = ent.text.strip()
            break
    # Fallback to NLTK if spaCy fails
    if not details["name"]:
        try:
            nltk_results = ne_chunk(pos_tag(word_tokenize(text)))
            for subtree in nltk_results:
                if type(subtree) == Tree and subtree.label() == 'PERSON':
                    name = ' '.join([leaf[0] for leaf in subtree.leaves()])
                    details["name"] = name
                    break
        except Exception:
            pass

    # Extract location (last GPE entity)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            details["location"] = ent.text

    return details

def extract_education(text: str) -> List[Dict[str, str]]:
    """
    Extract education details using NLP and pattern matching.
    """
    education = []

    # Common degree patterns
    degree_patterns = [
        r"(?:Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|B\.?E\.?|M\.?E\.?|B\.?Tech\.?|M\.?Tech\.?)",
        r"(?:Bachelor's|Master's|Doctorate)",
        r"(?:Computer Science|Engineering|Business Administration|Mathematics|Physics)"
    ]

    # Find education section
    sections = re.split(r'\n(?=[A-Z][A-Z\s]+:?(?:\n|$))', text)
    education_section = None
    for section in sections:
        if re.search(r'EDUCATION|ACADEMIC|QUALIFICATION', section.upper()):
            education_section = section
            break

    if not education_section:
        return []

    # Process each line in the education section
    lines = [line.strip() for line in education_section.split('\n') if line.strip()]
    current_degree = None

    # Skip the "EDUCATION" header
    for i, line in enumerate(lines[1:], 1):
        # Look for degree information
        is_degree_line = False
        for pattern in degree_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                is_degree_line = True
                # If we have a current degree and we're seeing a new one, save the current one
                if current_degree:
                    education.append(current_degree)

                # Start a new degree entry
                current_degree = {"degree": line}

                # Extract year if present
                year_match = re.search(r'20\d{2}|19\d{2}', line)
                if year_match:
                    current_degree["year"] = year_match.group()

                # Extract GPA if present
                gpa_match = re.search(r'GPA:?\s*(\d+\.?\d*)', line, re.IGNORECASE)
                if gpa_match:
                    current_degree["gpa"] = gpa_match.group(1)
                break

        # If not a degree line and we have a current degree, it might be additional info
        if not is_degree_line and current_degree:
            # Check if it's a GPA line
            gpa_match = re.search(r'GPA:?\s*(\d+\.?\d*)', line, re.IGNORECASE)
            if gpa_match and "gpa" not in current_degree:
                current_degree["gpa"] = gpa_match.group(1)

            # Check if it's a year range line
            year_range_match = re.search(r'(20\d{2}|19\d{2})\s*(?:-|–|to)\s*(20\d{2}|19\d{2}|Present)', line)
            if year_range_match:
                # Use the end year (or start year if no end year)
                end_year = year_range_match.group(2)
                if end_year == 'Present':
                    current_degree["year"] = year_range_match.group(1)
                else:
                    current_degree["year"] = end_year
            # If no year range but there's a single year
            elif "year" not in current_degree:
                year_match = re.search(r'20\d{2}|19\d{2}', line)
                if year_match:
                    current_degree["year"] = year_match.group()

            # If we see a line that looks like the start of a new section, break
            if i < len(lines) - 1 and re.match(r'^[A-Z][A-Z\s]+:?$', lines[i+1]):
                break

    # Don't forget to add the last degree
    if current_degree:
        education.append(current_degree)

    # Sort education entries by year in reverse order (most recent first)
    education.sort(key=lambda x: x.get("year", "0"), reverse=True)

    return education

def extract_experience(text: str) -> List[Dict[str, str]]:
    """
    Extract work experience details using NLP.
    """
    experience = []

    # Find experience section
    sections = re.split(r'\n(?=[A-Z][A-Z\s]+:?(?:\n|$))', text)
    experience_section = None
    for section in sections:
        if re.search(r'EXPERIENCE|EMPLOYMENT|WORK', section.upper()):
            experience_section = section
            break

    if not experience_section:
        return []

    # Split into entries (each job)
    # First, remove the section header
    experience_lines = experience_section.split('\n', 1)[1] if '\n' in experience_section else ""

    # Split into job entries - each entry starts with a capital letter and contains a pipe
    entries = []
    current_entry = []

    for line in experience_lines.split('\n'):
        line = line.strip()
        if not line:
            continue

        # If line starts with capital letter and contains a pipe, it's a new entry
        if re.match(r'^[A-Z]', line) and '|' in line:
            if current_entry:
                entries.append('\n'.join(current_entry))
            current_entry = [line]
        else:
            current_entry.append(line)

    # Don't forget the last entry
    if current_entry:
        entries.append('\n'.join(current_entry))

    for entry in entries:
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        if not lines:
            continue

        # First line should contain title and company
        if '|' not in lines[0]:
            continue

        job_entry = {
            "title_and_company": lines[0],
            "date_range": "",
            "responsibilities": []
        }

        # Extract date range from the second line
        if len(lines) > 1:
            date_pattern = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*\d{4}\s*(?:-|–|to)\s*(?:Present|Current|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*\d{4})'
            date_match = re.search(date_pattern, lines[1], re.IGNORECASE)
            if date_match:
                job_entry["date_range"] = date_match.group()

                # Extract responsibilities (bullet points) - start from line after date
                job_entry["responsibilities"] = [
                    line.lstrip('•-').strip()
                    for line in lines[2:]
                    if line.startswith(('-', '•')) or line.strip().startswith('-')
                ]

        experience.append(job_entry)

    return experience

def extract_skills(text: str) -> List[str]:
    """
    Extract skills using NLP and custom skill patterns.
    """
    skills = set()

    # Common technical skills patterns
    skill_patterns = [
        r'Python|Java|C\+\+|JavaScript|TypeScript|React|Node\.js|SQL|AWS|Docker|Kubernetes|Git',
        r'Machine Learning|Deep Learning|AI|Artificial Intelligence|Data Science|NLP|Computer Vision',
        r'HTML|CSS|REST|API|MongoDB|PostgreSQL|MySQL|Redis|Linux|Unix|Windows|MacOS',
        r'Agile|Scrum|Project Management|Team Leadership|Problem Solving|Communication',
        r'Django|Flask|Express'  # Additional frameworks
    ]

    # Find skills section
    sections = re.split(r'\n(?=[A-Z][A-Z\s]+:?(?:\n|$))', text)
    skills_section = None
    for section in sections:
        if re.search(r'SKILLS|TECHNOLOGIES|TECHNICAL', section.upper()):
            skills_section = section
            break

    if skills_section:
        # Extract skills using patterns
        for pattern in skill_patterns:
            matches = re.findall(pattern, skills_section, re.IGNORECASE)
            skills.update(matches)

        # Extract additional skills using labels and colons
        label_matches = re.findall(r'(?:Languages|Frameworks|Tools|Technologies):\s*(.*?)(?:\n|$)', skills_section)
        for match in label_matches:
            # Split by commas and clean up
            additional_skills = [s.strip() for s in match.split(',')]
            skills.update(additional_skills)

    # Also look for skills mentioned in experience sections
    for section in sections:
        if re.search(r'EXPERIENCE|EMPLOYMENT|WORK', section.upper()):
            for pattern in skill_patterns:
                matches = re.findall(pattern, section, re.IGNORECASE)
                skills.update(matches)

    # Clean up skills
    cleaned_skills = set()
    for skill in skills:
        # Remove any empty strings or whitespace-only strings
        if not skill or skill.isspace():
            continue
        # Remove any leading/trailing whitespace and punctuation
        skill = skill.strip(' .,;:')
        # Skip if the skill is too short (likely noise)
        if len(skill) < 2:
            continue
        cleaned_skills.add(skill)

    return sorted(list(cleaned_skills))

def extract_projects(text: str) -> List[Dict[str, Any]]:
    """
    Extract project details using NLP.
    """
    projects = []

    # Find projects section
    sections = re.split(r'\n(?=[A-Z][A-Z\s]+:?(?:\n|$))', text)
    projects_section = None
    for section in sections:
        if re.search(r'PROJECT|PORTFOLIO', section.upper()):
            projects_section = section
            break

    if not projects_section:
        return []

    # Split into individual projects
    # First, remove the section header
    project_lines = projects_section.split('\n', 1)[1] if '\n' in projects_section else ""

    # Split into project entries - each entry starts with a non-bullet point line

    # Split into entries by blank lines
    entries = re.split(r'\n\s*\n', project_lines)

    for entry in entries:
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        if not lines:
            continue

        # First line should be the project name
        if not lines[0].startswith(('-', '•')) and not lines[0].strip().startswith('-'):
            # Skip section headers and special lines
            if (re.match(r'^[A-Z][A-Z\s]+:?$', lines[0]) or
                re.match(r'^(?:Languages|Frameworks|Tools|Technologies):', lines[0]) or
                re.match(r'^(?:using|with|in)\s+', lines[0], re.IGNORECASE) or
                re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s*\|', lines[0]) or
                re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+', lines[0])):  # Skip job titles
                continue

            project = {
                "name": lines[0],
                "technologies": [],
                "description": []
            }

            # Extract description and technologies
            for line in lines[1:]:
                if line.startswith(('-', '•')) or line.strip().startswith('-'):
                    desc_line = line.lstrip('•-').strip()
                    project["description"].append(desc_line)

                    # Extract technologies if mentioned
                    tech_pattern = r'(?:using|with|in)\s+([\w\s,\.+]+)'
                    tech_match = re.search(tech_pattern, desc_line, re.IGNORECASE)
                    if tech_match:
                        techs = [t.strip() for t in tech_match.group(1).split(',')]
                        project["technologies"].extend(techs)

            # Only add projects that have both a name and description
            if project["name"] and project["description"]:
                projects.append(project)

    return projects

def validate_extracted_data(data: Dict[str, Any]) -> bool:
    """
    Validate the extracted resume data.
    """
    # Check for required personal details
    if not data.get("personal_details", {}).get("name"):
        logger.warning("Missing required field: name")
        return False

    # Validate email format if present
    email = data.get("personal_details", {}).get("email")
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        logger.warning("Invalid email format")
        return False

    # Validate phone format if present
    phone = data.get("personal_details", {}).get("phone")
    if phone and not re.match(r"\+?\d{1,2}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\(\d{3}\)\s*\d{3}[-.]?\d{4}", phone):
        logger.warning("Invalid phone format")
        return False

    # For minimal resumes, we only require name and either email or phone
    has_contact = bool(email or phone)
    if has_contact and data.get("personal_details", {}).get("name"):
        return True

    # For complete resumes, we require at least one content section
    has_content = any([
        data.get("education"),
        data.get("experience"),
        data.get("skills"),
        data.get("projects")
    ])

    if not has_content:
        logger.warning("No content sections found")
        return False

    return True

@dataclass
class ResumeData:
    raw_text: str
    personal_details: Dict[str, Optional[str]]
    education: List[Dict[str, str]]
    experience: List[Dict[str, str]]
    skills: List[str]
    projects: List[Dict[str, Any]]
    certifications: List[str]
    awards: List[str]
    achievements: List[str]
    summary: str = ""
    keywords: List[str] = field(default_factory=list)
    location: str = ""
