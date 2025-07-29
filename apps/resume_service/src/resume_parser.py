import spacy
import re
from typing import List, Dict, Any

nlp = spacy.load("en_core_web_sm")

def extract_contact_info(text: str) -> Dict[str, str]:
    email = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
    phone = re.findall(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", text)
    return {"email": email[0] if email else None, "phone": phone[0] if phone else None}

def extract_education(text: str) -> List[Dict[str, str]]:
    education = []
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "ORG" or ent.label_ == "GPE": # Simple heuristic for universities/locations
            # This is a very basic placeholder. More sophisticated NLP/regex needed for robust extraction.
            pass
    return education

def extract_skills(text: str) -> List[str]:
    # This is a placeholder. A more comprehensive skill extraction would involve a predefined list
    # or more advanced NLP techniques.
    skills = []
    keywords = ["Python", "Java", "SQL", "AWS", "Azure", "GCP", "Docker", "Kubernetes", "React", "Angular", "Vue", "JavaScript", "TypeScript", "HTML", "CSS", "Machine Learning", "Deep Learning", "NLP", "Data Science", "Big Data", "Spark", "Hadoop", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Git", "Agile", "Scrum", "REST API", "Microservices", "CI/CD", "DevOps"]
    for keyword in keywords:
        if re.search(r"\b" + re.escape(keyword) + r"\b", text, re.IGNORECASE):
            skills.append(keyword)
    return skills

def extract_experience(text: str) -> List[Dict[str, Any]]:
    # This is a highly simplified placeholder. Real experience extraction is complex.
    experience = []
    # Look for patterns like "Company Name - Job Title (Start Date - End Date)"
    # This needs significant improvement.
    return experience

def extract_certifications(text: str) -> List[str]:
    # Placeholder for certifications. Needs specific patterns or a database of certifications.
    certifications = []
    return certifications

def parse_resume(text: str) -> Dict[str, Any]:
    contact_info = extract_contact_info(text)
    education = extract_education(text)
    skills = extract_skills(text)
    experience = extract_experience(text)
    certifications = extract_certifications(text)

    # Name extraction is tricky without a pre-trained model or strong heuristics.
    # For now, we'll leave it as None or try a very basic heuristic.
    name = None
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break

    return {
        "name": name,
        "email": contact_info["email"],
        "phone": contact_info["phone"],
        "education": education,
        "skills": skills,
        "experience": experience,
        "certifications": certifications
    }

if __name__ == "__main__":
    sample_resume_text = """
    John Doe
    john.doe@example.com
    (123) 456-7890

    Education:
    Master of Science in Computer Science, University of Example, 2020
    Bachelor of Engineering in Software, Another University, 2018

    Skills:
    Python, Java, SQL, AWS, Docker, Machine Learning, NLP, Git, Agile

    Experience:
    Software Engineer, Tech Solutions Inc., 2020-Present
    Developed scalable backend services using Python and FastAPI.
    Implemented machine learning models for data analysis.

    Intern, Innovate Corp., 2019
    Assisted in developing web applications with React and JavaScript.

    Certifications:
    AWS Certified Developer
    """

    parsed_data = parse_resume(sample_resume_text)
    import json
    print(json.dumps(parsed_data, indent=2))