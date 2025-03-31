from typing import Dict, List, Optional
from datetime import datetime
import psutil
import logging
from ..models.owner_panel import (
    SystemMetrics,
    UserStats,
    SecurityConfig,
    FrontendConfig,
    SupportTicket,
    AuditLog,
    SystemDiagnostics,
    APIKey,
    DashboardMetrics,
    APIConfig,
    WebhookConfig,
    MarketplaceItem,
    MarketplaceOrder,
    SystemDiagnostic,
    PerformanceMetric,
    ErrorLog,
    LandingPageContent,
    ThemeConfig,
    UIComponent
)
from ..database.owner_panel_db import OwnerPanelDB
from ..utils.security import generate_api_key, hash_api_key
from ..utils.backup import create_backup, restore_backup
from ..config.logging_config import logger
from ..config.cache_config import cache
import uuid

class OwnerPanelService:
    def __init__(self):
        self.db = OwnerPanelDB()
        self._initialize_services()

    def _initialize_services(self):
        """Initialize required services and connections"""
        try:
            # Initialize database connections
            self.db.connect()
            logger.info("Owner panel services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize owner panel services: {str(e)}")
            raise

    async def get_system_metrics(self) -> SystemMetrics:
        """Get system-wide metrics and statistics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get application-specific metrics
            active_users = await self.db.get_active_users_count()
            total_users = await self.db.get_total_users_count()
            api_requests = await self.db.get_api_requests_count()
            error_rate = await self.db.get_error_rate()

            return SystemMetrics(
                active_users=active_users,
                total_users=total_users,
                system_load=cpu_percent,
                memory_usage=memory.percent,
                storage_usage=disk.percent,
                api_requests=api_requests,
                error_rate=error_rate
            )
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            raise

    async def get_user_statistics(self) -> UserStats:
        """Get user-related statistics"""
        try:
            stats = await self.db.get_user_statistics()
            return UserStats(**stats)
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            raise

    async def get_security_config(self) -> SecurityConfig:
        """Get current security configuration"""
        try:
            config = await self.db.get_security_config()
            return SecurityConfig(**config)
        except Exception as e:
            logger.error(f"Error getting security config: {str(e)}")
            raise

    async def update_security_config(self, config: SecurityConfig) -> SecurityConfig:
        """Update security configuration"""
        try:
            await self.db.update_security_config(config.dict())
            return config
        except Exception as e:
            logger.error(f"Error updating security config: {str(e)}")
            raise

    async def get_frontend_config(self) -> FrontendConfig:
        """Get frontend configuration"""
        try:
            config = await self.db.get_frontend_config()
            return FrontendConfig(**config)
        except Exception as e:
            logger.error(f"Error getting frontend config: {str(e)}")
            raise

    async def update_frontend_config(self, config: FrontendConfig) -> FrontendConfig:
        """Update frontend configuration"""
        try:
            await self.db.update_frontend_config(config.dict())
            return config
        except Exception as e:
            logger.error(f"Error updating frontend config: {str(e)}")
            raise

    async def get_support_tickets(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> List[SupportTicket]:
        """Get support tickets with filtering and pagination"""
        try:
            tickets = await self.db.get_support_tickets(
                status=status,
                priority=priority,
                page=page,
                limit=limit
            )
            return [SupportTicket(**ticket) for ticket in tickets]
        except Exception as e:
            logger.error(f"Error getting support tickets: {str(e)}")
            raise

    async def get_system_diagnostics(self) -> SystemDiagnostics:
        """Get system diagnostics and health information"""
        try:
            diagnostics = await self.db.get_system_diagnostics()
            return SystemDiagnostics(**diagnostics)
        except Exception as e:
            logger.error(f"Error getting system diagnostics: {str(e)}")
            raise

    async def get_audit_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action_type: Optional[str] = None,
        user_id: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> List[AuditLog]:
        """Get audit logs with filtering and pagination"""
        try:
            logs = await self.db.get_audit_logs(
                start_date=start_date,
                end_date=end_date,
                action_type=action_type,
                user_id=user_id,
                page=page,
                limit=limit
            )
            return [AuditLog(**log) for log in logs]
        except Exception as e:
            logger.error(f"Error getting audit logs: {str(e)}")
            raise

    async def create_system_backup(self) -> Dict:
        """Create a system backup"""
        try:
            backup_id = await create_backup()
            return {"backup_id": backup_id, "status": "success"}
        except Exception as e:
            logger.error(f"Error creating system backup: {str(e)}")
            raise

    async def restore_system_backup(self, backup_id: str) -> Dict:
        """Restore system from backup"""
        try:
            await restore_backup(backup_id)
            return {"status": "success", "message": "System restored successfully"}
        except Exception as e:
            logger.error(f"Error restoring system backup: {str(e)}")
            raise

    async def get_api_keys(self) -> List[APIKey]:
        """Get all API keys"""
        try:
            keys = await self.db.get_api_keys()
            return [APIKey(**key) for key in keys]
        except Exception as e:
            logger.error(f"Error getting API keys: {str(e)}")
            raise

    async def create_api_key(self, description: str, permissions: List[str]) -> APIKey:
        """Create a new API key"""
        try:
            key = generate_api_key()
            hashed_key = hash_api_key(key)
            
            api_key = APIKey(
                key=key,
                hashed_key=hashed_key,
                description=description,
                permissions=permissions,
                created_at=datetime.utcnow()
            )
            
            await self.db.create_api_key(api_key.dict())
            return api_key
        except Exception as e:
            logger.error(f"Error creating API key: {str(e)}")
            raise

    async def revoke_api_key(self, key_id: str) -> Dict:
        """Revoke an API key"""
        try:
            await self.db.revoke_api_key(key_id)
            return {"status": "success", "message": "API key revoked successfully"}
        except Exception as e:
            logger.error(f"Error revoking API key: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.db.close()
            logger.info("Owner panel services cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up owner panel services: {str(e)}")
            raise

    async def get_dashboard_metrics(self) -> DashboardMetrics:
        """Get system overview metrics"""
        try:
            # Get cached metrics if available
            cached_metrics = await cache.get("dashboard_metrics")
            if cached_metrics:
                return DashboardMetrics.parse_raw(cached_metrics)

            # Calculate metrics
            metrics = DashboardMetrics(
                total_users=await self._get_total_users(),
                active_users=await self._get_active_users(),
                total_projects=await self._get_total_projects(),
                active_projects=await self._get_active_projects(),
                system_status=await self._get_system_status(),
                api_requests=await self._get_api_requests_count(),
                error_rate=await self._calculate_error_rate(),
                uptime=await self._calculate_uptime(),
                last_updated=datetime.utcnow()
            )

            # Cache metrics for 5 minutes
            await cache.set("dashboard_metrics", metrics.json(), 300)
            return metrics
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {str(e)}")
            raise

    async def manage_api_config(self, config: APIConfig) -> APIConfig:
        """Create or update API configuration"""
        try:
            # Validate API configuration
            await self._validate_api_config(config)
            
            # Store API configuration
            await self._store_api_config(config)
            
            # Update API documentation
            await self._update_api_documentation(config)
            
            return config
        except Exception as e:
            logger.error(f"Error managing API config: {str(e)}")
            raise

    async def configure_webhook(self, webhook: WebhookConfig) -> WebhookConfig:
        """Configure webhook endpoint"""
        try:
            # Validate webhook URL
            await self._validate_webhook_url(webhook.url)
            
            # Generate webhook secret
            webhook.secret = await self._generate_webhook_secret()
            
            # Store webhook configuration
            await self._store_webhook_config(webhook)
            
            return webhook
        except Exception as e:
            logger.error(f"Error configuring webhook: {str(e)}")
            raise

    async def manage_marketplace_item(self, item: MarketplaceItem) -> MarketplaceItem:
        """Create or update marketplace item"""
        try:
            # Validate marketplace item
            await self._validate_marketplace_item(item)
            
            # Store marketplace item
            await self._store_marketplace_item(item)
            
            # Update marketplace index
            await self._update_marketplace_index(item)
            
            return item
        except Exception as e:
            logger.error(f"Error managing marketplace item: {str(e)}")
            raise

    async def handle_support_ticket(self, ticket: SupportTicket) -> SupportTicket:
        """Create or update support ticket"""
        try:
            # Validate support ticket
            await self._validate_support_ticket(ticket)
            
            # Store support ticket
            await self._store_support_ticket(ticket)
            
            # Notify support team
            await self._notify_support_team(ticket)
            
            return ticket
        except Exception as e:
            logger.error(f"Error handling support ticket: {str(e)}")
            raise

    async def get_system_diagnostics(self) -> SystemDiagnostic:
        """Get system diagnostics information"""
        try:
            # Get system metrics
            metrics = await self._collect_system_metrics()
            
            # Analyze system health
            health_status = await self._analyze_system_health(metrics)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(health_status)
            
            return SystemDiagnostic(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                **metrics,
                recommendations=recommendations
            )
        except Exception as e:
            logger.error(f"Error getting system diagnostics: {str(e)}")
            raise

    async def get_performance_metrics(self) -> List[PerformanceMetric]:
        """Get performance metrics for all endpoints"""
        try:
            # Get cached metrics if available
            cached_metrics = await cache.get("performance_metrics")
            if cached_metrics:
                return [PerformanceMetric.parse_raw(m) for m in cached_metrics]

            # Collect performance metrics
            metrics = await self._collect_performance_metrics()
            
            # Cache metrics for 5 minutes
            await cache.set("performance_metrics", [m.json() for m in metrics], 300)
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            raise

    async def get_error_logs(self, 
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           level: Optional[str] = None) -> List[ErrorLog]:
        """Get error logs with optional filtering"""
        try:
            # Get error logs from storage
            logs = await self._get_error_logs(start_time, end_time, level)
            
            # Format and return logs
            return [ErrorLog.parse_raw(log) for log in logs]
        except Exception as e:
            logger.error(f"Error getting error logs: {str(e)}")
            raise

    async def manage_landing_page_content(self, content: LandingPageContent) -> LandingPageContent:
        """Create or update landing page content"""
        try:
            # Validate content
            await self._validate_landing_page_content(content)
            
            # Store content
            await self._store_landing_page_content(content)
            
            # Update landing page cache
            await self._update_landing_page_cache(content)
            
            return content
        except Exception as e:
            logger.error(f"Error managing landing page content: {str(e)}")
            raise

    async def manage_theme_config(self, theme: ThemeConfig) -> ThemeConfig:
        """Create or update theme configuration"""
        try:
            # Validate theme configuration
            await self._validate_theme_config(theme)
            
            # Store theme configuration
            await self._store_theme_config(theme)
            
            # Update theme cache
            await self._update_theme_cache(theme)
            
            return theme
        except Exception as e:
            logger.error(f"Error managing theme configuration: {str(e)}")
            raise

    async def manage_ui_component(self, component: UIComponent) -> UIComponent:
        """Create or update UI component"""
        try:
            # Validate UI component
            await self._validate_ui_component(component)
            
            # Store UI component
            await self._store_ui_component(component)
            
            # Update component library cache
            await self._update_component_library_cache(component)
            
            return component
        except Exception as e:
            logger.error(f"Error managing UI component: {str(e)}")
            raise

    # Private helper methods
    async def _get_total_users(self) -> int:
        """Get total number of users"""
        # Implementation
        pass

    async def _get_active_users(self) -> int:
        """Get number of active users"""
        # Implementation
        pass

    async def _get_total_projects(self) -> int:
        """Get total number of projects"""
        # Implementation
        pass

    async def _get_active_projects(self) -> int:
        """Get number of active projects"""
        # Implementation
        pass

    async def _get_system_status(self) -> str:
        """Get current system status"""
        # Implementation
        pass

    async def _get_api_requests_count(self) -> int:
        """Get total number of API requests"""
        # Implementation
        pass

    async def _calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        # Implementation
        pass

    async def _calculate_uptime(self) -> float:
        """Calculate system uptime"""
        # Implementation
        pass

    async def _validate_api_config(self, config: APIConfig):
        """Validate API configuration"""
        # Implementation
        pass

    async def _store_api_config(self, config: APIConfig):
        """Store API configuration"""
        # Implementation
        pass

    async def _update_api_documentation(self, config: APIConfig):
        """Update API documentation"""
        # Implementation
        pass

    async def _validate_webhook_url(self, url: str):
        """Validate webhook URL"""
        # Implementation
        pass

    async def _generate_webhook_secret(self):
        """Generate a new webhook secret"""
        # Implementation
        pass

    async def _store_webhook_config(self, webhook: WebhookConfig):
        """Store webhook configuration"""
        # Implementation
        pass

    async def _validate_marketplace_item(self, item: MarketplaceItem):
        """Validate marketplace item"""
        # Implementation
        pass

    async def _store_marketplace_item(self, item: MarketplaceItem):
        """Store marketplace item"""
        # Implementation
        pass

    async def _update_marketplace_index(self, item: MarketplaceItem):
        """Update marketplace index"""
        # Implementation
        pass

    async def _validate_support_ticket(self, ticket: SupportTicket):
        """Validate support ticket"""
        # Implementation
        pass

    async def _store_support_ticket(self, ticket: SupportTicket):
        """Store support ticket"""
        # Implementation
        pass

    async def _notify_support_team(self, ticket: SupportTicket):
        """Notify support team"""
        # Implementation
        pass

    async def _collect_system_metrics(self):
        """Collect system metrics"""
        # Implementation
        pass

    async def _analyze_system_health(self, metrics: dict):
        """Analyze system health"""
        # Implementation
        pass

    async def _generate_recommendations(self, health_status: str):
        """Generate system recommendations"""
        # Implementation
        pass

    async def _get_error_logs(self, start_time: Optional[datetime], end_time: Optional[datetime], level: Optional[str]):
        """Get error logs from storage"""
        # Implementation
        pass

    async def _validate_landing_page_content(self, content: LandingPageContent):
        """Validate landing page content"""
        # Implementation
        pass

    async def _store_landing_page_content(self, content: LandingPageContent):
        """Store landing page content"""
        # Implementation
        pass

    async def _update_landing_page_cache(self, content: LandingPageContent):
        """Update landing page cache"""
        # Implementation
        pass

    async def _validate_theme_config(self, theme: ThemeConfig):
        """Validate theme configuration"""
        # Implementation
        pass

    async def _store_theme_config(self, theme: ThemeConfig):
        """Store theme configuration"""
        # Implementation
        pass

    async def _update_theme_cache(self, theme: ThemeConfig):
        """Update theme cache"""
        # Implementation
        pass

    async def _validate_ui_component(self, component: UIComponent):
        """Validate UI component"""
        # Implementation
        pass

    async def _store_ui_component(self, component: UIComponent):
        """Store UI component"""
        # Implementation
        pass

    async def _update_component_library_cache(self, component: UIComponent):
        """Update component library cache"""
        # Implementation
        pass

    async def _collect_performance_metrics(self):
        """Collect performance metrics"""
        # Implementation
        pass 