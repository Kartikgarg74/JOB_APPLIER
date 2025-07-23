# Custom Exceptions Module

## Purpose
This module (`custom_exceptions.py`) defines a hierarchy of custom exception classes for the Job Applier Agent application. These exceptions provide a structured way to handle and categorize application-specific errors, allowing for more precise error reporting and handling throughout the system.

## Key Components

### `JobApplierException` (Base Exception)
- **Purpose**: The base class for all custom exceptions within the Job Applier Agent application. It extends Python's built-in `Exception` class.
- **Attributes**:
  - `message` (str): A human-readable error message.
  - `status_code` (int, default: 500): An HTTP status code relevant to the error (useful for API responses).
  - `details` (dict, default: `{}`): A dictionary for additional, structured error details.

### `AgentOrchestrationError`
- **Purpose**: Raised when an error occurs during the orchestration of various agents (e.g., when managing the flow between job scraping, resume parsing, application automation, etc.).
- **Inherits From**: `JobApplierException`
- **Default Message**: "Agent orchestration failed."

### `UnicornError`
- **Purpose**: Raised for errors specific to the "Unicorn Agent" (presumably a specialized or critical agent within the system).
- **Inherits From**: `JobApplierException`
- **Default Message**: "Unicorn operation failed."

### `NotificationError`
- **Purpose**: Raised when there are issues with sending or processing notifications (e.g., email, SMS, in-app notifications).
- **Inherits From**: `JobApplierException`
- **Default Message**: "Notification delivery failed."

### `MicroserviceCommunicationError`
- **Purpose**: Raised when communication fails between different microservices or components of the application (e.g., API calls between services).
- **Inherits From**: `JobApplierException`
- **Default Message**: "Microservice communication failed."

## Usage
These custom exceptions should be raised in appropriate scenarios within the application logic to signal specific error conditions. They can then be caught and handled by higher-level error handlers, such as FastAPI exception handlers, to return consistent and informative error responses to clients.

```python
from packages.errors.custom_exceptions import AgentOrchestrationError, JobApplierException

def process_job_application(job_data):
    try:
        # Simulate an operation that might fail
        if not job_data.get("valid"): # Example condition
            raise AgentOrchestrationError("Invalid job data provided for processing.", status_code=400, details={"field": "valid", "reason": "missing"})
        print("Job application processed successfully.")
    except AgentOrchestrationError as e:
        print(f"Caught AgentOrchestrationError: {e.message} (Status: {e.status_code}, Details: {e.details})")
    except JobApplierException as e:
        print(f"Caught a general JobApplierException: {e.message}")
    except Exception as e:
        print(f"Caught an unexpected error: {e}")

# Example usage
process_job_application({"valid": False})
process_job_application({"valid": True})
```

## Error Handling Strategy
By using these custom exceptions, the application can implement a centralized error handling strategy. For instance, a global exception handler in a FastAPI application could catch `JobApplierException` instances and automatically convert them into appropriate HTTP responses with the correct status codes and error details.