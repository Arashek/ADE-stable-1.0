from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
from datetime import datetime
from ..models.core_components import (
    UserProfile, Notification, DashboardMetrics, NavigationItem,
    UserSettings, SystemHealth, ResourceUsage, DeploymentStatus,
    UserManagement, SystemOverview
)
from ..auth.auth import get_current_user, require_admin
from ..services.core_service import CoreService

router = APIRouter(prefix="/api/core", tags=["core"])

# Initialize service
core_service = CoreService()

# Dashboard Routes
@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: Dict = Depends(require_admin)
):
    """Get dashboard metrics and system overview"""
    try:
        return await core_service.get_dashboard_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/overview", response_model=SystemOverview)
async def get_system_overview(
    current_user: Dict = Depends(require_admin)
):
    """Get system overview and status"""
    try:
        return await core_service.get_system_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Navigation Routes
@router.get("/navigation", response_model=List[NavigationItem])
async def get_navigation(
    current_user: Dict = Depends(get_current_user)
):
    """Get navigation items based on user permissions"""
    try:
        return await core_service.get_navigation(current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User Profile Routes
@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: Dict = Depends(get_current_user)
):
    """Get current user profile"""
    try:
        return await core_service.get_user_profile(current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile: UserProfile,
    current_user: Dict = Depends(get_current_user)
):
    """Update user profile"""
    try:
        return await core_service.update_user_profile(current_user["id"], profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User Settings Routes
@router.get("/settings", response_model=UserSettings)
async def get_user_settings(
    current_user: Dict = Depends(get_current_user)
):
    """Get user settings"""
    try:
        return await core_service.get_user_settings(current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/settings", response_model=UserSettings)
async def update_user_settings(
    settings: UserSettings,
    current_user: Dict = Depends(get_current_user)
):
    """Update user settings"""
    try:
        return await core_service.update_user_settings(current_user["id"], settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Notification Routes
@router.get("/notifications", response_model=List[Notification])
async def get_notifications(
    unread_only: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict = Depends(get_current_user)
):
    """Get user notifications"""
    try:
        return await core_service.get_notifications(
            current_user["id"],
            unread_only=unread_only,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Mark notification as read"""
    try:
        return await core_service.mark_notification_read(
            current_user["id"],
            notification_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Health Routes
@router.get("/health", response_model=SystemHealth)
async def get_system_health(
    current_user: Dict = Depends(require_admin)
):
    """Get system health status"""
    try:
        return await core_service.get_system_health()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Resource Usage Routes
@router.get("/resources", response_model=ResourceUsage)
async def get_resource_usage(
    current_user: Dict = Depends(require_admin)
):
    """Get system resource usage"""
    try:
        return await core_service.get_resource_usage()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Deployment Routes
@router.get("/deployments", response_model=List[DeploymentStatus])
async def get_deployments(
    status: Optional[str] = None,
    environment: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict = Depends(require_admin)
):
    """Get deployment status"""
    try:
        return await core_service.get_deployments(
            status=status,
            environment=environment,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User Management Routes
@router.get("/users", response_model=UserManagement)
async def get_user_management(
    current_user: Dict = Depends(require_admin)
):
    """Get user management overview"""
    try:
        return await core_service.get_user_management()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}", response_model=UserProfile)
async def get_user(
    user_id: str,
    current_user: Dict = Depends(require_admin)
):
    """Get user details"""
    try:
        return await core_service.get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: Dict,
    current_user: Dict = Depends(require_admin)
):
    """Update user details"""
    try:
        return await core_service.update_user(user_id, user_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Dict = Depends(require_admin)
):
    """Delete user"""
    try:
        return await core_service.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 