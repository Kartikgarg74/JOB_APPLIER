import logging
import logging
from typing import List, Dict, Any
from packages.agents.job_processor.job_processor_utils import clean_and_normalize_job, enrich_job_data

logger = logging.getLogger(__name__)


class JobProcessorAgent:
    """
    [CONTEXT] Processes raw job listings to clean, normalize, and enrich the data.
    [PURPOSE] Transforms raw job data into a standardized format suitable for matching and analysis.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("JobProcessorAgent initialized.")

    def process(self, job_listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        [CONTEXT] Cleans, normalizes, and enriches a list of raw job listings.
        [PURPOSE] Prepares job data for subsequent steps in the application workflow.
        """
        self.logger.info(f"Starting job processing for {len(job_listings)} listings.")
        processed_listings = []

        for job in job_listings:
            processed_job = clean_and_normalize_job(job)
            processed_job = enrich_job_data(processed_job)
            processed_listings.append(processed_job)

        self.logger.info(
            f"Finished processing. Processed {len(processed_listings)} listings."
        )
        return processed_listings





if __name__ == "__main__":
    from packages.utilities.logging_utils import setup_logging

    setup_logging()

    processor = JobProcessorAgent()

    # Dummy job listings for testing
    dummy_job_listings = [
        {
            "title": "  Software Engineer (Python)  ",
            "company": "  Global Tech  ",
            "location": "  New York, NY, USA  ",
            "description": "We are looking for a senior software engineer with strong Python and SQL skills.",
            "url": "http://example.com/job1",
        },
        {
            "title": "Junior Data Scientist",
            "company": "DataCo",
            "location": "San Francisco, CA",
            "description": "Entry-level position for a data scientist. Knowledge of machine learning is a plus.",
            "url": "http://example.com/job2",
        },
        {
            "title": "Product Manager",
            "company": "Innovate Corp.",
            "location": "Remote",
            "description": "Define product vision and roadmap. No specific tech skills mentioned.",
            "url": "http://example.com/job3",
        },
    ]

    print("\n--- Processing Dummy Job Listings ---")
    processed_jobs = processor.process(dummy_job_listings)

    for job in processed_jobs:
        print(f"\nTitle: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        print(f"Experience Level: {job['experience_level']}")
        print(f"Extracted Skills: {', '.join(job['extracted_skills'])}")
        print(f"URL: {job['url']}")

    print("\n--- Processing complete ---")
