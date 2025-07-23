from typing import Dict, Any

def construct_cover_letter_prompt(
    resume_data: Dict[str, Any], job_description: str
) -> str:
    """
    [CONTEXT] Constructs the prompt for generating a personalized cover letter.
    [PURPOSE] Formats applicant and job description data into a prompt for the AI model.
    """
    applicant_name = resume_data.get("name", "")
    applicant_email = resume_data.get("email", "")
    applicant_phone = resume_data.get("phone", "")
    applicant_skills = ", ".join(resume_data.get("skills", []))
    applicant_experience = "\n".join(
        [f"- {exp['title']}: {exp['description']}" for exp in resume_data.get("experience", [])]
    )
    applicant_education = "\n".join(
        [f"- {edu['degree']} in {edu['field_of_study']} from {edu['institution']}" for edu in resume_data.get("education", [])]
    )

    prompt = f"""
Generate a personalized cover letter for a job application.

Applicant Information:
Name: {applicant_name}
Email: {applicant_email}
Phone: {applicant_phone}
Skills: {applicant_skills}
Experience:
{applicant_experience}
Education:
{applicant_education}

Job Description:
{job_description}

The cover letter should:
1. Be professional and enthusiastic.
2. Highlight relevant skills and experiences from the applicant's resume that match the job description.
3. Express genuine interest in the company and the specific role.
4. Be concise and to the point.
    """
    return prompt