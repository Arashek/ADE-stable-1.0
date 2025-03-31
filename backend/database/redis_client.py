from typing import Any, Optional, Union
import json
from redis.asyncio import Redis
from ..config.settings import settings
from ..config.logging_config import logger

class RedisClient:
    """Redis client for caching and rate limiting"""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Error connecting to Redis: {str(e)}")
            raise
            
    async def disconnect(self):
        """Disconnect from Redis"""
        try:
            if self.redis:
                await self.redis.close()
                logger.info("Successfully disconnected from Redis")
        except Exception as e:
            logger.error(f"Error disconnecting from Redis: {str(e)}")
            raise
            
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        try:
            if not self.redis:
                raise RuntimeError("Redis client not initialized")
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Error getting value from Redis: {str(e)}")
            raise
            
    async def set(
        self,
        key: str,
        value: Union[str, dict, list],
        expire: Optional[int] = None
    ) -> bool:
        """Set value in Redis with optional expiration"""
        try:
            if not self.redis:
                raise RuntimeError("Redis client not initialized")
                
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
                
            await self.redis.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Error setting value in Redis: {str(e)}")
            raise
            
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            if not self.redis:
                raise RuntimeError("Redis client not initialized")
            return bool(await self.redis.delete(key))
        except Exception as e:
            logger.error(f"Error deleting key from Redis: {str(e)}")
            raise
            
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            if not self.redis:
                raise RuntimeError("Redis client not initialized")
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error(f"Error checking key existence in Redis: {str(e)}")
            raise
            
    async def incr(self, key: str) -> int:
        """Increment counter in Redis"""
        try:
            if not self.redis:
                raise RuntimeError("Redis client not initialized")
            return await self.redis.incr(key)
        except Exception as e:
            logger.error(f"Error incrementing counter in Redis: {str(e)}")
            raise
            
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key in Redis"""
        try:
            if not self.redis:
                raise RuntimeError("Redis client not initialized")
            return bool(await self.redis.expire(key, seconds))
        except Exception as e:
            logger.error(f"Error setting expiration in Redis: {str(e)}")
            raise
            
    async def ttl(self, key: str) -> int:
        """Get time to live for key in Redis"""
        try:
            if not self.redis:
                raise RuntimeError("Redis client not initialized")
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL from Redis: {str(e)}")
            raise
            
    async def pipeline(self):
        """Get Redis pipeline for batch operations"""
        try:
            if not self.redis:
                raise RuntimeError("Redis client not initialized")
            return self.redis.pipeline()
        except Exception as e:
            logger.error(f"Error getting Redis pipeline: {str(e)}")
            raise
            
    async def flushdb(self) -> bool:
        """Flush all keys from Redis database"""
        try:
            if not self.redis:
                raise RuntimeError("Redis client not initialized")
            return bool(await self.redis.flushdb())
        except Exception as e:
            logger.error(f"Error flushing Redis database: {str(e)}")
            raise

# Create global Redis client instance
redis_client = RedisClient() 