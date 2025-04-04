from typing import Dict, List, Optional
from datetime import datetime
import logging
from models.management_components import (
    Permission, Role, AdminSettings, UserActivity,
    Component, Model, ServiceConfig, InfrastructureSettings,
    ExternalService, APIConfig, WebhookConfig,
    MarketplaceItem, MarketplaceOrder
)
from database.management_db import ManagementDB

logger = logging.getLogger(__name__)

class ManagementService:
    def __init__(self):
        self.db = ManagementDB()
        self._initialize_services()

    def _initialize_services(self):
        """Initialize required services and connections"""
        try:
            # Initialize database connections
            self.db.connect()
            logger.info("Management services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize management services: {str(e)}")
            raise

    # Security & Access Control Methods
    async def get_permissions(self) -> List[Permission]:
        """Get all permissions"""
        try:
            permissions = await self.db.get_permissions()
            return [Permission(**permission) for permission in permissions]
        except Exception as e:
            logger.error(f"Error getting permissions: {str(e)}")
            raise

    async def create_permission(self, permission: Permission) -> Permission:
        """Create a new permission"""
        try:
            created_permission = await self.db.create_permission(permission.dict())
            return Permission(**created_permission)
        except Exception as e:
            logger.error(f"Error creating permission: {str(e)}")
            raise

    async def get_roles(self) -> List[Role]:
        """Get all roles"""
        try:
            roles = await self.db.get_roles()
            return [Role(**role) for role in roles]
        except Exception as e:
            logger.error(f"Error getting roles: {str(e)}")
            raise

    async def create_role(self, role: Role) -> Role:
        """Create a new role"""
        try:
            created_role = await self.db.create_role(role.dict())
            return Role(**created_role)
        except Exception as e:
            logger.error(f"Error creating role: {str(e)}")
            raise

    async def get_admin_settings(self) -> List[AdminSettings]:
        """Get admin settings"""
        try:
            settings = await self.db.get_admin_settings()
            return [AdminSettings(**setting) for setting in settings]
        except Exception as e:
            logger.error(f"Error getting admin settings: {str(e)}")
            raise

    async def update_admin_setting(self, setting_id: str, setting: AdminSettings) -> AdminSettings:
        """Update admin setting"""
        try:
            updated_setting = await self.db.update_admin_setting(setting_id, setting.dict())
            return AdminSettings(**updated_setting)
        except Exception as e:
            logger.error(f"Error updating admin setting: {str(e)}")
            raise

    async def get_user_activity(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 10
    ) -> List[UserActivity]:
        """Get user activity"""
        try:
            logs = await self.db.get_user_activity(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                start_date=start_date,
                end_date=end_date,
                page=page,
                limit=limit
            )
            return [UserActivity(**log) for log in logs]
        except Exception as e:
            logger.error(f"Error getting user activity: {str(e)}")
            raise

    # Architecture Management Methods
    async def get_components(
        self,
        type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Component]:
        """Get system components"""
        try:
            components = await self.db.get_components(type=type, status=status)
            return [Component(**component) for component in components]
        except Exception as e:
            logger.error(f"Error getting components: {str(e)}")
            raise

    async def create_component(self, component: Component) -> Component:
        """Create a new component"""
        try:
            created_component = await self.db.create_component(component.dict())
            return Component(**created_component)
        except Exception as e:
            logger.error(f"Error creating component: {str(e)}")
            raise

    async def get_models(self) -> List[Model]:
        """Get data models"""
        try:
            models = await self.db.get_models()
            return [Model(**model) for model in models]
        except Exception as e:
            logger.error(f"Error getting models: {str(e)}")
            raise

    async def create_model(self, model: Model) -> Model:
        """Create a new model"""
        try:
            created_model = await self.db.create_model(model.dict())
            return Model(**created_model)
        except Exception as e:
            logger.error(f"Error creating model: {str(e)}")
            raise

    async def get_service_configs(
        self,
        service_id: Optional[str] = None,
        environment: Optional[str] = None
    ) -> List[ServiceConfig]:
        """Get service configurations"""
        try:
            configs = await self.db.get_service_configs(
                service_id=service_id,
                environment=environment
            )
            return [ServiceConfig(**config) for config in configs]
        except Exception as e:
            logger.error(f"Error getting service configs: {str(e)}")
            raise

    async def update_service_config(
        self,
        config_id: str,
        config: ServiceConfig
    ) -> ServiceConfig:
        """Update service configuration"""
        try:
            updated_config = await self.db.update_service_config(config_id, config.dict())
            return ServiceConfig(**updated_config)
        except Exception as e:
            logger.error(f"Error updating service config: {str(e)}")
            raise

    async def get_infrastructure_settings(self) -> List[InfrastructureSettings]:
        """Get infrastructure settings"""
        try:
            settings = await self.db.get_infrastructure_settings()
            return [InfrastructureSettings(**setting) for setting in settings]
        except Exception as e:
            logger.error(f"Error getting infrastructure settings: {str(e)}")
            raise

    async def update_infrastructure_setting(
        self,
        setting_id: str,
        setting: InfrastructureSettings
    ) -> InfrastructureSettings:
        """Update infrastructure setting"""
        try:
            updated_setting = await self.db.update_infrastructure_setting(setting_id, setting.dict())
            return InfrastructureSettings(**updated_setting)
        except Exception as e:
            logger.error(f"Error updating infrastructure setting: {str(e)}")
            raise

    # Integration Management Methods
    async def get_external_services(
        self,
        type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ExternalService]:
        """Get external services"""
        try:
            services = await self.db.get_external_services(type=type, status=status)
            return [ExternalService(**service) for service in services]
        except Exception as e:
            logger.error(f"Error getting external services: {str(e)}")
            raise

    async def create_external_service(self, service: ExternalService) -> ExternalService:
        """Create a new external service"""
        try:
            created_service = await self.db.create_external_service(service.dict())
            return ExternalService(**created_service)
        except Exception as e:
            logger.error(f"Error creating external service: {str(e)}")
            raise

    async def get_api_configs(self) -> List[APIConfig]:
        """Get API configurations"""
        try:
            configs = await self.db.get_api_configs()
            return [APIConfig(**config) for config in configs]
        except Exception as e:
            logger.error(f"Error getting API configs: {str(e)}")
            raise

    async def create_api_config(self, config: APIConfig) -> APIConfig:
        """Create a new API configuration"""
        try:
            created_config = await self.db.create_api_config(config.dict())
            return APIConfig(**created_config)
        except Exception as e:
            logger.error(f"Error creating API config: {str(e)}")
            raise

    async def get_webhook_configs(self) -> List[WebhookConfig]:
        """Get webhook configurations"""
        try:
            configs = await self.db.get_webhook_configs()
            return [WebhookConfig(**config) for config in configs]
        except Exception as e:
            logger.error(f"Error getting webhook configs: {str(e)}")
            raise

    async def create_webhook_config(self, config: WebhookConfig) -> WebhookConfig:
        """Create a new webhook configuration"""
        try:
            created_config = await self.db.create_webhook_config(config.dict())
            return WebhookConfig(**created_config)
        except Exception as e:
            logger.error(f"Error creating webhook config: {str(e)}")
            raise

    # Marketplace Methods
    async def get_marketplace_items(
        self,
        type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        page: int = 1,
        limit: int = 10
    ) -> List[MarketplaceItem]:
        """Get marketplace items"""
        try:
            items = await self.db.get_marketplace_items(
                type=type,
                tags=tags,
                page=page,
                limit=limit
            )
            return [MarketplaceItem(**item) for item in items]
        except Exception as e:
            logger.error(f"Error getting marketplace items: {str(e)}")
            raise

    async def create_marketplace_item(self, item: MarketplaceItem) -> MarketplaceItem:
        """Create a new marketplace item"""
        try:
            created_item = await self.db.create_marketplace_item(item.dict())
            return MarketplaceItem(**created_item)
        except Exception as e:
            logger.error(f"Error creating marketplace item: {str(e)}")
            raise

    async def get_marketplace_orders(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> List[MarketplaceOrder]:
        """Get marketplace orders"""
        try:
            orders = await self.db.get_marketplace_orders(
                user_id=user_id,
                status=status,
                page=page,
                limit=limit
            )
            return [MarketplaceOrder(**order) for order in orders]
        except Exception as e:
            logger.error(f"Error getting marketplace orders: {str(e)}")
            raise

    async def create_marketplace_order(self, order: MarketplaceOrder) -> MarketplaceOrder:
        """Create a new marketplace order"""
        try:
            created_order = await self.db.create_marketplace_order(order.dict())
            return MarketplaceOrder(**created_order)
        except Exception as e:
            logger.error(f"Error creating marketplace order: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.db.close()
            logger.info("Management services cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up management services: {str(e)}")
            raise 