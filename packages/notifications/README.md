# Notifications Package

## Purpose
This package provides a centralized service for sending various types of notifications across the Job Applier application. It abstracts the underlying communication mechanisms, allowing other parts of the system to send notifications without needing to know the specifics of email, SMS, or in-app messaging.

## Dependencies
- `logging`: For logging notification activities and errors.
- `packages.errors.custom_exceptions.NotificationError`: Custom exception for handling notification-specific errors.
- `aiohttp`: For asynchronous HTTP requests to external APIs (Mailgun, Twilio).

## Key Components

### `NotificationService`
- **Description**: Manages the dispatching of notifications to different channels.
- **Responsibilities**:
    - Sending emails via Mailgun.
    - Sending SMS messages via Twilio.
    - Sending in-app notifications.
    - Handling bulk notifications.
    - Logging notification attempts and failures.

## Configuration
To enable real email and SMS sending, the following environment variables must be set:

**Mailgun (for email):**
- `MAILGUN_API_KEY`: Your Mailgun API key.
- `MAILGUN_DOMAIN`: Your Mailgun sending domain.

**Twilio (for SMS):**
- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID.
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token.
- `TWILIO_PHONE_NUMBER`: Your Twilio phone number (e.g., `+15017122661`).

If these environment variables are not set, the service will simulate sending notifications.

## Usage Examples

```python
import asyncio
from packages.notifications.notification_service import NotificationService
from packages.errors.custom_exceptions import NotificationError

async def example_usage():
    notification_service = NotificationService()

    # Send an email notification
    try:
        await notification_service.send_notification(
            recipient="test@example.com",
            message="Your job application for Software Engineer has been submitted.",
            notification_type="email",
            details={"subject": "Application Submitted!"}
        )
        print("Email sent successfully.")
    except NotificationError as e:
        print(f"Failed to send email: {e.message}")

    # Send an SMS notification
    try:
        await notification_service.send_notification(
            recipient="+15551234567", # Use a valid phone number for Twilio
            message="Your application status has been updated.",
            notification_type="sms"
        )
        print("SMS sent successfully.")
    except NotificationError as e:
        print(f"Failed to send SMS: {e.message}")

    # Send an in-app notification
    try:
        await notification_service.send_notification(
            recipient="user_id_123",
            message="You have a new job match!",
            notification_type="in-app"
        )
        print("In-app notification sent successfully.")
    except NotificationError as e:
        print(f"Failed to send in-app notification: {e.message}")

    # Send bulk email notifications
    recipients = ["user1@example.com", "user2@example.com"]
    bulk_results = await notification_service.send_bulk_notifications(
        recipients,
        "Important update regarding your profile.",
        notification_type="email",
        details={"subject": "Profile Update"}
    )
    print(f"Bulk notification results: {bulk_results}")

if __name__ == "__main__":
    asyncio.run(example_usage())
```

## API Reference

### `NotificationService()`
Initializes the NotificationService.

### `async send_notification(recipient: str, message: str, notification_type: str = "email", details: Dict[str, Any] = None) -> bool`
Sends a single notification.
- `recipient` (str): The recipient's identifier (e.g., email address, phone number, user ID).
- `message` (str): The content of the notification.
- `notification_type` (str, optional): The type of notification ('email', 'sms', 'in-app'). Defaults to 'email'.
- `details` (Dict[str, Any], optional): Additional details specific to the notification type (e.g., `subject` for email).
- **Returns**: `True` if successful, `False` otherwise.
- **Raises**: `NotificationError` on failure.

### `async send_bulk_notifications(recipients: List[str], message: str, notification_type: str = "email", details: Dict[str, Any] = None) -> Dict[str, bool]`
Sends a notification to a list of recipients.
- `recipients` (List[str]): A list of recipient identifiers.
- `message` (str): The content of the notification.
- `notification_type` (str, optional): The type of notification ('email', 'sms', 'in-app'). Defaults to 'email'.
- `details` (Dict[str, Any], optional): Additional details.
- **Returns**: A dictionary mapping each recipient to a boolean indicating success or failure.

## Development Setup

No special setup is required beyond the standard project environment. Ensure `logging` is configured as needed.

## Testing

Unit tests for `NotificationService` should cover:
- Successful sending for each notification type.
- Handling of unsupported notification types.
- Error propagation from underlying sending mechanisms.
- Correct behavior for bulk notifications, including partial failures.

## Contributing

When adding new notification channels, ensure:
1. A new private method (`_send_new_type`) is implemented within `NotificationService`.
2. The `send_notification` method is updated to dispatch to the new type.
3. Relevant configurations are added if necessary.
4. Comprehensive tests are written for the new channel.