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


if __name__ == "__main__":
    from packages.utilities.logging_utils import setup_logging
    setup_logging()
    scraper = JobScraperAgent()
    # Example usage: see previous main block for details
