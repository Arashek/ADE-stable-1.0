from typing import Any, Optional, Dict, List, Union, Callable
import json
import logging
from datetime import datetime, timedelta
from redis import Redis
from functools import wraps

logger = logging.getLogger(__name__)

class CacheConfig:
    """Configuration for caching"""
    
    def __init__(
        self,
        default_ttl: int = 300,  # 5 minutes
        max_ttl: int = 3600,     # 1 hour
        prefix: str = "cache:",
        serialize: bool = True
    ):
        self.default_ttl = default_ttl
        self.max_ttl = max_ttl
        self.prefix = prefix
        self.serialize = serialize

class CacheManager:
    """Manages caching with Redis backend"""
    
    def __init__(
        self,
        redis_client: Redis,
        config: Optional[CacheConfig] = None
    ):
        self.redis = redis_client
        self.config = config or CacheConfig()
    
    def _get_key(self, key: str) -> str:
        """Get fully qualified cache key"""
        return f"{self.config.prefix}{key}"
    
    def _serialize(self, value: Any) -> str:
        """Serialize value for storage"""
        if not self.config.serialize:
            return str(value)
        return json.dumps(value)
    
    def _deserialize(self, value: str) -> Any:
        """Deserialize value from storage"""
        if not self.config.serialize:
            return value
        return json.loads(value)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            cache_key = self._get_key(key)
            value = await self.redis.get(cache_key)
            
            if value is None:
                return None
                
            return self._deserialize(value)
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        try:
            cache_key = self._get_key(key)
            ttl = min(ttl or self.config.default_ttl, self.config.max_ttl)
            
            serialized = self._serialize(value)
            await self.redis.setex(cache_key, ttl, serialized)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            cache_key = self._get_key(key)
            await self.redis.delete(cache_key)
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            cache_key = self._get_key(key)
            return bool(await self.redis.exists(cache_key))
            
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {str(e)}")
            return False
    
    async def clear(self, pattern: str = "*") -> bool:
        """Clear cache entries matching pattern"""
        try:
            cache_pattern = self._get_key(pattern)
            keys = await self.redis.keys(cache_pattern)
            
            if keys:
                await self.redis.delete(*keys)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error for pattern {pattern}: {str(e)}")
            return False
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        try:
            cache_keys = [self._get_key(k) for k in keys]
            values = await self.redis.mget(cache_keys)
            
            return {
                k: self._deserialize(v)
                for k, v in zip(keys, values)
                if v is not None
            }
            
        except Exception as e:
            logger.error(f"Cache get_many error for keys {keys}: {str(e)}")
            return {}
    
    async def set_many(
        self,
        items: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Set multiple values in cache"""
        try:
            ttl = min(ttl or self.config.default_ttl, self.config.max_ttl)
            pipe = self.redis.pipeline()
            
            for key, value in items.items():
                cache_key = self._get_key(key)
                serialized = self._serialize(value)
                pipe.setex(cache_key, ttl, serialized)
            
            await pipe.execute()
            return True
            
        except Exception as e:
            logger.error(f"Cache set_many error: {str(e)}")
            return False
    
    def cached(
        self,
        ttl: Optional[int] = None,
        key_prefix: str = "",
        key_builder: Optional[Callable] = None
    ):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Build cache key
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    # Default key building
                    key_parts = [key_prefix, func.__name__]
                    key_parts.extend(str(arg) for arg in args)
                    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                    cache_key = ":".join(key_parts)
                
                # Try to get from cache
                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
    
    async def invalidate_pattern(self, pattern: str) -> bool:
        """Invalidate all cache entries matching pattern"""
        return await self.clear(pattern)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check cache health"""
        try:
            # Test basic operations
            test_key = "health_check"
            test_value = {"test": "data"}
            
            # Test set
            set_success = await self.set(test_key, test_value)
            
            # Test get
            get_value = await self.get(test_key)
            get_success = get_value == test_value
            
            # Test delete
            delete_success = await self.delete(test_key)
            
            # Get cache stats
            info = await self.redis.info()
            
            return {
                "status": "healthy" if all([set_success, get_success, delete_success]) else "degraded",
                "operations": {
                    "set": set_success,
                    "get": get_success,
                    "delete": delete_success
                },
                "stats": {
                    "used_memory": info.get("used_memory", 0),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_connections_received": info.get("total_connections_received", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            } 