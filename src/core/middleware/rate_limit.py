from typing import Dict, Any, Optional, Tuple
import logging
import time
from fastapi import Request, Response, HTTPException
from redis import Redis
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimitConfig:
    """Configuration for rate limiting"""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: int = 10,
        block_duration: int = 300  # 5 minutes
    ):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.block_duration = block_duration

class RateLimitMiddleware:
    """Middleware for API rate limiting"""
    
    def __init__(
        self,
        redis_client: Redis,
        config: Optional[RateLimitConfig] = None,
        error_handler: Optional[callable] = None
    ):
        self.redis = redis_client
        self.config = config or RateLimitConfig()
        self.error_handler = error_handler or self._default_error_handler
    
    async def __call__(
        self,
        request: Request,
        call_next: callable
    ) -> Response:
        """Process request and apply rate limiting"""
        try:
            # Get client identifier
            client_id = self._get_client_id(request)
            
            # Check if client is blocked
            if await self._is_client_blocked(client_id):
                return await self.error_handler(
                    request,
                    "Rate limit exceeded. Please try again later.",
                    429
                )
            
            # Check rate limit
            if not await self._check_rate_limit(client_id):
                return await self.error_handler(
                    request,
                    "Rate limit exceeded. Please try again later.",
                    429
                )
            
            # Process request
            response = await call_next(request)
            
            # Update rate limit counters
            await self._update_rate_limit(client_id)
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(self.config.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(
                await self._get_remaining_requests(client_id)
            )
            response.headers["X-RateLimit-Reset"] = str(
                await self._get_reset_time(client_id)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            return await self.error_handler(request, str(e), 500)
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique identifier for client"""
        # Try to get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Try to get API key from header
        api_key = request.headers.get("X-API-Key")
        
        # Combine identifiers
        return f"{client_ip}:{api_key}" if api_key else client_ip
    
    async def _is_client_blocked(self, client_id: str) -> bool:
        """Check if client is blocked"""
        block_key = f"rate_limit:block:{client_id}"
        return bool(await self.redis.get(block_key))
    
    async def _check_rate_limit(self, client_id: str) -> bool:
        """Check if request is within rate limit"""
        current = await self._get_current_requests(client_id)
        return current < self.config.requests_per_minute
    
    async def _get_current_requests(self, client_id: str) -> int:
        """Get current request count for client"""
        key = f"rate_limit:requests:{client_id}"
        count = await self.redis.get(key)
        return int(count) if count else 0
    
    async def _update_rate_limit(self, client_id: str) -> None:
        """Update rate limit counters"""
        key = f"rate_limit:requests:{client_id}"
        pipe = self.redis.pipeline()
        
        # Increment counter
        pipe.incr(key)
        
        # Set expiry if key is new
        pipe.expire(key, 60)  # 1 minute
        
        # Check if we need to block client
        current = await self._get_current_requests(client_id)
        if current > self.config.requests_per_minute + self.config.burst_size:
            block_key = f"rate_limit:block:{client_id}"
            pipe.setex(block_key, self.config.block_duration, "1")
        
        await pipe.execute()
    
    async def _get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client"""
        current = await self._get_current_requests(client_id)
        return max(0, self.config.requests_per_minute - current)
    
    async def _get_reset_time(self, client_id: str) -> int:
        """Get time until rate limit resets"""
        key = f"rate_limit:requests:{client_id}"
        ttl = await self.redis.ttl(key)
        return max(0, ttl)
    
    async def _default_error_handler(
        self,
        request: Request,
        message: str,
        status_code: int
    ) -> Response:
        """Default error handler for rate limit violations"""
        return Response(
            content={
                "error": message,
                "timestamp": datetime.now().isoformat()
            },
            status_code=status_code,
            media_type="application/json"
        ) 