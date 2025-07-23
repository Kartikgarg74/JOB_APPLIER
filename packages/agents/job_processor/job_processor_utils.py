from typing import Dict, Any, List

def clean_and_normalize_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    [CONTEXT] Cleans and normalizes individual job listing data.
    [PURPOSE] Ensures consistency in data formats (e.g., location, title).
    """
    cleaned_job = job.copy()
    cleaned_job["title"] = cleaned_job.get("title", "").strip()
    cleaned_job["company"] = cleaned_job.get("company", "").strip()
    cleaned_job["location"] = (
        cleaned_job.get("location", "").replace("USA", "").strip()
    )  # Example normalization
    cleaned_job["description"] = cleaned_job.get("description", "").strip()
    return cleaned_job

def enrich_job_data(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    [CONTEXT] Enriches job listing data with additional derived information.
    [PURPOSE] Adds valuable insights like required skills, experience level, or industry.
    """
    enriched_job = job.copy()
    # Dummy enrichment: add a 'skills' field
    description = enriched_job.get("description", "").lower()
    skills = []
    if "python" in description:
        skills.append("Python")
    if "java" in description:
        skills.append("Java")
    if "sql" in description:
        skills.append("SQL")
    if "machine learning" in description:
        skills.append("Machine Learning")
    enriched_job["extracted_skills"] = skills

    # Dummy enrichment: add an 'experience_level' field
    if any(keyword in description for keyword in ["senior", "lead", "architect"]):
        enriched_job["experience_level"] = "Senior"
    elif any(keyword in description for keyword in ["junior", "entry-level"]):
        enriched_job["experience_level"] = "Junior"
    else:
        enriched_job["experience_level"] = "Mid-level"
    return enriched_job