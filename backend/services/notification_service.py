from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import json
from fastapi import HTTPException
from ..models.notification import Notification, NotificationStatus, NotificationType, NotificationPriority
from ..database.owner_panel_db import OwnerPanelDB
from ..config.logging_config import logger
from ..config.cache_config import cache
from ..utils.security import encrypt_sensitive_data, decrypt_sensitive_data
from ..utils.rate_limit import rate_limit
from ..utils.validation import validate_notification_data
from ..database.operations.notification import NotificationOperations
from ..config.settings import settings

class NotificationService:
    """Service for handling notifications"""
    
    def __init__(self, db_operations: NotificationOperations):
        self.db_operations = db_operations
        self.db = OwnerPanelDB()
        self.logger = logger
        self.rate_limit = rate_limit
        self.max_notifications_per_user = 1000  # Maximum notifications per user
        self.notification_retention_days = 30   # Days to keep notifications

    @rate_limit(requests_per_minute=100)
    async def create_notification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new notification"""
        try:
            # Validate notification data
            if not validate_notification_data(data):
                raise HTTPException(status_code=400, detail="Invalid notification data")
                
            # Check user notification limit
            user_notifications = await self.db_operations.get_user_notifications(
                data["user_id"],
                limit=settings.MAX_NOTIFICATIONS_PER_USER
            )
            if len(user_notifications) >= settings.MAX_NOTIFICATIONS_PER_USER:
                raise HTTPException(
                    status_code=429,
                    detail="User has reached maximum notification limit"
                )
                
            # Encrypt sensitive data in metadata
            if data.get("metadata"):
                data["metadata"] = encrypt_sensitive_data(str(data["metadata"]))
                
            # Create notification
            notification = await self.db_operations.create_notification(data)
            
            # Trigger notification event
            await self._trigger_notification_event(notification)
            
            return notification.to_dict()
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            raise
            
    async def get_notification(self, notification_id: int) -> Optional[Dict[str, Any]]:
        """Get notification by ID"""
        try:
            notification = await self.db_operations.get_notification(notification_id)
            if not notification:
                return None
                
            # Decrypt sensitive data in metadata
            notification_dict = notification.to_dict()
            if notification_dict.get("metadata"):
                notification_dict["metadata"] = decrypt_sensitive_data(
                    notification_dict["metadata"]
                )
                
            return notification_dict
        except Exception as e:
            logger.error(f"Error getting notification: {str(e)}")
            raise
            
    async def get_user_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_expired: bool = False
    ) -> List[Dict[str, Any]]:
        """Get user's notifications with pagination"""
        try:
            notifications = await self.db_operations.get_user_notifications(
                user_id,
                skip,
                limit,
                include_expired
            )
            
            # Decrypt sensitive data in metadata
            result = []
            for notification in notifications:
                notification_dict = notification.to_dict()
                if notification_dict.get("metadata"):
                    notification_dict["metadata"] = decrypt_sensitive_data(
                        notification_dict["metadata"]
                    )
                result.append(notification_dict)
                
            return result
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            raise
            
    async def mark_notification_read(self, notification_id: int) -> Optional[Dict[str, Any]]:
        """Mark notification as read"""
        try:
            notification = await self.db_operations.mark_notification_read(notification_id)
            if not notification:
                return None
                
            # Decrypt sensitive data in metadata
            notification_dict = notification.to_dict()
            if notification_dict.get("metadata"):
                notification_dict["metadata"] = decrypt_sensitive_data(
                    notification_dict["metadata"]
                )
                
            return notification_dict
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            raise
            
    async def mark_all_notifications_read(self, user_id: int) -> int:
        """Mark all user's notifications as read"""
        try:
            return await self.db_operations.mark_all_notifications_read(user_id)
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            raise
            
    async def archive_notification(self, notification_id: int) -> Optional[Dict[str, Any]]:
        """Archive notification"""
        try:
            notification = await self.db_operations.archive_notification(notification_id)
            if not notification:
                return None
                
            # Decrypt sensitive data in metadata
            notification_dict = notification.to_dict()
            if notification_dict.get("metadata"):
                notification_dict["metadata"] = decrypt_sensitive_data(
                    notification_dict["metadata"]
                )
                
            return notification_dict
        except Exception as e:
            logger.error(f"Error archiving notification: {str(e)}")
            raise
            
    async def delete_notification(self, notification_id: int) -> bool:
        """Delete notification"""
        try:
            return await self.db_operations.delete_notification(notification_id)
        except Exception as e:
            logger.error(f"Error deleting notification: {str(e)}")
            raise
            
    async def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        try:
            return await self.db_operations.get_unread_count(user_id)
        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            raise
            
    async def cleanup_expired_notifications(self) -> int:
        """Delete expired notifications"""
        try:
            return await self.db_operations.cleanup_expired_notifications()
        except Exception as e:
            logger.error(f"Error cleaning up expired notifications: {str(e)}")
            raise
            
    async def get_notification_preferences(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Get user's notification preferences"""
        try:
            preferences = await self.db_operations.get_notification_preferences(user_id)
            return [pref.to_dict() for pref in preferences]
        except Exception as e:
            logger.error(f"Error getting notification preferences: {str(e)}")
            raise
            
    async def update_notification_preferences(
        self,
        user_id: int,
        preferences: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Update user's notification preferences"""
        try:
            updated_preferences = await self.db_operations.update_notification_preferences(
                user_id,
                preferences
            )
            return [pref.to_dict() for pref in updated_preferences]
        except Exception as e:
            logger.error(f"Error updating notification preferences: {str(e)}")
            raise
            
    async def _trigger_notification_event(self, notification: Any) -> None:
        """Trigger notification event for real-time updates"""
        try:
            # TODO: Implement WebSocket event emission
            # This will be implemented when we add WebSocket support
            pass
        except Exception as e:
            logger.error(f"Error triggering notification event: {str(e)}")
            raise

    @rate_limit(max_requests=100, window_seconds=60)
    async def create_notification_enhanced(self, notification: Notification) -> Notification:
        """Create a new notification with enhanced security and validation"""
        try:
            # Validate notification data
            await validate_notification_data(notification)
            
            # Check user notification limit
            user_notification_count = await self.db.get_user_notification_count(notification.user_id)
            if user_notification_count >= self.max_notifications_per_user:
                # Archive oldest notifications
                await self._archive_old_notifications(notification.user_id)
                user_notification_count = await self.db.get_user_notification_count(notification.user_id)
                if user_notification_count >= self.max_notifications_per_user:
                    raise HTTPException(
                        status_code=429,
                        detail="User has reached maximum notification limit"
                    )

            # Generate notification ID
            notification.id = str(uuid.uuid4())
            notification.created_at = datetime.utcnow()
            
            # Encrypt sensitive data in metadata if present
            if notification.metadata and "sensitive_data" in notification.metadata:
                notification.metadata["sensitive_data"] = encrypt_sensitive_data(
                    json.dumps(notification.metadata["sensitive_data"])
                )
            
            # Store notification
            await self.db.create_notification(notification.dict())
            
            # Invalidate user's notification cache
            await cache.delete(f"user_notifications:{notification.user_id}")
            
            # Trigger notification event
            await self._trigger_notification_event(notification)
            
            return notification
        except Exception as e:
            self.logger.error(f"Error creating notification: {str(e)}")
            raise

    async def get_user_notifications_enhanced(
        self,
        user_id: str,
        status: Optional[NotificationStatus] = None,
        page: int = 1,
        limit: int = 20,
        include_expired: bool = False
    ) -> List[Notification]:
        """Get notifications for a user with enhanced filtering and security"""
        try:
            # Try to get from cache first
            cache_key = f"user_notifications:{user_id}:{status}:{page}:{limit}:{include_expired}"
            cached_notifications = await cache.get(cache_key)
            
            if cached_notifications:
                return [Notification.parse_raw(n) for n in cached_notifications]

            # Get from database
            notifications = await self.db.get_user_notifications(
                user_id=user_id,
                status=status,
                page=page,
                limit=limit,
                include_expired=include_expired
            )

            # Decrypt sensitive data if present
            for notification in notifications:
                if notification.metadata and "sensitive_data" in notification.metadata:
                    try:
                        decrypted_data = decrypt_sensitive_data(
                            notification.metadata["sensitive_data"]
                        )
                        notification.metadata["sensitive_data"] = json.loads(decrypted_data)
                    except Exception as e:
                        self.logger.error(f"Error decrypting notification data: {str(e)}")
                        notification.metadata["sensitive_data"] = None

            # Cache results
            await cache.set(cache_key, [n.json() for n in notifications], 300)
            
            return notifications
        except Exception as e:
            self.logger.error(f"Error getting user notifications: {str(e)}")
            raise

    async def mark_notification_read_enhanced(self, notification_id: str, user_id: str) -> Notification:
        """Mark a notification as read with enhanced security"""
        try:
            notification = await self.db.get_notification(notification_id)
            
            if not notification or notification.user_id != user_id:
                raise ValueError("Notification not found or unauthorized")

            # Check if notification is expired
            if notification.expires_at and notification.expires_at < datetime.utcnow():
                raise HTTPException(
                    status_code=400,
                    detail="Cannot mark expired notification as read"
                )

            notification.status = NotificationStatus.READ
            notification.read_at = datetime.utcnow()
            
            await self.db.update_notification(notification.dict())
            
            # Invalidate cache
            await cache.delete(f"user_notifications:{user_id}")
            
            return notification
        except Exception as e:
            self.logger.error(f"Error marking notification as read: {str(e)}")
            raise

    async def mark_all_notifications_read_enhanced(self, user_id: str) -> bool:
        """Mark all notifications as read with enhanced security"""
        try:
            # Get all unread notifications
            notifications = await self.db.get_user_notifications(
                user_id=user_id,
                status=NotificationStatus.UNREAD
            )

            # Update each notification
            for notification in notifications:
                if not notification.expires_at or notification.expires_at > datetime.utcnow():
                    notification.status = NotificationStatus.READ
                    notification.read_at = datetime.utcnow()
                    await self.db.update_notification(notification.dict())
            
            # Invalidate cache
            await cache.delete(f"user_notifications:{user_id}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error marking all notifications as read: {str(e)}")
            raise

    async def archive_notification_enhanced(self, notification_id: str, user_id: str) -> Notification:
        """Archive a notification with enhanced security"""
        try:
            notification = await self.db.get_notification(notification_id)
            
            if not notification or notification.user_id != user_id:
                raise ValueError("Notification not found or unauthorized")

            notification.status = NotificationStatus.ARCHIVED
            
            await self.db.update_notification(notification.dict())
            
            # Invalidate cache
            await cache.delete(f"user_notifications:{user_id}")
            
            return notification
        except Exception as e:
            self.logger.error(f"Error archiving notification: {str(e)}")
            raise

    async def get_unread_count_enhanced(self, user_id: str) -> int:
        """Get count of unread notifications with enhanced security"""
        try:
            # Try to get from cache first
            cache_key = f"unread_count:{user_id}"
            cached_count = await cache.get(cache_key)
            
            if cached_count is not None:
                return int(cached_count)

            count = await self.db.get_unread_notification_count(user_id)
            
            # Cache for 5 minutes
            await cache.set(cache_key, str(count), 300)
            
            return count
        except Exception as e:
            self.logger.error(f"Error getting unread notification count: {str(e)}")
            raise

    async def delete_notification_enhanced(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification with enhanced security"""
        try:
            notification = await self.db.get_notification(notification_id)
            
            if not notification or notification.user_id != user_id:
                raise ValueError("Notification not found or unauthorized")

            await self.db.delete_notification(notification_id)
            
            # Invalidate cache
            await cache.delete(f"user_notifications:{user_id}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error deleting notification: {str(e)}")
            raise

    async def bulk_create_notifications(
        self,
        notifications: List[Notification],
        batch_size: int = 100
    ) -> List[Notification]:
        """Create multiple notifications efficiently"""
        try:
            created_notifications = []
            for i in range(0, len(notifications), batch_size):
                batch = notifications[i:i + batch_size]
                for notification in batch:
                    notification.id = str(uuid.uuid4())
                    notification.created_at = datetime.utcnow()
                
                await self.db.bulk_create_notifications([n.dict() for n in batch])
                created_notifications.extend(batch)
                
                # Invalidate cache for affected users
                user_ids = {n.user_id for n in batch}
                for user_id in user_ids:
                    await cache.delete(f"user_notifications:{user_id}")
            
            return created_notifications
        except Exception as e:
            self.logger.error(f"Error bulk creating notifications: {str(e)}")
            raise

    async def _archive_old_notifications(self, user_id: str) -> None:
        """Archive old notifications to maintain user limits"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.notification_retention_days)
            await self.db.archive_old_notifications(user_id, cutoff_date)
        except Exception as e:
            self.logger.error(f"Error archiving old notifications: {str(e)}")

    async def _trigger_notification_event(self, notification: Notification) -> None:
        """Trigger notification event for real-time updates"""
        try:
            # Implement real-time notification delivery
            # This could be WebSocket, push notification, or email
            pass
        except Exception as e:
            self.logger.error(f"Error triggering notification event: {str(e)}") 