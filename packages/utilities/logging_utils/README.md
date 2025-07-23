# Logging Utilities

## Purpose
This module provides a centralized function to set up and configure logging for the entire Job Applier application. It ensures consistent log levels, formatting, and output destinations (e.g., console, file) across different components, making it easier to monitor application behavior, debug issues, and track events.

## Dependencies
- `logging`: Python's standard library for logging.

## Key Components
- `setup_logging(log_level_str: str = "INFO")`: This function initializes the logging system.
  - `log_level_str`: A string representing the desired logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"). Defaults to "INFO".

## Workflow
1. **Level Conversion**: Converts the input `log_level_str` into a `logging` module constant (e.g., "INFO" becomes `logging.INFO`).
2. **Basic Configuration**: Sets up the basic logging configuration, including:
   - `level`: The minimum logging level to capture.
   - `format`: Defines the structure of log messages (timestamp, logger name, level, message).
   - `handlers`: Specifies where log messages should be sent. By default, it configures a `StreamHandler` to output logs to the console.
3. **Optional File Handler**: The code includes commented-out sections for adding a `FileHandler`, which can be uncommented and configured to write logs to a file.
4. **Confirmation**: Logs an informational message confirming that logging has been set up and indicating the active log level.

## Usage Example
To set up logging in any part of the application, simply import and call `setup_logging()`:

```python
from packages.utilities.logging_utils import setup_logging
import logging

# Set up logging at the beginning of your application or module
setup_logging("DEBUG") # Set to DEBUG to see all messages

# Get a logger instance for your module
logger = logging.getLogger(__name__)

# Log messages at different levels
logger.debug("This is a debug message.")
logger.info("This is an informational message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.critical("This is a critical message.")
```

## Configuration
- **Log Level**: Can be controlled via the `log_level_str` parameter. It's recommended to configure this via environment variables or a central configuration file in a production environment.
- **File Logging**: To enable file logging, uncomment and configure the `FileHandler` section within the `setup_logging` function. You can specify the log file path and format.

## Contributing
When contributing to this module:
- Ensure that any changes maintain the simplicity and effectiveness of the logging setup.
- Avoid introducing complex logging configurations that might be difficult to manage.
- Consider adding support for more advanced logging features (e.g., rotating file handlers, remote logging) if required by future application needs, but keep them optional and configurable.