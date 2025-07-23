# Browser Automation

## Purpose
This module provides functionalities to control a web browser for various automation tasks, such as web scraping, form filling, and general application interaction. It is designed to abstract away the complexities of browser automation libraries, offering a simplified interface for common operations.

## Dependencies
- `selenium`: The primary library used for browser automation. This module specifically uses `webdriver.Chrome`.
- `selenium.webdriver.common.by`: For locating elements using different strategies (e.g., `By.ID`, `By.XPATH`).
- `selenium.webdriver.support.ui.WebDriverWait`: For explicit waits to ensure elements are present before interaction.
- `selenium.webdriver.support.expected_conditions`: Provides common conditions to wait for.

## Key Components
### `BrowserController` Class
This class encapsulates all browser automation functionalities.

- **`__init__(self, headless: bool = True)`**
  - Initializes the `BrowserController`. The `headless` parameter determines if the browser runs in headless mode (without a visible UI).

- **`launch_browser(self)`**
  - Launches a Chrome browser instance. Configures options such as headless mode, sandbox disabling, and shared memory usage.

- **`close_browser(self)`**
  - Closes the active browser instance.

- **`navigate_to(self, url: str)`**
  - Navigates the browser to the specified URL. If the browser is not already launched, it will launch it.

- **`find_element(self, by: By, value: str, timeout: int = 10)`**
  - Finds a web element on the page using the specified `By` strategy and `value`. It waits for the element to be present for a given `timeout`.
  - Returns the found element or `None` if not found within the timeout.

- **`fill_form_field(self, by: By, value: str, text: str)`**
  - Locates a form field and fills it with the provided `text`.
  - Returns `True` if the field was successfully filled, `False` otherwise.

- **`click_element(self, by: By, value: str)`**
  - Locates and clicks a web element.
  - Returns `True` if the element was successfully clicked, `False` otherwise.

- **`get_page_source(self) -> str`**
  - Returns the HTML source code of the current page.

- **`take_screenshot(self, filename: str = "screenshot.png")`**
  - Takes a screenshot of the current browser view and saves it to the specified `filename`.

## Workflow
1. **Initialization**: Create an instance of `BrowserController`, optionally specifying `headless=False` for visible browser operation.
2. **Launch**: Call `launch_browser()` to start the browser instance.
3. **Navigation**: Use `navigate_to(url)` to go to a specific web page.
4. **Interaction**: Utilize `find_element()`, `fill_form_field()`, and `click_element()` to interact with page elements.
5. **Data Extraction**: Use `get_page_source()` to retrieve the page's HTML for parsing.
6. **Cleanup**: Always call `close_browser()` to properly shut down the browser and release resources.

## Usage Examples

```python
from selenium.webdriver.common.by import By
from packages.utilities.browser_automation.browser_controller import BrowserController

def automate_login(url, username, password):
    controller = BrowserController(headless=False) # Set to False to see the browser
    try:
        controller.launch_browser()
        controller.navigate_to(url)

        # Fill username and password fields
        controller.fill_form_field(By.ID, "username", username)
        controller.fill_form_field(By.NAME, "password", password)

        # Click the login button
        controller.click_element(By.XPATH, "//button[@type='submit']")

        print("Login automation complete. Check browser for result.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        controller.close_browser()

# Example usage (replace with actual URL and credentials)
# automate_login("https://example.com/login", "myuser", "mypassword")


def scrape_data(url):
    controller = BrowserController()
    data = []
    try:
        controller.launch_browser()
        controller.navigate_to(url)

        # Example: Find all paragraph elements and extract text
        # This is a simplified example; more complex scraping would involve loops and specific selectors
        element = controller.find_element(By.TAG_NAME, "body")
        if element:
            print(f"Page source length: {len(controller.get_page_source())} characters")
            # Further parsing of page source would be needed here

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    finally:
        controller.close_browser()

# Example usage
# scrape_data("https://www.google.com")
```

## Error Handling
The `find_element` method includes error handling for `TimeoutException` and `NoSuchElementException`, printing messages if an element is not found within the specified timeout or does not exist. Other methods rely on the success of `find_element` and will return `False` or raise `RuntimeError` if the browser is not launched.

## Testing
Automated tests for this module would involve launching a browser, navigating to test pages (local or remote), performing actions, and asserting the expected outcomes or state changes. Mocking the `selenium` WebDriver might be necessary for unit tests that don't require a full browser launch.