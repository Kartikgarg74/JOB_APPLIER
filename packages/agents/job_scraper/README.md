# Job Scraper Agent

## Purpose
This agent is responsible for scraping job listings from various online sources based on user-defined criteria such as job roles and locations. It acts as the data collection component for the job application workflow, providing raw job data for further processing.

## Dependencies
- `logging`: Standard Python library for logging.
- `typing`: For type hints.

## Key Components
- `job_scraper_agent.py`: 
  - Defines the `JobScraperAgent` class, which contains the `scrape` method.
  - The `scrape` method takes a list of job roles and locations as input and returns a list of dictionaries, each representing a job listing with details like title, company, location, description, and URL.
  - Currently, the `scrape` method contains placeholder logic and returns dummy data. In a full implementation, this would integrate with web scraping libraries or job board APIs.

## Usage Examples
```python
from packages.agents.job_scraper.job_scraper_agent import JobScraperAgent
from packages.utilities.logging_utils import setup_logging

# Setup logging for better output
setup_logging()

# Initialize the JobScraperAgent
scraper = JobScraperAgent()

# Example 1: Scrape for 'Software Engineer' in 'San Francisco'
job_roles = ["Software Engineer"]
job_locations = ["San Francisco"]
job_listings = scraper.scrape(job_roles, job_locations)

print(f"Found {len(job_listings)} job listings for {job_roles} in {job_locations}:")
for job in job_listings:
    print(f"- {job['title']} at {job['company']} ({job['location']})")

# Example 2: Scrape for 'Data Scientist' in 'New York'
job_roles_2 = ["Data Scientist"]
job_locations_2 = ["New York"]
job_listings_2 = scraper.scrape(job_roles_2, job_locations_2)

print(f"\nFound {len(job_listings_2)} job listings for {job_roles_2} in {job_locations_2}:")
for job in job_listings_2:
    print(f"- {job['title']} at {job['company']} ({job['location']})")

# Example 3: Scrape without specific roles/locations (returns all dummy data)
all_jobs = scraper.scrape([], [])
print(f"\nFound {len(all_jobs)} total dummy job listings:")
```

## API Reference

### `JobScraperAgent` Class
- `__init__(self)`: Initializes the agent and its logger.
- `scrape(self, job_roles: List[str], job_locations: List[str]) -> List[Dict[str, Any]]`:
  - `job_roles`: A list of strings representing desired job titles or roles.
  - `job_locations`: A list of strings representing desired job locations.
  - Returns a list of dictionaries, where each dictionary contains details of a scraped job listing.

## Development Setup
No special setup is required beyond standard Python environment setup. Ensure all dependencies are installed.

## Testing
To test the `JobScraperAgent`, run `job_scraper_agent.py` directly. It contains an `if __name__ == "__main__":` block with example usage.

## Contributing
Follow the general contribution guidelines for the project. When implementing actual scraping logic, consider modularity for different job sources and robust error handling for network issues, CAPTCHAs, and website structure changes.