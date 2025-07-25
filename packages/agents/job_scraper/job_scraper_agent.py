import logging

from packages.agents.job_scraper.job_scraper_utils import IndeedScraper, LinkedInScraper, GoogleJobsScraper

logger = logging.getLogger(__name__)


class JobScraperAgent:
    """
    [CONTEXT] Orchestrates the scraping of job listings from various online sources.
    [PURPOSE] Gathers relevant job opportunities based on specified criteria (job roles, locations).
    """

    def __init__(self):
        self.indeed = IndeedScraper()
        self.linkedin = LinkedInScraper()
        self.google = GoogleJobsScraper()

    def search_indeed(self, query, location="", num_results=10):
        return self.indeed.search_jobs(query, location, num_results)

    def search_linkedin(self, query, location="", num_results=10):
        return self.linkedin.search_jobs(query, location, num_results)

    def search_google_jobs(self, query, location="", num_results=10):
        return self.google.search_jobs(query, location, num_results)


if __name__ == "__main__":
    from packages.utilities.logging_utils import setup_logging

    setup_logging()

    scraper = JobScraperAgent()

    # Example 1: Scrape without specific roles/locations (should return all dummy jobs)
    print("\n--- Scraping all dummy jobs ---")
    all_jobs = scraper.scrape([], [])
    for job in all_jobs:
        print(f"  - {job['title']} at {job['company']} ({job['location']})")

    # Example 2: Scrape for 'Software Engineer' in 'San Francisco'
    print("\n--- Scraping for Software Engineer in San Francisco ---")
    se_sf_jobs = scraper.scrape(["Software Engineer"], ["San Francisco"])
    for job in se_sf_jobs:
        print(f"  - {job['title']} at {job['company']} ({job['location']})")

    # Example 3: Scrape for 'Data Scientist' in 'New York'
    print("\n--- Scraping for Data Scientist in New York ---")
    ds_ny_jobs = scraper.scrape(["Data Scientist"], ["New York"])
    for job in ds_ny_jobs:
        print(f"  - {job['title']} at {job['company']} ({job['location']})")

    # Example 4: Scrape for a role that doesn't exist in dummy data
    print("\n--- Scraping for Non-Existent Role ---")
    non_existent_jobs = scraper.scrape(["DevOps Engineer"], [])
    if not non_existent_jobs:
        print("  No jobs found for 'DevOps Engineer'.")

    # Example 5: Scrape for a location that doesn't exist in dummy data
    print("\n--- Scraping for Non-Existent Location ---")
    non_existent_location_jobs = scraper.scrape([], ["London"])
    if not non_existent_location_jobs:
        print("  No jobs found for 'London'.")
