import asyncio
import logging
from datetime import datetime
from typing import Optional

from src.storage.document.repositories import UsageRepository, UserRepository
from src.core.services.usage_tracking import UsageTrackingService
from src.core.providers.registry import ProviderRegistry
from src.config.usage import USAGE_TRACKING_SETTINGS
from src.core.dependencies.database import get_database
from src.core.dependencies.providers import get_provider_registry
from src.core.dependencies.users import get_user_repository
from src.utils.metrics import (
    track_usage_metrics,
    track_provider_metrics,
    track_rate_limit_metrics,
    track_quota_alert_metrics
)

logger = logging.getLogger(__name__)

class MetricsUpdateTask:
    """Background task for updating metrics"""
    
    def __init__(self):
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.service: Optional[UsageTrackingService] = None
    
    async def start(self):
        """Start the metrics update task"""
        if self.is_running:
            return
        
        # Initialize service
        db = await anext(get_database())
        usage_repository = UsageRepository(db.client, db.name)
        user_repository = await anext(get_user_repository())
        provider_registry = await anext(get_provider_registry())
        
        self.service = UsageTrackingService(
            usage_repository=usage_repository,
            user_repository=user_repository,
            provider_registry=provider_registry
        )
        
        self.is_running = True
        self.task = asyncio.create_task(self._run())
        logger.info("Metrics update task started")
    
    async def stop(self):
        """Stop the metrics update task"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Metrics update task stopped")
    
    async def _run(self):
        """Run the metrics update task"""
        while self.is_running:
            try:
                if not self.service:
                    raise RuntimeError("Usage tracking service not initialized")
                
                # Get all users
                users = await self.service.user_repository.find({})
                
                # Update metrics for each user
                for user in users:
                    try:
                        # Get usage for the current month
                        start_of_month = datetime.utcnow().replace(
                            day=1, hour=0, minute=0, second=0, microsecond=0
                        )
                        
                        summary = await self.service.get_user_usage_summary(
                            user.id,
                            start_date=start_of_month
                        )
                        
                        # Get tier config
                        tier_config = self.service.tier_configs[user.billing_tier]
                        
                        # Update usage metrics
                        for usage_type, limit in tier_config.quota_limits.items():
                            current_usage = summary.usage_by_type.get(usage_type, 0)
                            
                            # Track quota metrics
                            track_quota_alert_metrics(
                                user_id=user.id,
                                usage_type=usage_type,
                                current_usage=current_usage,
                                limit=limit,
                                threshold=USAGE_TRACKING_SETTINGS["quota_alert_threshold"]
                            )
                        
                        # Update rate limit metrics
                        for provider in summary.usage_by_provider:
                            track_rate_limit_metrics(
                                user_id=user.id,
                                provider=provider,
                                model="all",
                                exceeded=False  # We don't track exceeded status here
                            )
                        
                    except Exception as e:
                        logger.error(f"Error updating metrics for user {user.id}: {str(e)}")
                        continue
                
                # Update provider metrics
                for provider in self.service.provider_registry.get_all_providers():
                    try:
                        track_provider_metrics(
                            provider_id=provider.provider_id,
                            provider_type=provider.provider_type,
                            status="active" if provider.is_initialized else "inactive",
                            latency=provider.performance.average_latency,
                            error=None
                        )
                    except Exception as e:
                        logger.error(f"Error updating metrics for provider {provider.provider_id}: {str(e)}")
                        continue
                
                # Wait before next update
                await asyncio.sleep(USAGE_TRACKING_SETTINGS["metrics_update_interval"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics update task: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying 