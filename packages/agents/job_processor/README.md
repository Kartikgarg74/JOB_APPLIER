# Job Processor Agent

## Purpose
This agent is responsible for taking raw job listings, typically obtained from the `JobScraperAgent`, and transforming them into a clean, normalized, and enriched format. This standardization is crucial for subsequent steps in the job application workflow, such as job matching and ATS scoring.

## Dependencies
- `logging`: Standard Python library for logging.
- `typing`: For type hints.

## Key Components
- `job_processor_agent.py`: 
  - Defines the `JobProcessorAgent` class, which contains the `process` method.
  - The `process` method iterates through a list of raw job listing dictionaries and applies two main sub-processes:
    - `_clean_and_normalize`: Handles tasks like stripping whitespace, standardizing location names, and removing HTML tags from descriptions.
    - `_enrich_data`: Adds valuable insights by extracting information such as required skills (using simple keyword matching as a placeholder) and determining experience levels from the job description.
  - The current implementation uses placeholder logic for cleaning, normalization, and enrichment. In a full production system, these methods would leverage more advanced NLP techniques and external data sources.

## Usage Examples
```python
from packages.agents.job_processor.job_processor_agent import JobProcessorAgent
from packages.utilities.logging_utils import setup_logging

# Setup logging for better output
setup_logging()

# Initialize the JobProcessorAgent
processor = JobProcessorAgent()

# Dummy raw job listings for demonstration
raw_job_listings = [
    {
        "title": "  Software Engineer (Python)  ",
        "company": "  Global Tech  ",
        "location": "  New York, NY, USA  ",
        "description": "We are looking for a senior software engineer with strong Python and SQL skills.",
        "url": "http://example.com/job1"
    },
    {
        "title": "Junior Data Scientist",
        "company": "DataCo",
        "location": "San Francisco, CA",
        "description": "Entry-level position for a data scientist. Knowledge of machine learning is a plus.",
        "url": "http://example.com/job2"
    }
]

print("\n--- Processing Raw Job Listings ---")
processed_jobs = processor.process(raw_job_listings)

for job in processed_jobs:
    print(f"\nTitle: {job['title']}")
    print(f"Company: {job['company']}")
    print(f"Location: {job['location']}")
    print(f"Experience Level: {job['experience_level']}")
    print(f"Extracted Skills: {', '.join(job['extracted_skills'])}")
    print(f"URL: {job['url']}")

print("\n--- Processing complete ---")
```

## API Reference

### `JobProcessorAgent` Class
- `__init__(self)`: Initializes the agent and its logger.
- `process(self, job_listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]`:
  - `job_listings`: A list of dictionaries, where each dictionary represents a raw job listing.
  - Returns a list of dictionaries, where each dictionary contains the cleaned, normalized, and enriched job listing data.
- `_clean_and_normalize(self, job: Dict[str, Any]) -> Dict[str, Any]`: (Internal method) Applies cleaning and normalization rules to a single job listing.
- `_enrich_data(self, job: Dict[str, Any]) -> Dict[str, Any]`: (Internal method) Enriches a single job listing with derived information.

## Development Setup
No special setup is required beyond standard Python environment setup. Ensure all dependencies are installed.

## Testing
To test the `JobProcessorAgent`, run `job_processor_agent.py` directly. It contains an `if __name__ == "__main__":` block with example usage.

## Contributing
Follow the general contribution guidelines for the project. When enhancing the cleaning, normalization, or enrichment logic, consider using more sophisticated NLP libraries and techniques. Ensure that any new data points added during enrichment are consistently named and documented.