from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
from datetime import datetime
from ..models.management_components import (
    Permission, Role, AuthSettings, AuditLog,
    Component, Model, ServiceConfig, InfrastructureSettings,
    ExternalService, APIConfig, WebhookConfig,
    MarketplaceItem, MarketplaceOrder
)
from ..auth.auth import get_current_user, require_admin, require_system
from ..services.management_service import ManagementService

router = APIRouter(prefix="/api/management", tags=["management"])

# Initialize service
management_service = ManagementService()

# Security & Access Control Routes
@router.get("/security/permissions", response_model=List[Permission])
async def get_permissions(
    current_user: Dict = Depends(require_admin)
):
    """Get all permissions"""
    try:
        return await management_service.get_permissions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/security/permissions", response_model=Permission)
async def create_permission(
    permission: Permission,
    current_user: Dict = Depends(require_system)
):
    """Create a new permission"""
    try:
        return await management_service.create_permission(permission)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/security/roles", response_model=List[Role])
async def get_roles(
    current_user: Dict = Depends(require_admin)
):
    """Get all roles"""
    try:
        return await management_service.get_roles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/security/roles", response_model=Role)
async def create_role(
    role: Role,
    current_user: Dict = Depends(require_system)
):
    """Create a new role"""
    try:
        return await management_service.create_role(role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/security/auth-settings", response_model=List[AuthSettings])
async def get_auth_settings(
    current_user: Dict = Depends(require_admin)
):
    """Get authentication settings"""
    try:
        return await management_service.get_auth_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/security/auth-settings/{setting_id}", response_model=AuthSettings)
async def update_auth_setting(
    setting_id: str,
    setting: AuthSettings,
    current_user: Dict = Depends(require_system)
):
    """Update authentication setting"""
    try:
        return await management_service.update_auth_setting(setting_id, setting)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/security/audit-logs", response_model=List[AuditLog])
async def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict = Depends(require_admin)
):
    """Get audit logs"""
    try:
        return await management_service.get_audit_logs(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Architecture Management Routes
@router.get("/architecture/components", response_model=List[Component])
async def get_components(
    type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict = Depends(require_admin)
):
    """Get system components"""
    try:
        return await management_service.get_components(type=type, status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/architecture/components", response_model=Component)
async def create_component(
    component: Component,
    current_user: Dict = Depends(require_system)
):
    """Create a new component"""
    try:
        return await management_service.create_component(component)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/architecture/models", response_model=List[Model])
async def get_models(
    current_user: Dict = Depends(require_admin)
):
    """Get data models"""
    try:
        return await management_service.get_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/architecture/models", response_model=Model)
async def create_model(
    model: Model,
    current_user: Dict = Depends(require_system)
):
    """Create a new model"""
    try:
        return await management_service.create_model(model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/architecture/service-configs", response_model=List[ServiceConfig])
async def get_service_configs(
    service_id: Optional[str] = None,
    environment: Optional[str] = None,
    current_user: Dict = Depends(require_admin)
):
    """Get service configurations"""
    try:
        return await management_service.get_service_configs(
            service_id=service_id,
            environment=environment
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/architecture/service-configs/{config_id}", response_model=ServiceConfig)
async def update_service_config(
    config_id: str,
    config: ServiceConfig,
    current_user: Dict = Depends(require_system)
):
    """Update service configuration"""
    try:
        return await management_service.update_service_config(config_id, config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/architecture/infrastructure", response_model=List[InfrastructureSettings])
async def get_infrastructure_settings(
    current_user: Dict = Depends(require_admin)
):
    """Get infrastructure settings"""
    try:
        return await management_service.get_infrastructure_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/architecture/infrastructure/{setting_id}", response_model=InfrastructureSettings)
async def update_infrastructure_setting(
    setting_id: str,
    setting: InfrastructureSettings,
    current_user: Dict = Depends(require_system)
):
    """Update infrastructure setting"""
    try:
        return await management_service.update_infrastructure_setting(setting_id, setting)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Integration Management Routes
@router.get("/integration/services", response_model=List[ExternalService])
async def get_external_services(
    type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict = Depends(require_admin)
):
    """Get external services"""
    try:
        return await management_service.get_external_services(type=type, status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integration/services", response_model=ExternalService)
async def create_external_service(
    service: ExternalService,
    current_user: Dict = Depends(require_system)
):
    """Create a new external service"""
    try:
        return await management_service.create_external_service(service)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/integration/apis", response_model=List[APIConfig])
async def get_api_configs(
    current_user: Dict = Depends(require_admin)
):
    """Get API configurations"""
    try:
        return await management_service.get_api_configs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integration/apis", response_model=APIConfig)
async def create_api_config(
    config: APIConfig,
    current_user: Dict = Depends(require_system)
):
    """Create a new API configuration"""
    try:
        return await management_service.create_api_config(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/integration/webhooks", response_model=List[WebhookConfig])
async def get_webhook_configs(
    current_user: Dict = Depends(require_admin)
):
    """Get webhook configurations"""
    try:
        return await management_service.get_webhook_configs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integration/webhooks", response_model=WebhookConfig)
async def create_webhook_config(
    config: WebhookConfig,
    current_user: Dict = Depends(require_system)
):
    """Create a new webhook configuration"""
    try:
        return await management_service.create_webhook_config(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Marketplace Routes
@router.get("/marketplace/items", response_model=List[MarketplaceItem])
async def get_marketplace_items(
    type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict = Depends(get_current_user)
):
    """Get marketplace items"""
    try:
        return await management_service.get_marketplace_items(
            type=type,
            tags=tags,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/marketplace/items", response_model=MarketplaceItem)
async def create_marketplace_item(
    item: MarketplaceItem,
    current_user: Dict = Depends(require_admin)
):
    """Create a new marketplace item"""
    try:
        return await management_service.create_marketplace_item(item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marketplace/orders", response_model=List[MarketplaceOrder])
async def get_marketplace_orders(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict = Depends(require_admin)
):
    """Get marketplace orders"""
    try:
        return await management_service.get_marketplace_orders(
            user_id=user_id,
            status=status,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/marketplace/orders", response_model=MarketplaceOrder)
async def create_marketplace_order(
    order: MarketplaceOrder,
    current_user: Dict = Depends(get_current_user)
):
    """Create a new marketplace order"""
    try:
        return await management_service.create_marketplace_order(order)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 