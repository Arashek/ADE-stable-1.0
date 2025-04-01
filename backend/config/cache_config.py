from redis import asyncio as aioredis
from config.settings import settings

class RedisCache:
    def __init__(self):
        self.redis = None
        self.redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        if settings.REDIS_PASSWORD:
            self.redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"

    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            return self.redis
        except Exception as e:
            raise Exception(f"Failed to connect to Redis: {str(e)}")

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str):
        """Get value from cache"""
        if not self.redis:
            await self.connect()
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int = 3600):
        """Set value in cache with expiration"""
        if not self.redis:
            await self.connect()
        await self.redis.set(key, value, ex=expire)

    async def delete(self, key: str):
        """Delete value from cache"""
        if not self.redis:
            await self.connect()
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis:
            await self.connect()
        return await self.redis.exists(key)

# Create global cache instance
cache = RedisCache() 