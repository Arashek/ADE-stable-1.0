from functools import wraps
from typing import Callable, Any
import time
from datetime import datetime, timedelta
from ..config.logging_config import logger
from ..database.redis_client import redis_client

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass

def rate_limit(
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000,
    requests_per_day: int = 10000
) -> Callable:
    """
    Rate limiting decorator that checks Redis for request counts
    and raises RateLimitExceeded if limits are exceeded
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                # Get user ID from request context
                user_id = kwargs.get('user_id')
                if not user_id:
                    raise ValueError("User ID not found in request context")

                # Generate Redis keys for different time windows
                minute_key = f"rate_limit:minute:{user_id}"
                hour_key = f"rate_limit:hour:{user_id}"
                day_key = f"rate_limit:day:{user_id}"

                # Check minute rate limit
                minute_count = await redis_client.get(minute_key)
                if minute_count and int(minute_count) >= requests_per_minute:
                    raise RateLimitExceeded("Rate limit exceeded for minute window")

                # Check hour rate limit
                hour_count = await redis_client.get(hour_key)
                if hour_count and int(hour_count) >= requests_per_hour:
                    raise RateLimitExceeded("Rate limit exceeded for hour window")

                # Check day rate limit
                day_count = await redis_client.get(day_key)
                if day_count and int(day_count) >= requests_per_day:
                    raise RateLimitExceeded("Rate limit exceeded for day window")

                # Increment counters with appropriate expiration
                pipeline = redis_client.pipeline()
                pipeline.incr(minute_key)
                pipeline.expire(minute_key, 60)  # 1 minute
                pipeline.incr(hour_key)
                pipeline.expire(hour_key, 3600)  # 1 hour
                pipeline.incr(day_key)
                pipeline.expire(day_key, 86400)  # 1 day
                await pipeline.execute()

                # Execute the original function
                return await func(*args, **kwargs)

            except RateLimitExceeded as e:
                logger.warning(f"Rate limit exceeded for user {user_id}: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Error in rate limiting: {str(e)}")
                raise

        return wrapper
    return decorator

class RateLimiter:
    """Class for managing rate limits with Redis"""
    
    def __init__(
        self,
        redis_client,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000
    ):
        self.redis = redis_client
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day

    async def check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limits"""
        try:
            # Check all time windows
            minute_count = await self.redis.get(f"rate_limit:minute:{user_id}")
            hour_count = await self.redis.get(f"rate_limit:hour:{user_id}")
            day_count = await self.redis.get(f"rate_limit:day:{user_id}")

            if (minute_count and int(minute_count) >= self.requests_per_minute) or \
               (hour_count and int(hour_count) >= self.requests_per_hour) or \
               (day_count and int(day_count) >= self.requests_per_day):
                return False

            return True
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            raise

    async def increment_rate_limit(self, user_id: str) -> None:
        """Increment rate limit counters for user"""
        try:
            pipeline = self.redis.pipeline()
            
            # Increment and set expiration for minute window
            pipeline.incr(f"rate_limit:minute:{user_id}")
            pipeline.expire(f"rate_limit:minute:{user_id}", 60)
            
            # Increment and set expiration for hour window
            pipeline.incr(f"rate_limit:hour:{user_id}")
            pipeline.expire(f"rate_limit:hour:{user_id}", 3600)
            
            # Increment and set expiration for day window
            pipeline.incr(f"rate_limit:day:{user_id}")
            pipeline.expire(f"rate_limit:day:{user_id}", 86400)
            
            await pipeline.execute()
        except Exception as e:
            logger.error(f"Error incrementing rate limit: {str(e)}")
            raise

    async def reset_rate_limit(self, user_id: str) -> None:
        """Reset rate limit counters for user"""
        try:
            pipeline = self.redis.pipeline()
            pipeline.delete(f"rate_limit:minute:{user_id}")
            pipeline.delete(f"rate_limit:hour:{user_id}")
            pipeline.delete(f"rate_limit:day:{user_id}")
            await pipeline.execute()
        except Exception as e:
            logger.error(f"Error resetting rate limit: {str(e)}")
            raise

    async def get_rate_limit_status(self, user_id: str) -> dict:
        """Get current rate limit status for user"""
        try:
            return {
                "minute": {
                    "count": int(await self.redis.get(f"rate_limit:minute:{user_id}") or 0),
                    "limit": self.requests_per_minute
                },
                "hour": {
                    "count": int(await self.redis.get(f"rate_limit:hour:{user_id}") or 0),
                    "limit": self.requests_per_hour
                },
                "day": {
                    "count": int(await self.redis.get(f"rate_limit:day:{user_id}") or 0),
                    "limit": self.requests_per_day
                }
            }
        except Exception as e:
            logger.error(f"Error getting rate limit status: {str(e)}")
            raise 