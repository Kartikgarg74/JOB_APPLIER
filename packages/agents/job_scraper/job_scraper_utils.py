import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional

class RateLimiter:
    def __init__(self, min_delay=1.0, max_delay=3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
    def wait(self):
        time.sleep(random.uniform(self.min_delay, self.max_delay))

class ProxyRotator:
    def __init__(self, proxies: Optional[List[str]] = None):
        self.proxies = proxies or []
        self.index = 0
    def get_proxy(self):
        if not self.proxies:
            return None
        proxy = self.proxies[self.index % len(self.proxies)]
        self.index += 1
        return proxy

class JobScraperBase:
    def __init__(self, rate_limiter=None, proxy_rotator=None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.proxy_rotator = proxy_rotator or ProxyRotator()
    def search_jobs(self, query: str, location: str = "", num_results: int = 10) -> List[Dict]:
        raise NotImplementedError

class IndeedScraper(JobScraperBase):
    BASE_URL = "https://www.indeed.com/jobs"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    def search_jobs(self, query: str, location: str = "", num_results: int = 10) -> List[Dict]:
        jobs = []
        params = {"q": query, "l": location}
        start = 0
        while len(jobs) < num_results:
            params["start"] = start
            proxy = self.proxy_rotator.get_proxy()
            proxies = {"http": proxy, "https": proxy} if proxy else None
            try:
                resp = requests.get(self.BASE_URL, params=params, proxies=proxies, headers=self.HEADERS, timeout=10)
                resp.raise_for_status()
            except Exception as e:
                print(f"[IndeedScraper] Request failed: {e}")
                break
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select(".jobsearch-SerpJobCard, .result")
            if not cards:
                print("[IndeedScraper] No job cards found. HTML may have changed or bot blocked.")
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
        jobs = []
        params = {"keywords": query, "location": location}
        start = 0
        while len(jobs) < num_results:
            params["start"] = start
            proxy = self.proxy_rotator.get_proxy()
            proxies = {"http": proxy, "https": proxy} if proxy else None
            try:
                resp = requests.get(self.BASE_URL, params=params, proxies=proxies, headers=self.HEADERS, timeout=10)
                resp.raise_for_status()
            except Exception as e:
                print(f"[LinkedInScraper] Request failed: {e}")
                break
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select(".result-card.job-result-card, .base-card")
            if not cards:
                print("[LinkedInScraper] No job cards found. HTML may have changed or bot blocked.")
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
        jobs = []
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
                print(f"[GlassdoorScraper] Request failed: {e}")
                break
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select(".react-job-listing, .jl")
            if not cards:
                print("[GlassdoorScraper] No job cards found. HTML may have changed or bot blocked.")
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
        jobs = []
        params = {"q": f"{query} jobs near {location}" if location else f"{query} jobs"}
        try:
            proxy = self.proxy_rotator.get_proxy()
            proxies = {"http": proxy, "https": proxy} if proxy else None
            resp = requests.get(self.BASE_URL, params=params, proxies=proxies, headers=self.HEADERS, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"[GoogleJobsScraper] Request failed: {e}")
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        # Google Jobs cards are not standard HTML and may not be present; this is a best-effort demo
        cards = soup.select(".BjJfJf.PUpOsf")  # This selector may change
        if not cards:
            print("[GoogleJobsScraper] No job cards found. Google may have blocked scraping or changed HTML.")
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
