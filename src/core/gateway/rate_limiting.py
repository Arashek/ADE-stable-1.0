from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import logging
from datetime import datetime, timedelta
import redis
import json

logger = logging.getLogger(__name__)

class UserTier(Enum):
    """User tiers for rate limiting."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

@dataclass
class RateLimitConfig:
    """Rate limit configuration for a tier."""
    requests_per_minute: int
    burst_size: int
    priority: int  # Higher number = higher priority
    cost_per_request: float  # Cost in tokens per request
    max_concurrent_requests: int
    timeout: float = 30.0
    retry_count: int = 3

class TokenBucket:
    """Token bucket implementation for rate limiting."""
    
    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        burst_size: int,
        redis_client: redis.Redis
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.burst_size = burst_size
        self.redis_client = redis_client
        
    def _get_bucket_key(self, user_id: str, endpoint: str) -> str:
        """Get Redis key for bucket state."""
        return f"rate_limit:{user_id}:{endpoint}"
        
    def _get_bucket_state(self, key: str) -> Tuple[float, float]:
        """Get current bucket state from Redis."""
        state = self.redis_client.get(key)
        if state:
            tokens, last_update = json.loads(state)
            return float(tokens), float(last_update)
        return self.capacity, time.time()
        
    def _update_bucket_state(
        self,
        key: str,
        tokens: float,
        last_update: float
    ) -> None:
        """Update bucket state in Redis."""
        self.redis_client.setex(
            key,
            int(self.capacity / self.refill_rate),  # TTL in seconds
            json.dumps([tokens, last_update])
        )
        
    def consume(self, user_id: str, endpoint: str, tokens: int) -> Tuple[bool, Dict[str, str]]:
        """Consume tokens from bucket."""
        key = self._get_bucket_key(user_id, endpoint)
        current_tokens, last_update = self._get_bucket_state(key)
        
        # Calculate token refill
        now = time.time()
        time_passed = now - last_update
        refill_amount = time_passed * self.refill_rate
        current_tokens = min(
            self.capacity,
            current_tokens + refill_amount
        )
        
        # Check if enough tokens available
        if current_tokens < tokens:
            # Calculate reset time
            reset_time = int((tokens - current_tokens) / self.refill_rate)
            return False, {
                "X-RateLimit-Limit": str(self.capacity),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time),
                "X-RateLimit-Burst": str(self.burst_size)
            }
            
        # Consume tokens
        current_tokens -= tokens
        self._update_bucket_state(key, current_tokens, now)
        
        return True, {
            "X-RateLimit-Limit": str(self.capacity),
            "X-RateLimit-Remaining": str(int(current_tokens)),
            "X-RateLimit-Reset": "0",
            "X-RateLimit-Burst": str(self.burst_size)
        }

class RateLimiter:
    """Rate limiter with user tier support."""
    
    def __init__(
        self,
        redis_client: redis.Redis,
        tier_configs: Optional[Dict[UserTier, RateLimitConfig]] = None
    ):
        self.redis_client = redis_client
        self.tier_configs = tier_configs or {
            UserTier.FREE: RateLimitConfig(
                requests_per_minute=60,
                burst_size=10,
                priority=1,
                cost_per_request=1.0,
                max_concurrent_requests=5
            ),
            UserTier.BASIC: RateLimitConfig(
                requests_per_minute=300,
                burst_size=50,
                priority=2,
                cost_per_request=0.8,
                max_concurrent_requests=20
            ),
            UserTier.PRO: RateLimitConfig(
                requests_per_minute=1000,
                burst_size=200,
                priority=3,
                cost_per_request=0.5,
                max_concurrent_requests=50
            ),
            UserTier.ENTERPRISE: RateLimitConfig(
                requests_per_minute=5000,
                burst_size=1000,
                priority=4,
                cost_per_request=0.2,
                max_concurrent_requests=200
            )
        }
        
        # Initialize token buckets for each tier
        self.buckets: Dict[UserTier, TokenBucket] = {}
        for tier, config in self.tier_configs.items():
            self.buckets[tier] = TokenBucket(
                capacity=config.requests_per_minute,
                refill_rate=config.requests_per_minute / 60.0,  # Convert to tokens per second
                burst_size=config.burst_size,
                redis_client=redis_client
            )
            
    def get_tier_config(self, tier: UserTier) -> RateLimitConfig:
        """Get rate limit configuration for tier."""
        return self.tier_configs.get(tier, self.tier_configs[UserTier.FREE])
        
    def check_rate_limit(
        self,
        user_id: str,
        endpoint: str,
        tier: UserTier,
        cost_multiplier: float = 1.0
    ) -> Tuple[bool, Dict[str, str]]:
        """Check if request is allowed and return rate limit headers."""
        config = self.get_tier_config(tier)
        bucket = self.buckets[tier]
        
        # Calculate token cost
        token_cost = int(config.cost_per_request * cost_multiplier)
        
        # Check concurrent requests
        concurrent_key = f"concurrent:{user_id}:{endpoint}"
        current_concurrent = int(self.redis_client.get(concurrent_key) or 0)
        
        if current_concurrent >= config.max_concurrent_requests:
            return False, {
                "X-RateLimit-Limit": str(config.requests_per_minute),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": "0",
                "X-RateLimit-Burst": str(config.burst_size),
                "X-RateLimit-Concurrent": str(current_concurrent),
                "X-RateLimit-Max-Concurrent": str(config.max_concurrent_requests)
            }
            
        # Check rate limit
        allowed, headers = bucket.consume(user_id, endpoint, token_cost)
        
        if allowed:
            # Increment concurrent requests
            self.redis_client.incr(concurrent_key)
            self.redis_client.expire(concurrent_key, config.timeout)
            
        return allowed, headers
        
    def release_concurrent_request(
        self,
        user_id: str,
        endpoint: str,
        tier: UserTier
    ) -> None:
        """Release a concurrent request slot."""
        config = self.get_tier_config(tier)
        concurrent_key = f"concurrent:{user_id}:{endpoint}"
        self.redis_client.decr(concurrent_key)
        
    def get_rate_limit_info(
        self,
        user_id: str,
        endpoint: str,
        tier: UserTier
    ) -> Dict[str, str]:
        """Get current rate limit information."""
        config = self.get_tier_config(tier)
        bucket = self.buckets[tier]
        
        concurrent_key = f"concurrent:{user_id}:{endpoint}"
        current_concurrent = int(self.redis_client.get(concurrent_key) or 0)
        
        current_tokens, _ = bucket._get_bucket_state(
            bucket._get_bucket_key(user_id, endpoint)
        )
        
        return {
            "X-RateLimit-Limit": str(config.requests_per_minute),
            "X-RateLimit-Remaining": str(int(current_tokens)),
            "X-RateLimit-Reset": "0",
            "X-RateLimit-Burst": str(config.burst_size),
            "X-RateLimit-Concurrent": str(current_concurrent),
            "X-RateLimit-Max-Concurrent": str(config.max_concurrent_requests),
            "X-RateLimit-Tier": tier.value
        } 