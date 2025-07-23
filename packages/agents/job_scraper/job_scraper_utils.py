from typing import List, Dict, Any

def filter_dummy_jobs(
    jobs: List[Dict[str, Any]], job_roles: List[str], job_locations: List[str]
) -> List[Dict[str, Any]]:
    """
    [CONTEXT] Helper method to filter dummy jobs based on roles and locations.
    [PURPOSE] Provides basic filtering for the placeholder data.
    """
    filtered_jobs = []
    for job in jobs:
        role_match = not job_roles or any(
            role.lower() in job["title"].lower() for role in job_roles
        )
        location_match = not job_locations or any(
            loc.lower() in job["location"].lower() for loc in job_locations
        )
        if role_match and location_match:
            filtered_jobs.append(job)
    return filtered_jobs