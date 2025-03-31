from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis
from typing import Dict

router = APIRouter()

async def get_mongodb() -> AsyncIOMotorClient:
    # Get MongoDB connection from your database module
    from src.core.database import get_database
    return await get_database()

async def get_redis() -> Redis:
    # Get Redis connection from your cache module
    from src.core.cache import get_redis
    return await get_redis()

@router.get("/health")
async def health_check(
    mongodb: AsyncIOMotorClient = Depends(get_mongodb),
    redis: Redis = Depends(get_redis)
) -> Dict[str, str]:
    """
    Health check endpoint that verifies connections to MongoDB and Redis
    """
    try:
        # Check MongoDB connection
        await mongodb.admin.command('ping')
        mongodb_status = "healthy"
    except Exception as e:
        mongodb_status = f"unhealthy: {str(e)}"

    try:
        # Check Redis connection
        redis.ping()
        redis_status = "healthy"
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if mongodb_status == "healthy" and redis_status == "healthy" else "unhealthy",
        "mongodb": mongodb_status,
        "redis": redis_status
    } 