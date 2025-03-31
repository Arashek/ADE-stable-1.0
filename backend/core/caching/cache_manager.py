from typing import Any, Optional, Dict, List
import asyncio
from redis import Redis
from functools import wraps
import json
import hashlib
from datetime import timedelta

class CacheManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.default_ttl = 300  # 5 minutes

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        return await self.redis.set(key, json.dumps(value), ex=ttl)

    def cached(self, ttl: int = None):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                key = f"{func.__name__}:{hashlib.md5(str(args).encode()).hexdigest()}"
                
                # Try to get from cache
                cached_value = await self.get(key)
                if cached_value is not None:
                    return cached_value
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.set(key, result, ttl)
                return result
            return wrapper
        return decorator

class BatchRequestManager:
    def __init__(self, batch_size: int = 100, max_wait: float = 0.5):
        self.batch_size = batch_size
        self.max_wait = max_wait
        self.batches: Dict[str, List] = {}
        self.batch_locks: Dict[str, asyncio.Lock] = {}
        self.batch_events: Dict[str, asyncio.Event] = {}

    async def add_to_batch(self, batch_key: str, item: Any) -> Any:
        """Add item to batch and wait for processing"""
        if batch_key not in self.batches:
            self.batches[batch_key] = []
            self.batch_locks[batch_key] = asyncio.Lock()
            self.batch_events[batch_key] = asyncio.Event()

        async with self.batch_locks[batch_key]:
            batch = self.batches[batch_key]
            batch.append(item)
            
            if len(batch) >= self.batch_size:
                return await self._process_batch(batch_key)
            
            # Start timer for batch processing
            asyncio.create_task(self._schedule_batch_processing(batch_key))
            
            # Wait for batch processing
            await self.batch_events[batch_key].wait()
            return batch[-1]  # Return last processed item

    async def _schedule_batch_processing(self, batch_key: str):
        """Schedule batch processing after max_wait time"""
        await asyncio.sleep(self.max_wait)
        async with self.batch_locks[batch_key]:
            if self.batches[batch_key]:
                await self._process_batch(batch_key)

    async def _process_batch(self, batch_key: str) -> List[Any]:
        """Process a batch of items"""
        async with self.batch_locks[batch_key]:
            batch = self.batches[batch_key]
            self.batches[batch_key] = []
            self.batch_events[batch_key].set()
            self.batch_events[batch_key].clear()
            return batch
