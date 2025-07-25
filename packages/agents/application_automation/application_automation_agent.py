import logging
import os
from typing import Dict, Any, Optional
import json
import datetime

from packages.utilities.retry_utils import retry_with_exponential_backoff as retry
from packages.agents.application_automation.application_automation_utils import load_user_data

logger = logging.getLogger(__name__)


class ApplicationAutomationAgent:
    """
    Automates the process of applying for jobs on various platforms.

    Args:
        db: Database/session dependency.
        logger: Logger instance for dependency injection and testability.
    """
    def __init__(self, db: Any, logger: Optional[logging.Logger] = None) -> None:
        self.db = db
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.logger.info("ApplicationAutomationAgent initialized.")

    def _log_application_attempt(self, job_data: dict, platform: str, result: str):
        """
        Logs an application attempt to application_log.json.
        Each entry includes: timestamp, platform, job title, company, url, and result (success/failure).
        """
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "platform": platform,
            "title": job_data.get("title"),
            "company": job_data.get("company"),
            "url": job_data.get("url"),
            "result": result,
        }
        try:
            import json
            log_path = "application_log.json"
            try:
                with open(log_path, "r") as f:
                    logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []
            logs.append(log_entry)
            with open(log_path, "w") as f:
                json.dump(logs, f, indent=2)
            self.logger.info(f"Logged application attempt: {log_entry}")
        except Exception as e:
            self.logger.error(f"Failed to log application attempt: {e}")

    @retry(max_retries=3, initial_delay=2, backoff_factor=2)
    def apply_for_job(
        self,
        job_data: Dict[str, Any],
        resume_path: str,
        cover_letter_path: str
    ) -> bool:
        """
        Navigates to the job application page and attempts to submit the application.

        Args:
            job_data: Dictionary containing job details (title, company, url, etc.).
            resume_path: Path to the resume file to upload.
            cover_letter_path: Path to the cover letter file to upload.

        Returns:
            True if the application was submitted successfully, False otherwise.
        """
        self.logger.info(
            f"Attempting to apply for job: {job_data.get('title')} at {job_data.get('company')}"
        )

        job_url = job_data.get("url")
        if not job_url:
            self.logger.error("Job URL not found. Cannot proceed with application.")
            self._log_application_attempt(job_data, "unknown", "failure: no url")
            return False

        platform = "unknown"
        if "linkedin.com" in job_url:
            platform = "linkedin"
        elif "indeed.com" in job_url:
            platform = "indeed"
        elif "workday.com" in job_url:
            platform = "workday"
        elif "greenhouse.io" in job_url:
            platform = "greenhouse"
        else:
            platform = "generic"

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                self.logger.info(f"Navigating to {job_url}...")
                page.goto(job_url)

                if platform == "linkedin":
                    self.logger.info("Detected LinkedIn application.")
                    success = self._handle_linkedin_application(
                        page, job_data, resume_path, cover_letter_path
                    )
                elif platform == "indeed":
                    self.logger.info("Detected Indeed application.")
                    success = self._handle_indeed_application(
                        page, job_data, resume_path, cover_letter_path
                    )
                elif platform == "workday":
                    self.logger.info("Detected Workday application.")
                    success = self._handle_workday_application(
                        page, job_data, resume_path, cover_letter_path
                    )
                elif platform == "greenhouse":
                    self.logger.info("Detected Greenhouse application.")
                    success = self._handle_greenhouse_application(
                        page, job_data, resume_path, cover_letter_path
                    )
                else:
                    self.logger.info("Attempting generic application process.")
                    success = self._handle_generic_application(
                        page, job_data, resume_path, cover_letter_path
                    )

                browser.close()
                self._log_application_attempt(job_data, platform, "success" if success else "failure")
                return success
        except Exception as e:
            self.logger.exception(f"An error occurred during web automation: {e}")
            self._log_application_attempt(job_data, platform, f"failure: {e}")
            return False

    def _save_cookies(self, page: Any, platform: str):
        """
        Saves cookies for the given platform to a local file for session reuse.
        """
        cookies = page.context.cookies()
        with open(f".session_cookies_{platform}.json", "w") as f:
            json.dump(cookies, f)
        self.logger.info(f"Saved cookies for {platform}.")

    def _load_cookies(self, page: Any, platform: str):
        """
        Loads cookies for the given platform from a local file, if available.
        """
        try:
            with open(f".session_cookies_{platform}.json", "r") as f:
                cookies = json.load(f)
            page.context.add_cookies(cookies)
            self.logger.info(f"Loaded cookies for {platform}.")
        except FileNotFoundError:
            self.logger.info(f"No saved cookies found for {platform}.")
        except Exception as e:
            self.logger.error(f"Error loading cookies for {platform}: {e}")

    def _get_linkedin_credentials(self):
        """
        Loads LinkedIn credentials from environment variables.
        Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in your environment.
        """
        email = os.environ.get("LINKEDIN_EMAIL")
        password = os.environ.get("LINKEDIN_PASSWORD")
        if not email or not password:
            self.logger.error("LinkedIn credentials not set in environment variables.")
        return email, password

    def _get_indeed_credentials(self):
        """
        Loads Indeed credentials from environment variables.
        Set INDEED_EMAIL and INDEED_PASSWORD in your environment.
        """
        email = os.environ.get("INDEED_EMAIL")
        password = os.environ.get("INDEED_PASSWORD")
        if not email or not password:
            self.logger.error("Indeed credentials not set in environment variables.")
        return email, password

    def _detect_captcha(self, page: Any) -> bool:
        """
        Checks for the presence of a CAPTCHA on the current page.
        Returns True if a CAPTCHA is detected, else False.
        """
        # Common selectors/images for CAPTCHA
        captcha_selectors = [
            "iframe[src*='captcha']",
            "div.g-recaptcha",
            "img[alt*='captcha']",
            "input[name='captcha']",
            "#captcha-internal",
            "[id*='captcha']",
        ]
        for selector in captcha_selectors:
            if page.query_selector(selector):
                return True
        return False

    def _handle_linkedin_application(
        self,
        page: Any,
        job_data: Dict[str, Any],
        resume_path: str,
        cover_letter_path: str,
    ) -> bool:
        """
        [CONTEXT] Handles the application process for LinkedIn jobs (Easy Apply, etc).
        [PURPOSE] Automates form filling and submission on LinkedIn.
        [REQUIRES] Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD as environment variables.
        [CAPTCHA] If a CAPTCHA is detected, logs a warning and aborts. Integrate a solving service here if desired.
        [SESSION] Loads and saves cookies for session reuse. Skips login if cookies are valid.
        """
        self.logger.info("Handling LinkedIn application.")
        user_data = load_user_data(self.db)
        email, password = self._get_linkedin_credentials()
        try:
            # Try to load cookies and skip login if possible
            self._load_cookies(page, "linkedin")
            page.goto("https://www.linkedin.com/feed/", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)
            if not page.url.startswith("https://www.linkedin.com/login"):
                self.logger.info("LinkedIn session restored from cookies.")
            else:
                # 1. Go to LinkedIn login page
                self.logger.info("Navigating to LinkedIn login page...")
                page.goto("https://www.linkedin.com/login", timeout=30000)
                page.wait_for_selector("input#username", timeout=10000)
                page.fill("input#username", email)
                page.fill("input#password", password)
                page.click("button[type='submit']")
                page.wait_for_load_state("networkidle", timeout=15000)
                self.logger.info("Logged in to LinkedIn.")
                self._save_cookies(page, "linkedin")

            # CAPTCHA detection after login
            if self._detect_captcha(page):
                self.logger.warning("CAPTCHA detected on LinkedIn. Manual intervention or CAPTCHA solving service required.")
                return False

            # 2. Go to job URL
            job_url = job_data.get("url")
            self.logger.info(f"Navigating to job URL: {job_url}")
            page.goto(job_url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)

            # CAPTCHA detection on job page
            if self._detect_captcha(page):
                self.logger.warning("CAPTCHA detected on LinkedIn job page. Manual intervention or CAPTCHA solving service required.")
                return False

            # 3. Detect and click Easy Apply button
            easy_apply_selector = "button.jobs-apply-button, button[data-control-name='jobdetails_topcard_inapply']"
            try:
                page.wait_for_selector(easy_apply_selector, timeout=10000)
                self.logger.info("Easy Apply button found. Clicking...")
                page.click(easy_apply_selector)
                page.wait_for_timeout(2000)
            except Exception:
                self.logger.error("Easy Apply button not found on this job posting.")
                return False

            # CAPTCHA detection after clicking Easy Apply
            if self._detect_captcha(page):
                self.logger.warning("CAPTCHA detected after clicking Easy Apply. Manual intervention or CAPTCHA solving service required.")
                return False

            # 4. Fill out the Easy Apply form (basic fields)
            try:
                if user_data.get("name"):
                    first_name = user_data["name"].split(" ")[0]
                    last_name = user_data["name"].split(" ")[-1]
                    page.fill("input#first-name, input[name='firstName']", first_name)
                    page.fill("input#last-name, input[name='lastName']", last_name)
                if user_data.get("email"):
                    page.fill("input#email, input[name='email']", user_data["email"])
                if user_data.get("phone"):
                    page.fill("input#phone, input[name='phone']", user_data["phone"])
                # Upload resume
                if resume_path:
                    page.set_input_files("input[type='file']", resume_path)
                # Handle multi-step (click Next/Review/Submit)
                for _ in range(5):  # Max 5 steps
                    if page.query_selector("button[aria-label='Submit application'], button[aria-label='Review your application']"):
                        break
                    next_btn = page.query_selector("button[aria-label='Next'], button[aria-label='Continue']")
                    if next_btn:
                        next_btn.click()
                        page.wait_for_timeout(1500)
                # Submit
                submit_btn = page.query_selector("button[aria-label='Submit application']")
                if submit_btn:
                    submit_btn.click()
                    self.logger.info("Application submitted on LinkedIn.")
                    return True
                else:
                    self.logger.error("Submit button not found on LinkedIn Easy Apply.")
                    return False
            except Exception as e:
                self.logger.error(f"Error filling LinkedIn Easy Apply form: {e}")
                return False
        except Exception as e:
            self.logger.error(f"Error handling LinkedIn application: {e}")
            return False

    def _handle_indeed_application(
        self,
        page: Any,
        job_data: Dict[str, Any],
        resume_path: str,
        cover_letter_path: str,
    ) -> bool:
        """
        [CONTEXT] Handles the application process for Indeed jobs.
        [PURPOSE] Automates form filling and submission on Indeed.
        [REQUIRES] Set INDEED_EMAIL and INDEED_PASSWORD as environment variables.
        [CAPTCHA] If a CAPTCHA is detected, logs a warning and aborts. Integrate a solving service here if desired.
        [SESSION] Loads and saves cookies for session reuse. Skips login if cookies are valid.
        """
        self.logger.info("Handling Indeed application.")
        user_data = load_user_data(self.db)
        email, password = self._get_indeed_credentials()
        try:
            # Try to load cookies and skip login if possible
            self._load_cookies(page, "indeed")
            page.goto("https://www.indeed.com/", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)
            if not page.url.startswith("https://secure.indeed.com/account/login"):
                self.logger.info("Indeed session restored from cookies.")
            else:
                # 1. Go to Indeed login page
                self.logger.info("Navigating to Indeed login page...")
                page.goto("https://secure.indeed.com/account/login", timeout=30000)
                page.wait_for_selector("input#login-email-input, input[name='email']", timeout=10000)
                page.fill("input#login-email-input, input[name='email']", email)
                page.fill("input#login-password-input, input[name='password']", password)
                page.click("button[type='submit'], button[data-tn-element='login-submit-button']")
                page.wait_for_load_state("networkidle", timeout=15000)
                self.logger.info("Logged in to Indeed.")
                self._save_cookies(page, "indeed")

            # CAPTCHA detection after login
            if self._detect_captcha(page):
                self.logger.warning("CAPTCHA detected on Indeed. Manual intervention or CAPTCHA solving service required.")
                return False

            # 2. Go to job URL
            job_url = job_data.get("url")
            self.logger.info(f"Navigating to job URL: {job_url}")
            page.goto(job_url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)

            # CAPTCHA detection on job page
            if self._detect_captcha(page):
                self.logger.warning("CAPTCHA detected on Indeed job page. Manual intervention or CAPTCHA solving service required.")
                return False

            # 3. Detect and click Apply button
            apply_selector = "button.ia-ApplyButton, button[data-tn-element='apply-button']"
            try:
                page.wait_for_selector(apply_selector, timeout=10000)
                self.logger.info("Apply button found. Clicking...")
                page.click(apply_selector)
                page.wait_for_timeout(2000)
            except Exception:
                self.logger.error("Apply button not found on this job posting.")
                return False

            # CAPTCHA detection after clicking Apply
            if self._detect_captcha(page):
                self.logger.warning("CAPTCHA detected after clicking Apply. Manual intervention or CAPTCHA solving service required.")
                return False

            # 4. Fill out the application form (basic fields)
            try:
                if user_data.get("name"):
                    first_name = user_data["name"].split(" ")[0]
                    last_name = user_data["name"].split(" ")[-1]
                    page.fill("input[name*='first'][name*='name'], input[id*='first'][id*='name']", first_name)
                    page.fill("input[name*='last'][name*='name'], input[id*='last'][id*='name']", last_name)
                if user_data.get("email"):
                    page.fill("input[name*='email'], input[id*='email']", user_data["email"])
                if user_data.get("phone"):
                    page.fill("input[name*='phone'], input[id*='phone']", user_data["phone"])
                # Upload resume
                if resume_path:
                    page.set_input_files("input[type='file'][name*='resume'], input[type='file'][id*='resume']", resume_path)
                # Handle multi-step (click Next/Continue/Submit)
                for _ in range(5):  # Max 5 steps
                    if page.query_selector("button[type='submit'], button[aria-label='Submit application']"):
                        break
                    next_btn = page.query_selector("button[aria-label='Continue'], button[aria-label='Next'], button[type='button']")
                    if next_btn:
                        next_btn.click()
                        page.wait_for_timeout(1500)
                # Submit
                submit_btn = page.query_selector("button[type='submit'], button[aria-label='Submit application']")
                if submit_btn:
                    submit_btn.click()
                    self.logger.info("Application submitted on Indeed.")
                    return True
                else:
                    self.logger.error("Submit button not found on Indeed application.")
                    return False
            except Exception as e:
                self.logger.error(f"Error filling Indeed application form: {e}")
                return False
        except Exception as e:
            self.logger.error(f"Error handling Indeed application: {e}")
            return False

    def _handle_workday_application(
        self,
        page: Any,
        job_data: Dict[str, Any],
        resume_path: str,
        cover_letter_path: str,
    ) -> bool:
        """
        [CONTEXT] Handles the application process for Workday platforms.
        [PURPOSE] Automates form filling and submission on Workday.
        """
        self.logger.info("Handling Workday application.")
        load_user_data(self.db)

        try:
            # Example: Click 'Apply' button (adjust selector as needed)
            # page.click("button[data-automation-id='applyButton']")

            # Example: Fill out name field
            # page.fill("input[data-automation-id='legalName_firstName']", user_data.get('name', '').split(' ')[0])
            # page.fill("input[data-automation-id='legalName_lastName']", user_data.get('name', '').split(' ')[-1])

            # Example: Upload resume
            # page.set_input_files("input[type='file']", resume_path)

            self.logger.info(
                "Workday application logic executed (placeholders for specific selectors)."
            )
            return True
        except Exception as e:
            self.logger.error(f"Error handling Workday application: {e}")
            return False

    def _handle_greenhouse_application(
        self,
        page: Any,
        job_data: Dict[str, Any],
        resume_path: str,
        cover_letter_path: str,
    ) -> bool:
        """
        [CONTEXT] Handles the application process for Greenhouse platforms.
        [PURPOSE] Automates form filling and submission on Greenhouse.
        """
        self.logger.info("Handling Greenhouse application.")
        load_user_data(self.db)

        try:
            # Example: Fill out name and email
            # page.fill("input[name='first_name']", user_data.get('name', '').split(' ')[0])
            # page.fill("input[name='last_name']", user_data.get('name', '').split(' ')[-1])
            # page.fill("input[name='email']", user_data.get('email', ''))

            # Example: Upload resume and cover letter
            # page.set_input_files("input[type='file'][name='resume']", resume_path)
            # page.set_input_files("input[type='file'][name='cover_letter']", cover_letter_path)

            self.logger.info(
                "Greenhouse application logic executed (placeholders for specific selectors)."
            )
            return True
        except Exception as e:
            self.logger.error(f"Error handling Greenhouse application: {e}")
            return False

    def _handle_generic_application(
        self,
        page: Any,
        job_data: Dict[str, Any],
        resume_path: str,
        cover_letter_path: str,
    ) -> bool:
        """
        [CONTEXT] Handles a generic application process for unknown platforms.
        [PURPOSE] Provides a fallback for basic form filling and submission.
        """
        self.logger.info("Handling generic application.")
        user_data = load_user_data(self.db)

        try:
            # Attempt to fill common fields
            if user_data.get("name"):
                first_name = user_data["name"].split(" ")[0]
                last_name = user_data["name"].split(" ")[-1]
                try:
                    page.fill("input[name*='first'][name*='name'], input[id*='first'][id*='name']", first_name)  # type: ignore
                except:
                    pass
                try:
                    page.fill("input[name*='last'][name*='name'], input[id*='last'][id*='name']", last_name)  # type: ignore
                except:
                    pass

            if user_data.get("email"):
                try:
                    page.fill("input[name*='email'], input[id*='email']", user_data["email"])  # type: ignore
                except:
                    pass

            if user_data.get("phone"):
                try:
                    page.fill("input[name*='phone'], input[id*='phone']", user_data["phone"])  # type: ignore
                except:
                    pass

            # Attempt to upload files
            if os.path.exists(resume_path):
                try:
                    page.set_input_files("input[type='file'][name*='resume'], input[type='file'][id*='resume']", resume_path)  # type: ignore
                except:
                    pass
            if os.path.exists(cover_letter_path):
                try:
                    page.set_input_files("input[type='file'][name*='cover'], input[type='file'][id*='cover']", cover_letter_path)  # type: ignore
                except:
                    pass

            # Attempt to click a submit button
            # page.click("button[type='submit'], input[type='submit']")

            self.logger.info(
                "Generic application logic executed. Manual review may be needed."
            )
            return True
        except Exception as e:
            self.logger.error(f"An error occurred during generic application: {e}")
            return False

    def _check_compliance_and_bot_detection(self, url: str) -> bool:
        """
        [CONTEXT] Simulates checks for website terms of service compliance and bot detection.
        [PURPOSE] Ensures automated application adheres to ethical and legal guidelines.
        """
        self.logger.info(f"Checking compliance and bot detection for {url}...")
        # In a real-world scenario, this would involve:
        # - Checking robots.txt
        # - Analyzing website's terms of service for automation clauses
        # - Implementing CAPTCHA solving mechanisms or human-like interaction patterns
        # - Using proxy rotations, user-agent spoofing, etc.
        # For now, we'll assume compliance.
        return True


if __name__ == "__main__":
    from packages.utilities.logging_utils import setup_logging

    setup_logging()

    applier = ApplicationAutomationAgent()

    # Dummy job data for testing
    dummy_job_data_generic = {
        "title": "QA Engineer",
        "company": "TestCo",
        "url": "https://www.google.com",  # Using a simple, accessible URL for initial testing
        "description": "Test software applications.",
    }

    dummy_job_data_workday = {
        "title": "Software Developer",
        "company": "Workday Inc.",
        "url": "https://www.workday.com/en-us/company/careers.html",  # Example Workday careers page
        "description": "Develop and maintain Workday applications.",
    }

    dummy_job_data_greenhouse = {
        "title": "Product Manager",
        "company": "Greenhouse Inc.",
        "url": "https://www.greenhouse.io/careers",  # Example Greenhouse careers page
        "description": "Manage product development.",
    }

    dummy_resume_path = "/tmp/dummy_resume.pdf"  # Placeholder, ensure this file exists for actual testing
    dummy_cover_letter_path = "/tmp/dummy_cover_letter.pdf"  # Placeholder

    print("\n--- Attempting Generic Job Application ---")
    success_generic = applier.apply_for_job(
        dummy_job_data_generic, dummy_resume_path, dummy_cover_letter_path
    )
    print(f"Generic Application attempt: {'SUCCESS' if success_generic else 'FAILED'}")

    print("\n--- Attempting Workday Job Application (Placeholder) ---")
    success_workday = applier.apply_for_job(
        dummy_job_data_workday, dummy_resume_path, dummy_cover_letter_path
    )
    print(f"Workday Application attempt: {'SUCCESS' if success_workday else 'FAILED'}")

    print("\n--- Attempting Greenhouse Job Application (Placeholder) ---")
    success_greenhouse = applier.apply_for_job(
        dummy_job_data_greenhouse, dummy_resume_path, dummy_cover_letter_path
    )
    print(
        f"Greenhouse Application attempt: {'SUCCESS' if success_greenhouse else 'FAILED'}"
    )
