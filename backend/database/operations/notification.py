from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.notification import Notification, NotificationPreference, NotificationStatus
from config.logging_config import logger

class NotificationOperations:
    """Database operations for notifications"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_notification(self, data: Dict[str, Any]) -> Notification:
        """Create a new notification"""
        try:
            notification = Notification.from_dict(data)
            self.session.add(notification)
            await self.session.commit()
            await self.session.refresh(notification)
            return notification
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating notification: {str(e)}")
            raise
            
    async def get_notification(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID"""
        try:
            query = select(Notification).where(Notification.id == notification_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting notification: {str(e)}")
            raise
            
    async def get_user_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_expired: bool = False
    ) -> List[Notification]:
        """Get user's notifications with pagination"""
        try:
            query = select(Notification).where(Notification.user_id == user_id)
            
            if not include_expired:
                query = query.where(
                    or_(
                        Notification.expires_at.is_(None),
                        Notification.expires_at > datetime.utcnow()
                    )
                )
                
            query = query.order_by(Notification.created_at.desc())
            query = query.offset(skip).limit(limit)
            
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            raise
            
    async def mark_notification_read(self, notification_id: int) -> Optional[Notification]:
        """Mark notification as read"""
        try:
            query = (
                update(Notification)
                .where(Notification.id == notification_id)
                .values(
                    status=NotificationStatus.READ,
                    read_at=datetime.utcnow()
                )
                .returning(Notification)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error marking notification as read: {str(e)}")
            raise
            
    async def mark_all_notifications_read(self, user_id: int) -> int:
        """Mark all user's notifications as read"""
        try:
            query = (
                update(Notification)
                .where(
                    and_(
                        Notification.user_id == user_id,
                        Notification.status == NotificationStatus.UNREAD
                    )
                )
                .values(
                    status=NotificationStatus.READ,
                    read_at=datetime.utcnow()
                )
            )
            result = await self.session.execute(query)
            await self.session.commit()
            return result.rowcount
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error marking all notifications as read: {str(e)}")
            raise
            
    async def archive_notification(self, notification_id: int) -> Optional[Notification]:
        """Archive notification"""
        try:
            query = (
                update(Notification)
                .where(Notification.id == notification_id)
                .values(status=NotificationStatus.ARCHIVED)
                .returning(Notification)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error archiving notification: {str(e)}")
            raise
            
    async def delete_notification(self, notification_id: int) -> bool:
        """Delete notification"""
        try:
            query = (
                delete(Notification)
                .where(Notification.id == notification_id)
                .returning(Notification.id)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            return bool(result.scalar_one_or_none())
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting notification: {str(e)}")
            raise
            
    async def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        try:
            query = select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.status == NotificationStatus.UNREAD
                )
            )
            result = await self.session.execute(query)
            return len(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            raise
            
    async def cleanup_expired_notifications(self) -> int:
        """Delete expired notifications"""
        try:
            query = (
                delete(Notification)
                .where(
                    and_(
                        Notification.expires_at.isnot(None),
                        Notification.expires_at <= datetime.utcnow()
                    )
                )
                .returning(Notification.id)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            return len(result.scalars().all())
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error cleaning up expired notifications: {str(e)}")
            raise
            
    async def get_notification_preferences(
        self,
        user_id: int
    ) -> List[NotificationPreference]:
        """Get user's notification preferences"""
        try:
            query = select(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            )
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting notification preferences: {str(e)}")
            raise
            
    async def update_notification_preferences(
        self,
        user_id: int,
        preferences: List[Dict[str, Any]]
    ) -> List[NotificationPreference]:
        """Update user's notification preferences"""
        try:
            # Delete existing preferences
            query = delete(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            )
            await self.session.execute(query)
            
            # Create new preferences
            new_preferences = []
            for pref_data in preferences:
                pref_data["user_id"] = user_id
                preference = NotificationPreference.from_dict(pref_data)
                new_preferences.append(preference)
                
            self.session.add_all(new_preferences)
            await self.session.commit()
            
            return new_preferences
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating notification preferences: {str(e)}")
            raise 