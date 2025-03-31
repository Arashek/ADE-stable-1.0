from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
from ..auth.auth import get_current_user, require_admin
from ..services.owner_panel_service import OwnerPanelService
from ..models.owner_panel import (
    DashboardMetrics, APIConfig, WebhookConfig, MarketplaceItem,
    MarketplaceOrder, SupportTicket, SystemDiagnostic, PerformanceMetric,
    ErrorLog, LandingPageContent, ThemeConfig, UIComponent
)
from ..auth.auth import get_current_admin_user
from ..config.logging_config import logger

router = APIRouter(prefix="/api/owner-panel", tags=["owner-panel"])

# Request/Response Models
class SystemMetrics(BaseModel):
    active_users: int
    total_users: int
    system_load: float
    memory_usage: float
    storage_usage: float
    api_requests: int
    error_rate: float

class UserStats(BaseModel):
    total_users: int
    active_users: int
    new_users: int
    suspended_users: int
    user_growth: float

class SecurityConfig(BaseModel):
    auth_providers: List[str]
    mfa_enabled: bool
    session_timeout: int
    password_policy: Dict
    ip_whitelist: List[str]

class FrontendConfig(BaseModel):
    theme: Dict
    navigation: List[Dict]
    components: List[Dict]
    content: Dict

# Initialize service
owner_service = OwnerPanelService()

# Dashboard Routes
@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(current_user: dict = Depends(get_current_admin_user)):
    """Get system overview metrics"""
    try:
        return await owner_service.get_dashboard_metrics()
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard metrics")

@router.get("/dashboard/user-stats", response_model=UserStats)
async def get_user_statistics(
    current_user: Dict = Depends(require_admin)
):
    """Get user-related statistics"""
    try:
        return await owner_service.get_user_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Security Routes
@router.get("/security/config", response_model=SecurityConfig)
async def get_security_config(
    current_user: Dict = Depends(require_admin)
):
    """Get current security configuration"""
    try:
        return await owner_service.get_security_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/security/config", response_model=SecurityConfig)
async def update_security_config(
    config: SecurityConfig,
    current_user: Dict = Depends(require_admin)
):
    """Update security configuration"""
    try:
        return await owner_service.update_security_config(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Frontend Management Routes
@router.get("/frontend/config", response_model=FrontendConfig)
async def get_frontend_config(
    current_user: Dict = Depends(require_admin)
):
    """Get frontend configuration"""
    try:
        return await owner_service.get_frontend_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/frontend/config", response_model=FrontendConfig)
async def update_frontend_config(
    config: FrontendConfig,
    current_user: Dict = Depends(require_admin)
):
    """Update frontend configuration"""
    try:
        return await owner_service.update_frontend_config(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Technical Support Routes
@router.get("/support/tickets")
async def get_support_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict = Depends(require_admin)
):
    """Get support tickets with filtering and pagination"""
    try:
        return await owner_service.get_support_tickets(
            status=status,
            priority=priority,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/support/diagnostics")
async def get_system_diagnostics(
    current_user: Dict = Depends(require_admin)
):
    """Get system diagnostics and health information"""
    try:
        return await owner_service.get_system_diagnostics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Audit Logs Routes
@router.get("/audit/logs")
async def get_audit_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    action_type: Optional[str] = None,
    user_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict = Depends(require_admin)
):
    """Get audit logs with filtering and pagination"""
    try:
        return await owner_service.get_audit_logs(
            start_date=start_date,
            end_date=end_date,
            action_type=action_type,
            user_id=user_id,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Maintenance Routes
@router.post("/maintenance/backup")
async def create_system_backup(
    current_user: Dict = Depends(require_admin)
):
    """Create a system backup"""
    try:
        return await owner_service.create_system_backup()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/maintenance/restore")
async def restore_system_backup(
    backup_id: str,
    current_user: Dict = Depends(require_admin)
):
    """Restore system from backup"""
    try:
        return await owner_service.restore_system_backup(backup_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API Management Routes
@router.get("/api/keys")
async def get_api_keys(
    current_user: Dict = Depends(require_admin)
):
    """Get all API keys"""
    try:
        return await owner_service.get_api_keys()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/keys")
async def create_api_key(
    description: str,
    permissions: List[str],
    current_user: Dict = Depends(require_admin)
):
    """Create a new API key"""
    try:
        return await owner_service.create_api_key(description, permissions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: Dict = Depends(require_admin)
):
    """Revoke an API key"""
    try:
        return await owner_service.revoke_api_key(key_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/config", response_model=APIConfig)
async def create_api_config(
    config: APIConfig,
    current_user: dict = Depends(get_current_admin_user)
):
    """Create new API configuration"""
    try:
        return await owner_service.manage_api_config(config)
    except Exception as e:
        logger.error(f"Error creating API config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create API configuration")

@router.put("/api/config/{config_id}", response_model=APIConfig)
async def update_api_config(
    config_id: str,
    config: APIConfig,
    current_user: dict = Depends(get_current_admin_user)
):
    """Update existing API configuration"""
    try:
        config.id = config_id
        return await owner_service.manage_api_config(config)
    except Exception as e:
        logger.error(f"Error updating API config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update API configuration")

# Webhook Configuration Routes
@router.post("/webhooks", response_model=WebhookConfig)
async def create_webhook(
    webhook: WebhookConfig,
    current_user: dict = Depends(get_current_admin_user)
):
    """Create new webhook configuration"""
    try:
        return await owner_panel_service.configure_webhook(webhook)
    except Exception as e:
        logger.error(f"Error creating webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create webhook configuration")

@router.put("/webhooks/{webhook_id}", response_model=WebhookConfig)
async def update_webhook(
    webhook_id: str,
    webhook: WebhookConfig,
    current_user: dict = Depends(get_current_admin_user)
):
    """Update existing webhook configuration"""
    try:
        webhook.id = webhook_id
        return await owner_panel_service.configure_webhook(webhook)
    except Exception as e:
        logger.error(f"Error updating webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update webhook configuration")

# Marketplace Management Routes
@router.post("/marketplace/items", response_model=MarketplaceItem)
async def create_marketplace_item(
    item: MarketplaceItem,
    current_user: dict = Depends(get_current_admin_user)
):
    """Create new marketplace item"""
    try:
        return await owner_panel_service.manage_marketplace_item(item)
    except Exception as e:
        logger.error(f"Error creating marketplace item: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create marketplace item")

@router.put("/marketplace/items/{item_id}", response_model=MarketplaceItem)
async def update_marketplace_item(
    item_id: str,
    item: MarketplaceItem,
    current_user: dict = Depends(get_current_admin_user)
):
    """Update existing marketplace item"""
    try:
        item.id = item_id
        return await owner_panel_service.manage_marketplace_item(item)
    except Exception as e:
        logger.error(f"Error updating marketplace item: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update marketplace item")

# Support Ticket Management Routes
@router.post("/support/tickets", response_model=SupportTicket)
async def create_support_ticket(
    ticket: SupportTicket,
    current_user: dict = Depends(get_current_admin_user)
):
    """Create new support ticket"""
    try:
        return await owner_panel_service.handle_support_ticket(ticket)
    except Exception as e:
        logger.error(f"Error creating support ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create support ticket")

@router.put("/support/tickets/{ticket_id}", response_model=SupportTicket)
async def update_support_ticket(
    ticket_id: str,
    ticket: SupportTicket,
    current_user: dict = Depends(get_current_admin_user)
):
    """Update existing support ticket"""
    try:
        ticket.id = ticket_id
        return await owner_panel_service.handle_support_ticket(ticket)
    except Exception as e:
        logger.error(f"Error updating support ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update support ticket")

# System Diagnostics Routes
@router.get("/diagnostics", response_model=SystemDiagnostic)
async def get_system_diagnostics(
    current_user: dict = Depends(get_current_admin_user)
):
    """Get system diagnostics information"""
    try:
        return await owner_panel_service.get_system_diagnostics()
    except Exception as e:
        logger.error(f"Error getting system diagnostics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get system diagnostics")

# Performance Monitoring Routes
@router.get("/performance/metrics", response_model=List[PerformanceMetric])
async def get_performance_metrics(
    current_user: dict = Depends(get_current_admin_user)
):
    """Get performance metrics for all endpoints"""
    try:
        return await owner_panel_service.get_performance_metrics()
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")

# Error Logging Routes
@router.get("/logs/errors", response_model=List[ErrorLog])
async def get_error_logs(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    level: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get error logs with optional filtering"""
    try:
        return await owner_panel_service.get_error_logs(start_time, end_time, level)
    except Exception as e:
        logger.error(f"Error getting error logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get error logs")

# Landing Page Management Routes
@router.post("/landing-page/content", response_model=LandingPageContent)
async def create_landing_page_content(
    content: LandingPageContent,
    current_user: dict = Depends(get_current_admin_user)
):
    """Create new landing page content"""
    try:
        return await owner_panel_service.manage_landing_page_content(content)
    except Exception as e:
        logger.error(f"Error creating landing page content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create landing page content")

@router.put("/landing-page/content/{content_id}", response_model=LandingPageContent)
async def update_landing_page_content(
    content_id: str,
    content: LandingPageContent,
    current_user: dict = Depends(get_current_admin_user)
):
    """Update existing landing page content"""
    try:
        content.id = content_id
        return await owner_panel_service.manage_landing_page_content(content)
    except Exception as e:
        logger.error(f"Error updating landing page content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update landing page content")

# Theme Configuration Routes
@router.post("/themes", response_model=ThemeConfig)
async def create_theme_config(
    theme: ThemeConfig,
    current_user: dict = Depends(get_current_admin_user)
):
    """Create new theme configuration"""
    try:
        return await owner_panel_service.manage_theme_config(theme)
    except Exception as e:
        logger.error(f"Error creating theme configuration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create theme configuration")

@router.put("/themes/{theme_id}", response_model=ThemeConfig)
async def update_theme_config(
    theme_id: str,
    theme: ThemeConfig,
    current_user: dict = Depends(get_current_admin_user)
):
    """Update existing theme configuration"""
    try:
        theme.id = theme_id
        return await owner_panel_service.manage_theme_config(theme)
    except Exception as e:
        logger.error(f"Error updating theme configuration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update theme configuration")

# UI Component Library Routes
@router.post("/ui/components", response_model=UIComponent)
async def create_ui_component(
    component: UIComponent,
    current_user: dict = Depends(get_current_admin_user)
):
    """Create new UI component"""
    try:
        return await owner_panel_service.manage_ui_component(component)
    except Exception as e:
        logger.error(f"Error creating UI component: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create UI component")

@router.put("/ui/components/{component_id}", response_model=UIComponent)
async def update_ui_component(
    component_id: str,
    component: UIComponent,
    current_user: dict = Depends(get_current_admin_user)
):
    """Update existing UI component"""
    try:
        component.id = component_id
        return await owner_panel_service.manage_ui_component(component)
    except Exception as e:
        logger.error(f"Error updating UI component: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update UI component") 