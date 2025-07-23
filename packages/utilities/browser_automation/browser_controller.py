# packages/utilities/browser_automation/browser_controller.py

# This file would contain functions to control a web browser for scraping and application automation
# using libraries like Selenium or Playwright.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class BrowserController:
    """Controls a web browser for automation tasks."""

    def __init__(self, headless: bool = True):
        print(f"Initializing BrowserController (headless: {headless})...")
        self.driver = None
        self.headless = headless

    def launch_browser(self):
        """Launches the Chrome browser."""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        # Add other options as needed, e.g., user-agent, proxy

        # Assuming chromedriver is in PATH or specify service=Service('/path/to/chromedriver')
        self.driver = webdriver.Chrome(options=options)
        print("Browser launched.")

    def close_browser(self):
        """Closes the browser."""
        if self.driver:
            self.driver.quit()
            print("Browser closed.")

    def navigate_to(self, url: str):
        """Navigates to a given URL."""
        if not self.driver:
            self.launch_browser()
        print(f"Navigating to: {url}")
        self.driver.get(url)

    def find_element(self, by: By, value: str, timeout: int = 10):
        """Finds an element on the page with a wait condition."""
        if not self.driver:
            raise RuntimeError("Browser not launched.")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"Timeout: Element not found by {by} with value {value}")
            return None
        except NoSuchElementException:
            print(f"No such element: Element not found by {by} with value {value}")
            return None

    def fill_form_field(self, by: By, value: str, text: str):
        """Fills a form field with the given text."""
        element = self.find_element(by, value)
        if element:
            element.send_keys(text)
            print(f"Filled field by {by} with value {value}.")
            return True
        return False

    def click_element(self, by: By, value: str):
        """Clicks an element on the page."""
        element = self.find_element(by, value)
        if element:
            element.click()
            print(f"Clicked element by {by} with value {value}.")
            return True
        return False

    def get_page_source(self) -> str:
        """Returns the current page's HTML source."""
        if self.driver:
            return self.driver.page_source
        return ""

    def take_screenshot(self, filename: str = "screenshot.png"):
        """Takes a screenshot of the current page."""
        if self.driver:
            self.driver.save_screenshot(filename)
            print(f"Screenshot saved to {filename}")
