# Notification Service Module (`notification_service.py`)

## Purpose
This module defines the `NotificationService` class, which provides a centralized way to send various types of notifications (e.g., email, SMS, in-app) within the Job Applier Agent application. It abstracts the underlying communication mechanisms with third-party services like Mailgun (for email) and Twilio (for SMS), and includes simulation capabilities for development and testing when API credentials are not configured.

## Dependencies
- `logging`: For logging service operations and errors.
- `typing.List`, `typing.Dict`, `typing.Any`: For type hinting.
- `aiohttp`: An asynchronous HTTP client for making requests to external APIs (Mailgun, Twilio).
- `json`: For handling JSON data.
- `packages.errors.custom_exceptions.NotificationError`: Custom exception for notification-specific errors.
- `packages.config.settings.settings`: To retrieve API keys and domain information for Mailgun and Twilio.

## Key Components

### `NotificationService` Class
- **Purpose**: Manages the sending of notifications.
- **Initialization (`__init__`)**:
  - Retrieves API keys and domain information from `settings` (Mailgun API key, Mailgun domain, Twilio Account SID, Twilio Auth Token, Twilio Phone Number).
  - Logs warnings if any required credentials are not set, indicating that corresponding notification types will be simulated.

### Private Helper Methods

#### `_make_request(self, method: str, url: str, headers: Dict, data: Any = None, auth: aiohttp.BasicAuth = None) -> Dict`
- **Purpose**: A generic asynchronous method for making HTTP requests to external APIs.
- **Functionality**: Uses `aiohttp.ClientSession` to perform `GET`, `POST`, etc., requests. Handles `aiohttp.ClientError` and raises `NotificationError` on failure.

#### `_send_email(self, recipient: str, message: str, details: Dict[str, Any]) -> bool`
- **Purpose**: Sends an email notification using Mailgun.
- **Functionality**: Constructs a Mailgun API request with recipient, subject (from `details`), and message. If Mailgun credentials are not set, it logs a simulation message.

#### `_send_sms(self, recipient: str, message: str, details: Dict[str, Any]) -> bool`
- **Purpose**: Sends an SMS notification using Twilio.
- **Functionality**: Constructs a Twilio API request with recipient, sender phone number, and message. If Twilio credentials are not set, it logs a simulation message.

#### `_send_in_app_notification(self, recipient: str, message: str, details: Dict[str, Any]) -> bool`
- **Purpose**: Simulates sending an in-app notification.
- **Functionality**: Currently a placeholder that logs the notification. In a full implementation, this would involve storing the notification in a database or pushing it via WebSockets.

### Public Methods

#### `send_notification(self, recipient: str, message: str, notification_type: str = "email", details: Dict[str, Any] = None) -> bool`
- **Purpose**: The primary method for sending a single notification.
- **Parameters**:
  - `recipient` (str): The target (e.g., email address, phone number).
  - `message` (str): The content of the notification.
  - `notification_type` (str): The type of notification ("email", "sms", "in-app").
  - `details` (Dict[str, Any]): Additional data like email subject.
- **Functionality**: Dispatches the request to the appropriate private helper method based on `notification_type`. Raises `NotificationError` for unsupported types or failures.

#### `send_bulk_notifications(self, recipients: List[str], message: str, notification_type: str = "email", details: Dict[str, Any] = None) -> Dict[str, bool]`
- **Purpose**: Sends the same notification to multiple recipients.
- **Parameters**:
  - `recipients` (List[str]): A list of target identifiers.
  - `message` (str): The content of the notification.
  - `notification_type` (str): The type of notification.
  - `details` (Dict[str, Any]): Additional data.
- **Functionality**: Iterates through the list of recipients, calling `send_notification` for each. Returns a dictionary mapping each recipient to a boolean indicating success or failure.

## Usage Examples

```python
import asyncio
from packages.notifications.notification_service import NotificationService
from packages.errors.custom_exceptions import NotificationError

async def main():
    notification_service = NotificationService()

    # Example 1: Send an email
    try:
        success = await notification_service.send_notification(
            recipient="test@example.com",
            message="Hello from Job Applier Agent! Your application status has been updated.",
            notification_type="email",
            details={"subject": "Application Update"}
        )
        print(f"Email sent status: {success}")
    except NotificationError as e:
        print(f"Failed to send email: {e.message}")

    # Example 2: Send an SMS (if Twilio credentials are set)
    try:
        success = await notification_service.send_notification(
            recipient="+15551234567", # Replace with a valid phone number
            message="Your job application process is complete.",
            notification_type="sms"
        )
        print(f"SMS sent status: {success}")
    except NotificationError as e:
        print(f"Failed to send SMS: {e.message}")

    # Example 3: Send an in-app notification
    try:
        success = await notification_service.send_notification(
            recipient="user_id_123",
            message="New job recommendation available!",
            notification_type="in-app",
            details={"category": "recommendation"}
        )
        print(f"In-app notification sent status: {success}")
    except NotificationError as e:
        print(f"Failed to send in-app notification: {e.message}")

    # Example 4: Send bulk emails
    try:
        bulk_recipients = ["user1@example.com", "user2@example.com"]
        bulk_results = await notification_service.send_bulk_notifications(
            recipients=bulk_recipients,
            message="Important update for all users.",
            notification_type="email",
            details={"subject": "Important Notice"}
        )
        print(f"Bulk email results: {bulk_results}")
    except NotificationError as e:
        print(f"Failed to send bulk notifications: {e.message}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration
For actual email and SMS sending, ensure the following environment variables (or their equivalents in `packages.config.settings`) are properly configured:
- `MAILGUN_API_KEY`
- `MAILGUN_DOMAIN`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`

If these are not set, the service will log messages indicating that notifications are being simulated.