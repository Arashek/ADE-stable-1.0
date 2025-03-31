from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.session import get_db
from ..services.notification_service import NotificationService
from ..database.operations.notification import NotificationOperations
from ..models.notification import NotificationType, NotificationPriority, NotificationStatus
from ..auth.auth import get_current_user
from ..config.logging_config import logger

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.post("")
async def create_notification(
    notification_data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new notification"""
    try:
        notification_service = NotificationService(NotificationOperations(db))
        notification_data["user_id"] = current_user["id"]
        return await notification_service.create_notification(notification_data)
    except Exception as e:
        logger.error(f"Error in create_notification route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{notification_id}")
async def get_notification(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get notification by ID"""
    try:
        notification_service = NotificationService(NotificationOperations(db))
        notification = await notification_service.get_notification(notification_id)
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        if notification["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to access this notification")
            
        return notification
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_notification route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
async def get_user_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    include_expired: bool = False,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's notifications with pagination"""
    try:
        notification_service = NotificationService(NotificationOperations(db))
        return await notification_service.get_user_notifications(
            current_user["id"],
            skip,
            limit,
            include_expired
        )
    except Exception as e:
        logger.error(f"Error in get_user_notifications route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read"""
    try:
        notification_service = NotificationService(NotificationOperations(db))
        notification = await notification_service.get_notification(notification_id)
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        if notification["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to modify this notification")
            
        return await notification_service.mark_notification_read(notification_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in mark_notification_read route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/read-all")
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all user's notifications as read"""
    try:
        notification_service = NotificationService(NotificationOperations(db))
        return await notification_service.mark_all_notifications_read(current_user["id"])
    except Exception as e:
        logger.error(f"Error in mark_all_notifications_read route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{notification_id}/archive")
async def archive_notification(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Archive notification"""
    try:
        notification_service = NotificationService(NotificationOperations(db))
        notification = await notification_service.get_notification(notification_id)
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        if notification["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to modify this notification")
            
        return await notification_service.archive_notification(notification_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in archive_notification route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete notification"""
    try:
        notification_service = NotificationService(NotificationOperations(db))
        notification = await notification_service.get_notification(notification_id)
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        if notification["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this notification")
            
        return await notification_service.delete_notification(notification_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_notification route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/unread/count")
async def get_unread_count(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications"""
    try:
        notification_service = NotificationService(NotificationOperations(db))
        return await notification_service.get_unread_count(current_user["id"])
    except Exception as e:
        logger.error(f"Error in get_unread_count route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preferences")
async def get_notification_preferences(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's notification preferences"""
    try:
        notification_service = NotificationService(NotificationOperations(db))
        return await notification_service.get_notification_preferences(current_user["id"])
    except Exception as e:
        logger.error(f"Error in get_notification_preferences route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/preferences")
async def update_notification_preferences(
    preferences: List[dict],
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's notification preferences"""
    try:
        notification_service = NotificationService(NotificationOperations(db))
        return await notification_service.update_notification_preferences(
            current_user["id"],
            preferences
        )
    except Exception as e:
        logger.error(f"Error in update_notification_preferences route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 