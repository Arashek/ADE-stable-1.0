import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, List

from src.storage.document.repositories import UsageRepository, UserRepository
from src.core.services.usage_tracking import UsageTrackingService
from src.core.providers.registry import ProviderRegistry
from src.config.usage import USAGE_TRACKING_SETTINGS
from src.core.dependencies.database import get_database
from src.core.dependencies.providers import get_provider_registry
from src.core.dependencies.users import get_user_repository
from src.utils.metrics import track_quota_alert_metrics

logger = logging.getLogger(__name__)

class QuotaMonitorTask:
    """Background task for monitoring quota usage and sending alerts"""
    
    def __init__(self):
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.service: Optional[UsageTrackingService] = None
        self.alerted_users: Dict[str, Dict[str, bool]] = {}  # Track which users have been alerted
    
    async def start(self):
        """Start the quota monitoring task"""
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
        logger.info("Quota monitoring task started")
    
    async def stop(self):
        """Stop the quota monitoring task"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Quota monitoring task stopped")
    
    async def _run(self):
        """Run the quota monitoring task"""
        while self.is_running:
            try:
                if not self.service:
                    raise RuntimeError("Usage tracking service not initialized")
                
                # Get all users
                users = await self.service.user_repository.find({})
                
                # Check quota usage for each user
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
                        
                        # Check each usage type
                        for usage_type, limit in tier_config.quota_limits.items():
                            current_usage = summary.usage_by_type.get(usage_type, 0)
                            
                            # Track metrics
                            track_quota_alert_metrics(
                                user_id=user.id,
                                usage_type=usage_type,
                                current_usage=current_usage,
                                limit=limit,
                                threshold=USAGE_TRACKING_SETTINGS["quota_alert_threshold"]
                            )
                            
                            # Check if alert threshold is exceeded
                            if current_usage >= (limit * USAGE_TRACKING_SETTINGS["quota_alert_threshold"]):
                                # Check if we've already alerted this user for this type
                                if not self._has_alerted(user.id, usage_type):
                                    await self._send_quota_alert(
                                        user,
                                        usage_type,
                                        current_usage,
                                        limit
                                    )
                                    self._mark_alerted(user.id, usage_type)
                        
                        # Reset alerts at the start of each month
                        if datetime.utcnow().day == 1:
                            self._reset_alerts(user.id)
                        
                    except Exception as e:
                        logger.error(f"Error checking quota for user {user.id}: {str(e)}")
                        continue
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in quota monitoring task: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    def _has_alerted(self, user_id: str, usage_type: str) -> bool:
        """Check if we've already alerted a user for a specific usage type"""
        return (
            user_id in self.alerted_users and
            usage_type in self.alerted_users[user_id] and
            self.alerted_users[user_id][usage_type]
        )
    
    def _mark_alerted(self, user_id: str, usage_type: str) -> None:
        """Mark that we've alerted a user for a specific usage type"""
        if user_id not in self.alerted_users:
            self.alerted_users[user_id] = {}
        self.alerted_users[user_id][usage_type] = True
    
    def _reset_alerts(self, user_id: str) -> None:
        """Reset alerts for a user"""
        if user_id in self.alerted_users:
            self.alerted_users[user_id] = {}
    
    async def _send_quota_alert(
        self,
        user: any,
        usage_type: str,
        current_usage: int,
        limit: int
    ) -> None:
        """Send a quota alert to a user"""
        try:
            # Calculate usage percentage
            usage_percentage = (current_usage / limit) * 100
            
            # Log the alert
            logger.warning(
                f"Quota alert for user {user.id}: {usage_type} usage at "
                f"{usage_percentage:.1f}% of limit ({current_usage}/{limit})"
            )
            
            # TODO: Implement actual alert sending (email, notification, etc.)
            # For now, we just log the alert
            
        except Exception as e:
            logger.error(f"Error sending quota alert: {str(e)}") 