# Retry Utilities

## Purpose
This module provides a flexible decorator, `retry_with_exponential_backoff`, to enhance the robustness of functions by automatically retrying them in case of specified errors. It implements an exponential backoff strategy, which increases the delay between retries, preventing overwhelming external services and allowing transient issues to resolve.

## Dependencies
- `logging`: For logging retry attempts and failures.
- `functools`: For preserving the original function's metadata when using the decorator.
- `time`: **(Implicitly required)** The `time.sleep()` function is used within the decorator, so the `time` module must be imported in the file where this decorator is defined.

## Key Components
- `retry_with_exponential_backoff(max_retries: int = 5, initial_delay: float = 1.0, backoff_factor: float = 2.0, errors: tuple = (Exception,))`:
  - A decorator function that takes the following parameters:
    - `max_retries` (int): The maximum number of times the decorated function will be retried. Defaults to 5.
    - `initial_delay` (float): The delay in seconds before the first retry. Defaults to 1.0.
    - `backoff_factor` (float): The multiplier for the delay after each subsequent retry. For example, a factor of 2.0 means the delay doubles each time. Defaults to 2.0.
    - `errors` (tuple): A tuple of exception types that, if raised by the decorated function, will trigger a retry. Defaults to `(Exception,)`, meaning it will retry on any exception.

## Workflow
1. When the decorated function is called, it attempts to execute.
2. If the function executes successfully, its result is returned immediately.
3. If the function raises an exception that is included in the `errors` tuple:
   - A warning is logged, indicating the failed attempt.
   - If `max_retries` has not been reached, the execution pauses for a calculated `delay`.
   - The `delay` is then increased by `backoff_factor` for the next attempt.
   - The function is retried.
4. If all `max_retries` are exhausted and the function still fails, the last exception is re-raised.

## Usage Example
```python
import logging
import time # Don't forget to import time!
from packages.utilities.retry_utils import retry_with_exponential_backoff

# Configure basic logging for demonstration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

call_count = 0

@retry_with_exponential_backoff(max_retries=3, initial_delay=0.5, backoff_factor=2, errors=(ValueError, ConnectionError))
def unreliable_function():
    global call_count
    call_count += 1
    logging.info(f"Attempting unreliable_function, call count: {call_count}")
    if call_count < 3:
        if call_count == 1:
            raise ValueError("Simulating a value error")
        else:
            raise ConnectionError("Simulating a connection error")
    return "Success!"

if __name__ == "__main__":
    try:
        result = unreliable_function()
        print(f"Function returned: {result}")
    except (ValueError, ConnectionError) as e:
        print(f"Function failed after retries: {e}")

    call_count = 0 # Reset for another example

    @retry_with_exponential_backoff(max_retries=2, initial_delay=0.1, errors=(TypeError,))
    def another_unreliable_function():
        global call_count
        call_count += 1
        logging.info(f"Attempting another_unreliable_function, call count: {call_count}")
        if call_count < 3:
            raise TypeError("Simulating a type error")
        return "Another Success!"

    try:
        result = another_unreliable_function()
        print(f"Function returned: {result}")
    except TypeError as e:
        print(f"Function failed after retries: {e}")
```

## Contributing
When contributing to this module:
- Ensure that any changes maintain the decorator's functionality and error handling.
- Consider adding more advanced retry strategies (e.g., jitter, circuit breaker patterns) if required by future application needs, but keep the core decorator simple and focused.