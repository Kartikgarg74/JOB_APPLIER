import time
import logging
from functools import wraps
import time

__all__ = ["retry_with_exponential_backoff"]

logger = logging.getLogger(__name__)


def retry_with_exponential_backoff(
    max_retries: int = 5,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    errors: tuple = (Exception,),
):  # Added errors parameter
    """
    A decorator that retries a function call with exponential backoff.

    Args:
        max_retries (int): The maximum number of times to retry the function.
        initial_delay (float): The initial delay in seconds before the first retry.
        backoff_factor (float): The factor by which the delay increases after each retry.
        errors (tuple): A tuple of exceptions to catch and retry on.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except errors as e:
                    logger.warning(
                        f"Attempt {i + 1}/{max_retries} failed for {func.__name__}: {e}"
                    )
                    if i < max_retries - 1:
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"All {max_retries} attempts failed for {func.__name__}."
                        )
                        raise  # Re-raise the last exception if all retries fail

        return wrapper

    return decorator
