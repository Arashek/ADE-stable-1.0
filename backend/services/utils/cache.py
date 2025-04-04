import logging
import time
from typing import Dict, Any, Optional, Callable, TypeVar, Generic
import hashlib
import json
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Type variable for cache value type
T = TypeVar('T')

class ModelCache(Generic[T]):
    """Cache implementation for model responses to improve performance and reduce costs"""
    
    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.logger = logging.getLogger(__name__)
        
    def _create_key(self, params: Dict[str, Any]) -> str:
        """Create a cache key from the input parameters"""
        # Sort the dictionary to ensure consistent keys
        serialized = json.dumps(params, sort_keys=True)
        # Create a hash of the serialized data
        return hashlib.md5(serialized.encode()).hexdigest()
        
    async def get(self, params: Dict[str, Any]) -> Optional[T]:
        """Get a value from the cache if it exists and is not expired"""
        key = self._create_key(params)
        
        if key in self.cache:
            entry = self.cache[key]
            now = time.time()
            
            # Check if the entry is expired
            if now - entry["timestamp"] > self.ttl_seconds:
                self.logger.debug(f"Cache hit but expired for key: {key}")
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                return None
                
            # Update access time
            self.access_times[key] = now
            self.logger.debug(f"Cache hit for key: {key}")
            return entry["value"]
            
        self.logger.debug(f"Cache miss for key: {key}")
        return None
        
    async def set(self, params: Dict[str, Any], value: T) -> None:
        """Set a value in the cache"""
        key = self._create_key(params)
        now = time.time()
        
        # If we're at capacity, remove the least recently used item
        if len(self.cache) >= self.max_size:
            self._evict_lru()
            
        # Store the value and timestamp
        self.cache[key] = {
            "value": value,
            "timestamp": now
        }
        self.access_times[key] = now
        self.logger.debug(f"Cached value for key: {key}")
        
    async def invalidate(self, params: Dict[str, Any]) -> bool:
        """Invalidate a specific cache entry"""
        key = self._create_key(params)
        
        if key in self.cache:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            self.logger.debug(f"Invalidated cache for key: {key}")
            return True
            
        return False
        
    async def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.access_times.clear()
        self.logger.debug("Cache cleared")
        
    def _evict_lru(self) -> None:
        """Evict the least recently used cache entry"""
        if not self.access_times:
            return
            
        # Find the oldest accessed key
        oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        
        # Remove from cache and access times
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
        self.logger.debug(f"Evicted LRU cache entry: {oldest_key}")
        
    async def async_cached(self, func: Callable) -> Callable:
        """Decorator for caching async function results"""
        async def wrapper(*args, **kwargs):
            # Create parameters dictionary
            params = {
                "args": args,
                "kwargs": kwargs
            }
            
            # Try to get from cache
            cached_result = await self.get(params)
            if cached_result is not None:
                return cached_result
                
            # Call the original function
            result = await func(*args, **kwargs)
            
            # Cache the result
            await self.set(params, result)
            
            return result
            
        return wrapper
