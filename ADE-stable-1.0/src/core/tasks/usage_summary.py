import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from src.storage.document.repositories import UsageRepository, UserRepository
from src.core.services.usage_tracking import UsageTrackingService
from src.core.providers.registry import ProviderRegistry
from src.config.usage import USAGE_TRACKING_SETTINGS
from src.core.dependencies.database import get_database
from src.core.dependencies.providers import get_provider_registry
from src.core.dependencies.users import get_user_repository

logger = logging.getLogger(__name__)

class UsageSummaryTask:
    """Background task for updating usage summaries"""
    
    def __init__(self):
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.service: Optional[UsageTrackingService] = None
    
    async def start(self):
        """Start the summary update task"""
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
        logger.info("Usage summary update task started")
    
    async def stop(self):
        """Stop the summary update task"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Usage summary update task stopped")
    
    async def _run(self):
        """Run the summary update task"""
        while self.is_running:
            try:
                if not self.service:
                    raise RuntimeError("Usage tracking service not initialized")
                
                # Get all users
                users = await self.service.user_repository.find({})
                
                # Update summary for each user
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
                        
                        # Update summary in database
                        await self.service.usage_repository.update_summary(
                            user.id,
                            summary
                        )
                        
                        logger.debug(f"Updated usage summary for user {user.id}")
                        
                    except Exception as e:
                        logger.error(f"Error updating summary for user {user.id}: {str(e)}")
                        continue
                
                # Wait before next update
                await asyncio.sleep(USAGE_TRACKING_SETTINGS["summary_update_interval"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in usage summary task: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying 