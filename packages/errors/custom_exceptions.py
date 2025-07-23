from typing import Any, Optional

class JobApplierException(Exception):
    """Custom exception for Job Applier Agent application-specific errors."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[dict[Any, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class AgentOrchestrationError(JobApplierException):
    """Custom exception for errors during agent orchestration."""
    def __init__(self, message: str = "Agent orchestration failed.", status_code: int = 500, details: Optional[dict[Any, Any]] = None):
        super().__init__(message, status_code, details)

class UnicornError(JobApplierException):
    """Custom exception for errors specific to the Unicorn Agent."""
    def __init__(self, message: str = "Unicorn operation failed.", status_code: int = 500, details: Optional[dict[Any, Any]] = None):
        super().__init__(message, status_code, details)

class NotificationError(JobApplierException):
    """Custom exception for errors during notification processes."""
    def __init__(self, message: str = "Notification delivery failed.", status_code: int = 500, details: Optional[dict[Any, Any]] = None):
        super().__init__(message, status_code, details)

class MicroserviceCommunicationError(JobApplierException):
    """Custom exception for errors during inter-microservice communication."""
    def __init__(self, message: str = "Microservice communication failed.", status_code: int = 500, details: Optional[dict[Any, Any]] = None):
        super().__init__(message, status_code, details)

class DatabaseError(JobApplierException):
    """Custom exception for database-related errors."""
    def __init__(self, message: str = "Database operation failed.", status_code: int = 500, details: Optional[dict[Any, Any]] = None):
        super().__init__(message, status_code, details)