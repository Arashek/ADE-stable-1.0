import asyncio
import logging
from datetime import datetime, timedelta

from src.config.settings import get_settings
from src.core.dependencies.database import get_database
from src.storage.document.repositories import UsageRepository

logger = logging.getLogger(__name__)

class UsageCleanupTask:
    """Task to clean up old usage records"""
    
    def __init__(self):
        self.settings = get_settings()
        self.running = False
        self.task = None
    
    async def start(self):
        """Start the cleanup task"""
        if self.running:
            logger.warning("Usage cleanup task is already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run())
        logger.info("Started usage cleanup task")
    
    async def stop(self):
        """Stop the cleanup task"""
        if not self.running:
            logger.warning("Usage cleanup task is not running")
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped usage cleanup task")
    
    async def _run(self):
        """Run the cleanup task periodically"""
        while self.running:
            try:
                async for db in get_database():
                    repo = UsageRepository(db.client, db.database_name)
                    cutoff_date = datetime.now() - timedelta(days=self.settings.USAGE_RETENTION_DAYS)
                    result = await repo.delete_old_records(cutoff_date)
                    logger.info(f"Cleaned up {result.deleted_count} old usage records")
            except Exception as e:
                logger.error(f"Error in usage cleanup task: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying
                continue
            
            # Wait for next cleanup interval
            await asyncio.sleep(self.settings.USAGE_CLEANUP_INTERVAL) 