from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis
from typing import Optional
from ..utils.settings import get_settings
from ..utils.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

class DatabaseManager:
    _mongodb_client: Optional[AsyncIOMotorClient] = None
    _redis_client: Optional[Redis] = None
    
    @classmethod
    async def get_mongodb(cls) -> AsyncIOMotorClient:
        """Get MongoDB client"""
        if cls._mongodb_client is None:
            try:
                cls._mongodb_client = AsyncIOMotorClient(
                    settings.MONGODB_URI,
                    username=settings.MONGODB_USER,
                    password=settings.MONGODB_PASSWORD
                )
                # Test connection
                await cls._mongodb_client.admin.command('ping')
                logger.info("MongoDB connection established")
            except Exception as e:
                logger.error(f"MongoDB connection failed: {str(e)}")
                raise
        return cls._mongodb_client
    
    @classmethod
    def get_redis(cls) -> Redis:
        """Get Redis client"""
        if cls._redis_client is None:
            try:
                cls._redis_client = Redis(
                    host='redis',
                    port=6379,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True
                )
                # Test connection
                cls._redis_client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Redis connection failed: {str(e)}")
                raise
        return cls._redis_client
    
    @classmethod
    async def close_connections(cls):
        """Close all database connections"""
        if cls._mongodb_client:
            cls._mongodb_client.close()
            cls._mongodb_client = None
            logger.info("MongoDB connection closed")
            
        if cls._redis_client:
            cls._redis_client.close()
            cls._redis_client = None
            logger.info("Redis connection closed") 