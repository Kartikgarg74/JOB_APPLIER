import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional, Any
import urllib.robotparser
import logging

class RateLimiter:
    """
    Simple rate limiter for web scraping.

    Args:
        min_delay: Minimum delay between requests (seconds).
        max_delay: Maximum delay between requests (seconds).
    """
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0) -> None:
        self.min_delay = min_delay
        self.max_delay = max_delay

    def wait(self) -> None:
        """Wait for a random delay between min_delay and max_delay."""
        time.sleep(random.uniform(self.min_delay, self.max_delay))

class ProxyRotator:
    """
    Rotates through a list of proxies for web requests.

    Args:
        proxies: List of proxy URLs.
    """
    def __init__(self, proxies: Optional[List[str]] = None) -> None:
        self.proxies = proxies or []
        self.index = 0

    def get_proxy(self) -> Optional[str]:
        """Get the next proxy in the rotation."""
        if not self.proxies:
            return None
        proxy = self.proxies[self.index % len(self.proxies)]
        self.index += 1
        return proxy

class RobotsTxtChecker:
    """
    Checks robots.txt for scraping permissions.

    Args:
        user_agent: User agent string to use for robots.txt checks.
    """
    def __init__(self, user_agent: str = "*") -> None:
        self.user_agent = user_agent
        self.parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}

    def can_fetch(self, url: str) -> bool:
        """
        Check if the given URL can be fetched according to robots.txt.

        Args:
            url: The URL to check.
        Returns:
            True if allowed, False otherwise.
        """
        from urllib.parse import urlparse
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        if base_url not in self.parsers:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{base_url}/robots.txt")
            try:
                rp.read()
            except Exception:
                return True  # If robots.txt can't be read, default to allow
            self.parsers[base_url] = rp
        return self.parsers[base_url].can_fetch(self.user_agent, url)

class JobScraperBase:
    """
    Base class for job scrapers with rate limiting, proxy rotation, and robots.txt checking.

    Args:
        rate_limiter: Optional RateLimiter instance.
        proxy_rotator: Optional ProxyRotator instance.
        max_retries: Maximum number of request retries.
        logger: Optional logger for dependency injection.
    """
    def __init__(self, rate_limiter: Optional[RateLimiter] = None, proxy_rotator: Optional[ProxyRotator] = None, max_retries: int = 3, logger: Optional[logging.Logger] = None) -> None:
        self.rate_limiter = rate_limiter or RateLimiter()
        self.proxy_rotator = proxy_rotator or ProxyRotator()
        self.max_retries = max_retries
        self.robots_checker = RobotsTxtChecker()
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def safe_request(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Optional[requests.Response]:
        """
        Make a request with retries, proxy rotation, and robots.txt check.

        Args:
            url: The URL to request.
            params: Query parameters.
            headers: Request headers.
            timeout: Request timeout in seconds.
        Returns:
            Response object if successful, None otherwise.
        """
        if not self.robots_checker.can_fetch(url):
            self.logger.warning(f"Blocked by robots.txt: {url}")
            return None
        attempt = 0
        while attempt < self.max_retries:
            proxy = self.proxy_rotator.get_proxy()
            proxies = {"http": proxy, "https": proxy} if proxy else None
            try:
                resp = requests.get(url, params=params, proxies=proxies, headers=headers, timeout=timeout)
                resp.raise_for_status()
                return resp
            except Exception as e:
                self.logger.warning(f"Request failed (attempt {attempt+1}): {e}")
                self.rate_limiter.wait()
                attempt += 1
                time.sleep(2 ** attempt)  # Exponential backoff
        self.logger.error(f"All retries failed for {url}")
        return None

def is_captcha_page(html: str) -> bool:
    """Detect if the HTML page is a CAPTCHA page."""
    captcha_keywords = [
        'captcha', 'recaptcha', 'g-recaptcha', 'hcaptcha',
        'please verify you are a human', 'are you a robot',
        'security check', 'unusual traffic', 'verify you are not a robot'
    ]
    html_lower = html.lower()
    return any(keyword in html_lower for keyword in captcha_keywords)

class IndeedScraper(JobScraperBase):
    BASE_URL = "https://www.indeed.com/jobs"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    def search_jobs(self, query: str, location: str = "", num_results: int = 10) -> List[Dict]:
        """
        Search Indeed for job listings.

        Args:
            query: Job title or keywords.
            location: Job location.
            num_results: Maximum number of results to return.
        Returns:
            List of job listings as dictionaries.
        """
        jobs: List[Dict] = []
        params = {"q": query, "l": location}
        start = 0
        while len(jobs) < num_results:
            params["start"] = start
            resp = self.safe_request(self.BASE_URL, params=params, headers=self.HEADERS)
            if resp is None:
                break
            if is_captcha_page(resp.text):
                self.logger.warning("[IndeedScraper] CAPTCHA detected. Skipping page.")
                break
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select(".jobsearch-SerpJobCard, .result")
            if not cards:
                self.logger.warning("[IndeedScraper] No job cards found. HTML may have changed or bot blocked.")
                break
            for card in cards:
                title = card.select_one(".title a")
                company = card.select_one(".company")
                location = card.select_one(".location")
                summary = card.select_one(".summary")
                job = {
                    "title": title.text.strip() if title else None,
                    "company": company.text.strip() if company else None,
                    "location": location.text.strip() if location else None,
                    "summary": summary.text.strip() if summary else None,
                    "url": f"https://www.indeed.com{title['href']}" if title and title.has_attr('href') else None,
                }
                jobs.append(job)
                if len(jobs) >= num_results:
                    break
            self.rate_limiter.wait()
            start += 10
        return jobs[:num_results]

class LinkedInScraper(JobScraperBase):
    BASE_URL = "https://www.linkedin.com/jobs/search/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    def search_jobs(self, query: str, location: str = "", num_results: int = 10) -> List[Dict]:
        """
        Search LinkedIn for job listings.

        Args:
            query: Job title or keywords.
            location: Job location.
            num_results: Maximum number of results to return.
        Returns:
            List of job listings as dictionaries.
        """
        jobs: List[Dict] = []
        params = {"keywords": query, "location": location}
        start = 0
        while len(jobs) < num_results:
            params["start"] = start
            resp = self.safe_request(self.BASE_URL, params=params, headers=self.HEADERS)
            if resp is None:
                break
            if is_captcha_page(resp.text):
                self.logger.warning("[LinkedInScraper] CAPTCHA detected. Skipping page.")
                break
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select(".result-card.job-result-card, .base-card")
            if not cards:
                self.logger.warning("[LinkedInScraper] No job cards found. HTML may have changed or bot blocked.")
                break
            for card in cards:
                title = card.select_one(".base-search-card__title, .result-card__title")
                company = card.select_one(".base-search-card__subtitle, .result-card__subtitle")
                location = card.select_one(".job-search-card__location, .job-result-card__location")
                url = card.select_one("a.base-card__full-link, a.result-card__full-card-link")
                job = {
                    "title": title.text.strip() if title else None,
                    "company": company.text.strip() if company else None,
                    "location": location.text.strip() if location else None,
                    "summary": None,
                    "url": url["href"] if url and url.has_attr("href") else None,
                }
                jobs.append(job)
                if len(jobs) >= num_results:
                    break
            self.rate_limiter.wait()
            start += 25
        return jobs[:num_results]

class GlassdoorScraper(JobScraperBase):
    BASE_URL = "https://www.glassdoor.com/Job/jobs.htm"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    def search_jobs(self, query: str, location: str = "", num_results: int = 10) -> List[Dict]:
        """
        Search Glassdoor for job listings.

        Args:
            query: Job title or keywords.
            location: Job location.
            num_results: Maximum number of results to return.
        Returns:
            List of job listings as dictionaries.
        """
        jobs: List[Dict] = []
        params = {"sc.keyword": query, "locT": "C", "locId": "", "locKeyword": location}
        start = 0
        while len(jobs) < num_results:
            params["s"] = start
            proxy = self.proxy_rotator.get_proxy()
            proxies = {"http": proxy, "https": proxy} if proxy else None
            try:
                resp = requests.get(self.BASE_URL, params=params, proxies=proxies, headers=self.HEADERS, timeout=10)
                resp.raise_for_status()
            except Exception as e:
                self.logger.warning(f"[GlassdoorScraper] Request failed: {e}")
                break
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select(".react-job-listing, .jl")
            if not cards:
                self.logger.warning("[GlassdoorScraper] No job cards found. HTML may have changed or bot blocked.")
                break
            for card in cards:
                title = card.select_one(".jobLink, .jobTitle")
                company = card.select_one(".jobEmpolyerName, .jobInfoItem.jobEmpolyerName")
                location = card.select_one(".jobLocation, .subtle.loc")
                summary = card.select_one(".jobDescriptionContent, .job-snippet")
                url = card.select_one("a.jobLink, a.jobTitle")
                job = {
                    "title": title.text.strip() if title else None,
                    "company": company.text.strip() if company else None,
                    "location": location.text.strip() if location else None,
                    "summary": summary.text.strip() if summary else None,
                    "url": f"https://www.glassdoor.com{url['href']}" if url and url.has_attr('href') else None,
                }
                jobs.append(job)
                if len(jobs) >= num_results:
                    break
            self.rate_limiter.wait()
            start += 10
        return jobs[:num_results]

class CompanyScraper(JobScraperBase):
    def search_jobs(self, query: str, location: str = "", num_results: int = 10) -> List[Dict]:
        # TODO: Implement scraping for specific company career pages (configurable)
        return []

class GoogleJobsScraper(JobScraperBase):
    BASE_URL = "https://www.google.com/search"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    def search_jobs(self, query: str, location: str = "", num_results: int = 10) -> List[Dict]:
        """
        Search Google Jobs for job listings.

        Args:
            query: Job title or keywords.
            location: Job location.
            num_results: Maximum number of results to return.
        Returns:
            List of job listings as dictionaries.
        """
        jobs: List[Dict] = []
        params = {"q": f"{query} jobs near {location}" if location else f"{query} jobs"}
        resp = self.safe_request(self.BASE_URL, params=params, headers=self.HEADERS)
        if resp is None:
            return []
        if is_captcha_page(resp.text):
            self.logger.warning("[GoogleJobsScraper] CAPTCHA detected. Skipping page.")
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        # Google Jobs cards are not standard HTML and may not be present; this is a best-effort demo
        cards = soup.select(".BjJfJf.PUpOsf")  # This selector may change
        if not cards:
            self.logger.warning("[GoogleJobsScraper] No job cards found. Google may have blocked scraping or changed HTML.")
            return []
        for card in cards:
            title = card.select_one(".BjJfJf.PUpOsf span")
            company = card.select_one(".vNEEBe")
            location = card.select_one(".Qk80Jf")
            url = card.select_one("a")
            job = {
                "title": title.text.strip() if title else None,
                "company": company.text.strip() if company else None,
                "location": location.text.strip() if location else None,
                "summary": None,
                "url": url["href"] if url and url.has_attr("href") else None,
            }
            jobs.append(job)
            if len(jobs) >= num_results:
                break
        return jobs[:num_results]
