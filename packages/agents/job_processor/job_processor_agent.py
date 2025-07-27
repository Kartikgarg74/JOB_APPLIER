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
    # Removed all dummy job listings and test processing
