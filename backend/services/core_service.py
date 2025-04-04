from typing import Dict, List, Optional
from datetime import datetime
import psutil
import logging
from models.core_components import (
    UserProfile, Notification, DashboardMetrics, NavigationItem,
    UserSettings, SystemHealth, ResourceUsage, DeploymentStatus,
    UserManagement, SystemOverview, SystemStatus
)
from database.core_db import CoreDB

logger = logging.getLogger(__name__)

class CoreService:
    def __init__(self):
        self.db = CoreDB()
        self._initialize_services()

    def _initialize_services(self):
        """Initialize required services and connections"""
        try:
            # Initialize database connections
            self.db.connect()
            logger.info("Core services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize core services: {str(e)}")
            raise

    async def get_dashboard_metrics(self) -> DashboardMetrics:
        """Get dashboard metrics and system overview"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()

            # Get application metrics
            metrics = await self.db.get_dashboard_metrics()
            
            return DashboardMetrics(
                total_users=metrics["total_users"],
                active_users=metrics["active_users"],
                system_status=metrics["system_status"],
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                network_usage={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv
                },
                error_rate=metrics["error_rate"],
                response_time=metrics["response_time"]
            )
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {str(e)}")
            raise

    async def get_system_overview(self) -> SystemOverview:
        """Get system overview and status"""
        try:
            # Get system information
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = (datetime.now() - boot_time).total_seconds()
            
            # Get application information
            overview = await self.db.get_system_overview()
            
            return SystemOverview(
                uptime=uptime,
                version=overview["version"],
                environment=overview["environment"],
                last_update=overview["last_update"],
                next_maintenance=overview["next_maintenance"],
                active_services=overview["active_services"],
                system_info=overview["system_info"],
                performance_metrics=overview["performance_metrics"]
            )
        except Exception as e:
            logger.error(f"Error getting system overview: {str(e)}")
            raise

    async def get_navigation(self, user_id: str) -> List[NavigationItem]:
        """Get navigation items based on user permissions"""
        try:
            # Get user permissions
            permissions = await self.db.get_user_permissions(user_id)
            
            # Get navigation items
            items = await self.db.get_navigation_items()
            
            # Filter items based on permissions
            filtered_items = [
                item for item in items
                if all(perm in permissions for perm in item.permissions)
            ]
            
            return filtered_items
        except Exception as e:
            logger.error(f"Error getting navigation: {str(e)}")
            raise

    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile"""
        try:
            profile = await self.db.get_user_profile(user_id)
            return UserProfile(**profile)
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise

    async def update_user_profile(self, user_id: str, profile: UserProfile) -> UserProfile:
        """Update user profile"""
        try:
            updated_profile = await self.db.update_user_profile(user_id, profile.dict())
            return UserProfile(**updated_profile)
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            raise

    async def get_user_settings(self, user_id: str) -> UserSettings:
        """Get user settings"""
        try:
            settings = await self.db.get_user_settings(user_id)
            return UserSettings(**settings)
        except Exception as e:
            logger.error(f"Error getting user settings: {str(e)}")
            raise

    async def update_user_settings(self, user_id: str, settings: UserSettings) -> UserSettings:
        """Update user settings"""
        try:
            updated_settings = await self.db.update_user_settings(user_id, settings.dict())
            return UserSettings(**updated_settings)
        except Exception as e:
            logger.error(f"Error updating user settings: {str(e)}")
            raise

    async def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        page: int = 1,
        limit: int = 10
    ) -> List[Notification]:
        """Get user notifications"""
        try:
            notifications = await self.db.get_notifications(
                user_id,
                unread_only=unread_only,
                page=page,
                limit=limit
            )
            return [Notification(**notification) for notification in notifications]
        except Exception as e:
            logger.error(f"Error getting notifications: {str(e)}")
            raise

    async def mark_notification_read(self, user_id: str, notification_id: str) -> Dict:
        """Mark notification as read"""
        try:
            return await self.db.mark_notification_read(user_id, notification_id)
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            raise

    async def get_system_health(self) -> SystemHealth:
        """Get system health status"""
        try:
            # Get system health information
            health = await self.db.get_system_health()
            
            # Check system resources
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine system status
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                status = SystemStatus.CRITICAL
            elif cpu_percent > 80 or memory.percent > 80 or disk.percent > 80:
                status = SystemStatus.WARNING
            else:
                status = SystemStatus.HEALTHY
            
            return SystemHealth(
                status=status,
                components=health["components"],
                last_check=datetime.utcnow(),
                issues=health["issues"],
                recommendations=health["recommendations"],
                metrics={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent
                }
            )
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            raise

    async def get_resource_usage(self) -> ResourceUsage:
        """Get system resource usage"""
        try:
            # Get system resource information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Get process information
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info())
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Get service information
            services = await self.db.get_service_status()
            
            return ResourceUsage(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                network_in=network.bytes_recv,
                network_out=network.bytes_sent,
                processes=processes,
                services=services
            )
        except Exception as e:
            logger.error(f"Error getting resource usage: {str(e)}")
            raise

    async def get_deployments(
        self,
        status: Optional[str] = None,
        environment: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> List[DeploymentStatus]:
        """Get deployment status"""
        try:
            deployments = await self.db.get_deployments(
                status=status,
                environment=environment,
                page=page,
                limit=limit
            )
            return [DeploymentStatus(**deployment) for deployment in deployments]
        except Exception as e:
            logger.error(f"Error getting deployments: {str(e)}")
            raise

    async def get_user_management(self) -> UserManagement:
        """Get user management overview"""
        try:
            management = await self.db.get_user_management()
            return UserManagement(**management)
        except Exception as e:
            logger.error(f"Error getting user management: {str(e)}")
            raise

    async def get_user(self, user_id: str) -> UserProfile:
        """Get user details"""
        try:
            user = await self.db.get_user(user_id)
            return UserProfile(**user)
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            raise

    async def update_user(self, user_id: str, user_data: Dict) -> UserProfile:
        """Update user details"""
        try:
            updated_user = await self.db.update_user(user_id, user_data)
            return UserProfile(**updated_user)
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise

    async def delete_user(self, user_id: str) -> Dict:
        """Delete user"""
        try:
            return await self.db.delete_user(user_id)
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.db.close()
            logger.info("Core services cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up core services: {str(e)}")
            raise 