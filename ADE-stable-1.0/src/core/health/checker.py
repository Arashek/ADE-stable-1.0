from typing import Dict, Any, List
import logging
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from ..persistence.database import DatabaseManager
from ..tasks.queue_manager import TaskQueueManager
from ..providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)

class ComponentStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class ComponentHealth:
    name: str
    status: ComponentStatus
    details: Dict[str, Any]
    last_checked: datetime
    error: Optional[str] = None

class HealthChecker:
    """Monitors health of all system components"""
    
    def __init__(
        self,
        database_manager: DatabaseManager,
        task_queue_manager: TaskQueueManager,
        provider_registry: ProviderRegistry
    ):
        self.database_manager = database_manager
        self.task_queue_manager = task_queue_manager
        self.provider_registry = provider_registry
        self.components: Dict[str, ComponentHealth] = {}
    
    async def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all components"""
        try:
            # Check database health
            db_health = await self._check_database()
            self.components["database"] = db_health
            
            # Check task queue health
            task_health = await self._check_task_queue()
            self.components["task_queue"] = task_health
            
            # Check provider registry health
            provider_health = await self._check_providers()
            self.components["providers"] = provider_health
            
            # Determine overall system status
            overall_status = self._determine_overall_status()
            
            return {
                "status": overall_status.value,
                "timestamp": datetime.now().isoformat(),
                "components": {
                    name: {
                        "status": health.status.value,
                        "details": health.details,
                        "last_checked": health.last_checked.isoformat(),
                        "error": health.error
                    }
                    for name, health in self.components.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": ComponentStatus.UNHEALTHY.value,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def _check_database(self) -> ComponentHealth:
        """Check database health"""
        try:
            db_status = await self.database_manager.health_check()
            
            if db_status["status"] == "healthy":
                return ComponentHealth(
                    name="database",
                    status=ComponentStatus.HEALTHY,
                    details=db_status,
                    last_checked=datetime.now()
                )
            else:
                return ComponentHealth(
                    name="database",
                    status=ComponentStatus.UNHEALTHY,
                    details=db_status,
                    last_checked=datetime.now(),
                    error=db_status.get("error")
                )
                
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return ComponentHealth(
                name="database",
                status=ComponentStatus.UNHEALTHY,
                details={},
                last_checked=datetime.now(),
                error=str(e)
            )
    
    async def _check_task_queue(self) -> ComponentHealth:
        """Check task queue health"""
        try:
            queue_status = await self.task_queue_manager.health_check()
            
            if queue_status["status"] == "healthy":
                return ComponentHealth(
                    name="task_queue",
                    status=ComponentStatus.HEALTHY,
                    details=queue_status,
                    last_checked=datetime.now()
                )
            else:
                return ComponentHealth(
                    name="task_queue",
                    status=ComponentStatus.DEGRADED,
                    details=queue_status,
                    last_checked=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Task queue health check failed: {str(e)}")
            return ComponentHealth(
                name="task_queue",
                status=ComponentStatus.UNHEALTHY,
                details={},
                last_checked=datetime.now(),
                error=str(e)
            )
    
    async def _check_providers(self) -> ComponentHealth:
        """Check provider registry health"""
        try:
            providers = self.provider_registry.get_available_providers()
            provider_status = {
                "total_providers": len(providers),
                "available_providers": providers,
                "status": "healthy"
            }
            
            return ComponentHealth(
                name="providers",
                status=ComponentStatus.HEALTHY,
                details=provider_status,
                last_checked=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Provider health check failed: {str(e)}")
            return ComponentHealth(
                name="providers",
                status=ComponentStatus.DEGRADED,
                details={},
                last_checked=datetime.now(),
                error=str(e)
            )
    
    def _determine_overall_status(self) -> ComponentStatus:
        """Determine overall system status based on component health"""
        if not self.components:
            return ComponentStatus.UNKNOWN
            
        # If any component is unhealthy, system is unhealthy
        if any(c.status == ComponentStatus.UNHEALTHY for c in self.components.values()):
            return ComponentStatus.UNHEALTHY
            
        # If any component is degraded, system is degraded
        if any(c.status == ComponentStatus.DEGRADED for c in self.components.values()):
            return ComponentStatus.DEGRADED
            
        # If all components are healthy, system is healthy
        if all(c.status == ComponentStatus.HEALTHY for c in self.components.values()):
            return ComponentStatus.HEALTHY
            
        return ComponentStatus.UNKNOWN 