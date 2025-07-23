import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from packages.database.models import InAppNotification # Assuming this model exists or will be created
from packages.errors.custom_exceptions import DatabaseError

logger = logging.getLogger(__name__)

class InAppNotificationManager:
    """Manages the creation, storage, and retrieval of in-app notifications."""

    def __init__(self, db: Session):
        self.db = db
        logger.info("InAppNotificationManager initialized.")

    def create_notification(self, user_id: int, message: str, details: Dict[str, Any] = None) -> InAppNotification:
        """Creates and stores a new in-app notification in the database."""
        try:
            notification = InAppNotification(
                user_id=user_id,
                message=message,
                details=details if details is not None else {}
            )
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            logger.info(f"Created in-app notification for user {user_id}: {message}")
            return notification
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to create in-app notification for user {user_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to create in-app notification for user {user_id}: {e}", details={"user_id": user_id, "message": message, "details": details})

    def get_notifications_for_user(self, user_id: int, limit: int = 10, offset: int = 0) -> List[InAppNotification]:
        """Retrieves a list of in-app notifications for a given user."""
        try:
            notifications = (
                self.db.query(InAppNotification)
                .filter(InAppNotification.user_id == user_id)
                .order_by(InAppNotification.created_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )
            logger.info(f"Retrieved {len(notifications)} in-app notifications for user {user_id}.")
            return notifications
        except SQLAlchemyError as e:
            logger.error(f"Failed to retrieve in-app notifications for user {user_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to retrieve in-app notifications for user {user_id}: {e}", details={"user_id": user_id, "limit": limit, "offset": offset})

    def mark_as_read(self, notification_id: int) -> bool:
        """Marks an in-app notification as read."""
        try:
            notification = self.db.query(InAppNotification).filter(InAppNotification.id == notification_id).first()
            if notification:
                notification.is_read = True
                self.db.commit()
                self.db.refresh(notification)
                logger.info(f"Marked in-app notification {notification_id} as read.")
                return True
            logger.warning(f"In-app notification {notification_id} not found.")
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to mark in-app notification {notification_id} as read: {e}", exc_info=True)
            raise DatabaseError(f"Failed to mark in-app notification {notification_id} as read: {e}", details={"notification_id": notification_id})

    def delete_notification(self, notification_id: int) -> bool:
        """Deletes an in-app notification."""
        try:
            notification = self.db.query(InAppNotification).filter(InAppNotification.id == notification_id).first()
            if notification:
                self.db.delete(notification)
                self.db.commit()
                logger.info(f"Deleted in-app notification {notification_id}.")
                return True
            logger.warning(f"In-app notification {notification_id} not found for deletion.")
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to delete in-app notification {notification_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to delete in-app notification {notification_id}: {e}", details={"notification_id": notification_id})