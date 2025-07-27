import logging
from typing import List, Dict, Optional
from packages.agents.job_scraper.job_scraper_utils import IndeedScraper, LinkedInScraper, GoogleJobsScraper, RateLimiter, ProxyRotator

class JobScraperAgent:
    """
    Orchestrates the scraping of job listings from various online sources.

    Args:
        rate_limiter: Optional RateLimiter instance for controlling request rate.
        proxies: Optional list of proxy URLs for rotation.
        logger: Optional logger for dependency injection and testability.
    """
    def __init__(self, rate_limiter: Optional[RateLimiter] = None, proxies: Optional[List[str]] = None, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or logging.getLogger(__name__)
        rate_limiter = rate_limiter or RateLimiter()
        proxy_rotator = ProxyRotator(proxies)
        self.indeed = IndeedScraper(rate_limiter=rate_limiter, proxy_rotator=proxy_rotator)
        self.linkedin = LinkedInScraper(rate_limiter=rate_limiter, proxy_rotator=proxy_rotator)
        self.google = GoogleJobsScraper(rate_limiter=rate_limiter, proxy_rotator=proxy_rotator)

    def search_all_platforms(self, query: str, location: str = "", num_results: int = 10) -> Dict[str, List[Dict]]:
        """
        Search all available platforms for job listings.

        Args:
            query: Job title or keywords.
            location: Job location.
            num_results: Maximum number of results per platform.

        Returns:
            Dictionary with platform names as keys and job listings as values.
        """
        self.logger.info(f"Searching all platforms for '{query}' in '{location}' (max {num_results} per platform)")

        results = {
            'indeed': [],
            'linkedin': [],
            'google_jobs': []
        }

        # Search Indeed
        try:
            results['indeed'] = self.search_indeed(query, location, num_results)
            self.logger.info(f"Found {len(results['indeed'])} jobs on Indeed")
        except Exception as e:
            self.logger.error(f"Error searching Indeed: {e}")

        # Search LinkedIn
        try:
            results['linkedin'] = self.search_linkedin(query, location, num_results)
            self.logger.info(f"Found {len(results['linkedin'])} jobs on LinkedIn")
        except Exception as e:
            self.logger.error(f"Error searching LinkedIn: {e}")

        # Search Google Jobs
        try:
            results['google_jobs'] = self.search_google_jobs(query, location, num_results)
            self.logger.info(f"Found {len(results['google_jobs'])} jobs on Google Jobs")
        except Exception as e:
            self.logger.error(f"Error searching Google Jobs: {e}")

        total_jobs = sum(len(jobs) for jobs in results.values())
        self.logger.info(f"Total jobs found across all platforms: {total_jobs}")

        return results

    def search_indeed(self, query: str, location: str = "", num_results: int = 10) -> List[Dict]:
        """
        Search Indeed for job listings.

        Args:
            query: Job title or keywords.
            location: Job location.
            num_results: Maximum number of results to return.

        Returns:
            List of job listings as dictionaries.
        """
        self.logger.info(f"Searching Indeed for '{query}' in '{location}' (max {num_results})")
        try:
            return self.indeed.search_jobs(query, location, num_results)
        except Exception as e:
            self.logger.exception(f"Error searching Indeed: {e}")
            return []

    def search_linkedin(self, query: str, location: str = "", num_results: int = 10) -> List[Dict]:
        """
        Search LinkedIn for job listings.

        Args:
            query: Job title or keywords.
            location: Job location.
            num_results: Maximum number of results to return.

        Returns:
            List of job listings as dictionaries.
        """
        self.logger.info(f"Searching LinkedIn for '{query}' in '{location}' (max {num_results})")
        try:
            return self.linkedin.search_jobs(query, location, num_results)
        except Exception as e:
            self.logger.exception(f"Error searching LinkedIn: {e}")
            return []

    def search_google_jobs(self, query: str, location: str = "", num_results: int = 10) -> List[Dict]:
        """
        Search Google Jobs for job listings.

        Args:
            query: Job title or keywords.
            location: Job location.
            num_results: Maximum number of results to return.

        Returns:
            List of job listings as dictionaries.
        """
        self.logger.info(f"Searching Google Jobs for '{query}' in '{location}' (max {num_results})")
        try:
            return self.google.search_jobs(query, location, num_results)
        except Exception as e:
            self.logger.exception(f"Error searching Google Jobs: {e}")
            return []

    def get_job_details(self, job_url: str, platform: str) -> Dict:
        """
        Get detailed information about a specific job posting.

        Args:
            job_url: URL of the job posting.
            platform: Platform name (indeed, linkedin, google_jobs).

        Returns:
            Dictionary with detailed job information.
        """
        self.logger.info(f"Getting job details for {platform}: {job_url}")

        try:
            if platform == 'indeed':
                return self.indeed.get_job_details(job_url)
            elif platform == 'linkedin':
                return self.linkedin.get_job_details(job_url)
            elif platform == 'google_jobs':
                return self.google.get_job_details(job_url)
            else:
                self.logger.error(f"Unsupported platform: {platform}")
                return {}
        except Exception as e:
            self.logger.exception(f"Error getting job details for {platform}: {e}")
            return {}


if __name__ == "__main__":
    from packages.utilities.logging_utils import setup_logging
    setup_logging()
    scraper = JobScraperAgent()

    # Example usage
    results = scraper.search_all_platforms("Python Developer", "San Francisco", 5)
    print(f"Found jobs: {results}")
