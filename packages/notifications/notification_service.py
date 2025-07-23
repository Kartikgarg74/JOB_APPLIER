import logging
from typing import List, Dict, Any
import aiohttp
import json
from sqlalchemy.orm import Session

from packages.errors.custom_exceptions import NotificationError
from packages.config.settings import settings
from packages.notifications.in_app_notifications.in_app_notification_manager import InAppNotificationManager

logger = logging.getLogger(__name__)

class NotificationService:
    """Manages sending various types of notifications (e.g., email, SMS, in-app)."""

    def __init__(self, db_session: Session = None):
        # [CONTEXT] Initializes the NotificationService with configurations for different notification channels.
        self.mailgun_api_key = settings.MAILGUN_API_KEY
        self.mailgun_domain = settings.MAILGUN_DOMAIN
        self.twilio_account_sid = settings.TWILIO_ACCOUNT_SID
        self.twilio_auth_token = settings.TWILIO_AUTH_TOKEN
        self.twilio_phone_number = settings.TWILIO_PHONE_NUMBER
        self.db_session = db_session
        self.in_app_notification_manager = InAppNotificationManager(db_session) if db_session else None

        if not self.mailgun_api_key or not self.mailgun_domain:
            logger.warning("Mailgun API key or domain not set. Email notifications will be simulated.")
        if not self.twilio_account_sid or not self.twilio_auth_token or not self.twilio_phone_number:
            logger.warning("Twilio credentials not set. SMS notifications will be simulated.")
        if not self.db_session:
            logger.warning("Database session not provided. In-app notifications will be simulated.")

        logger.info("NotificationService initialized.")

    async def _make_request(self, method: str, url: str, headers: Dict, data: Any = None, auth: aiohttp.BasicAuth = None) -> Dict:
        async with aiohttp.ClientSession(auth=auth) as session:
            try:
                async with session.request(method, url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                logger.error(f"HTTP request failed: {e}", exc_info=True)
                raise NotificationError(f"HTTP request failed: {e}")

    async def send_notification(self, recipient: str, message: str, notification_type: str = "email", details: Dict[str, Any] = None) -> bool:
        """Sends a notification to the specified recipient.

        Args:
            recipient (str): The recipient's identifier (e.g., email address, phone number).
            message (str): The content of the notification.
            notification_type (str): The type of notification to send (e.g., 'email', 'sms', 'in-app').
            details (Dict[str, Any]): Additional details for the notification (e.g., subject for email).

        Returns:
            bool: True if the notification was sent successfully, False otherwise.

        Raises:
            NotificationError: If there's an error sending the notification.
        """
        # [CONTEXT] Dispatches notifications based on their type.
        try:
            if notification_type == "email":
                return await self._send_email(recipient, message, details)
            elif notification_type == "sms":
                return await self._send_sms(recipient, message, details)
            elif notification_type == "in-app":
                return await self._send_in_app_notification(recipient, message, details)
            else:
                raise NotificationError(f"Unsupported notification type: {notification_type}")
        except Exception as e:
            logger.error(f"Failed to send {notification_type} notification to {recipient}: {e}", exc_info=True)
            raise NotificationError(f"Failed to send notification: {e}", details={"recipient": recipient, "type": notification_type})

    async def _send_email(self, recipient: str, message: str, details: Dict[str, Any]) -> bool:
        """Sends an email notification using Mailgun or simulates it if credentials are not set."""
        # [CONTEXT] Integrates with Mailgun for email sending.
        subject = details.get("subject", "Job Applier Notification")
        if self.mailgun_api_key and self.mailgun_domain:
            url = f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages"
            auth = aiohttp.BasicAuth("api", self.mailgun_api_key)
            data = aiohttp.FormData()
            data.add_field("from", f"Job Applier <mailgun@{self.mailgun_domain}>")
            data.add_field("to", recipient)
            data.add_field("subject", subject)
            data.add_field("text", message)

            try:
                await self._make_request("POST", url, headers={}, data=data, auth=auth)
                logger.info(f"Email sent to {recipient} with subject '{subject}' via Mailgun.")
                return True
            except NotificationError as e:
                logger.error(f"Failed to send email via Mailgun: {e}", exc_info=True)
                return False
        else:
            logger.info(f"Simulating email to {recipient} with subject '{subject}': {message}")
            return True

    async def _send_sms(self, recipient: str, message: str, details: Dict[str, Any]) -> bool:
        """Sends an SMS notification using Twilio or simulates it if credentials are not set."""
        # [CONTEXT] Integrates with Twilio for SMS sending.
        if self.twilio_account_sid and self.twilio_auth_token and self.twilio_phone_number:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
            auth = aiohttp.BasicAuth(self.twilio_account_sid, self.twilio_auth_token)
            data = {
                "To": recipient,
                "From": self.twilio_phone_number,
                "Body": message
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            try:
                await self._make_request("POST", url, headers=headers, data=data, auth=auth)
                logger.info(f"SMS sent to {recipient} via Twilio.")
                return True
            except NotificationError as e:
                logger.error(f"Failed to send SMS via Twilio: {e}", exc_info=True)
                return False
        else:
            logger.info(f"Simulating SMS to {recipient}: {message}")
            return True

    async def _send_in_app_notification(self, recipient: str, message: str, details: Dict[str, Any]) -> bool:
        """Sends an in-app notification by storing it in the database."""
        # [CONTEXT] Stores in-app notifications in the database using InAppNotificationManager.
        if self.in_app_notification_manager and self.db_session:
            try:
                user_id = int(recipient) # Assuming recipient is user_id for in-app notifications
                notification = self.in_app_notification_manager.create_notification(user_id, message, details)
                logger.info(f"In-app notification created for user {recipient}: {message}")
                return True
            except DatabaseError as e:
                logger.error(f"Failed to create in-app notification for user {recipient}: {e}", exc_info=True)
                raise NotificationError(f"Failed to send in-app notification: {e}", details=e.details)
        else:
            logger.info(f"Simulating in-app notification for user {recipient}: {message} (DB session not available)")
            return True

    async def send_bulk_notifications(self, recipients: List[str], message: str, notification_type: str = "email", details: Dict[str, Any] = None) -> Dict[str, bool]:
        """Sends a notification to multiple recipients."""
        # [CONTEXT] Iterates through a list of recipients to send bulk notifications.
        results = {}
        for recipient in recipients:
            try:
                success = await self.send_notification(recipient, message, notification_type, details)
                results[recipient] = success
            except NotificationError:
                results[recipient] = False
        return results