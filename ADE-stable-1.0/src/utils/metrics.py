"""Provider metrics with Prometheus integration."""
from prometheus_client import Counter, Histogram, Gauge, Info
import time
import functools
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from src.storage.document.models.usage import UsageRecord

# Configure logging
logger = logging.getLogger("ade-metrics")

# Provider metrics
PROVIDER_REQUEST_COUNT = Counter(
    'provider_request_total', 
    'Total number of provider requests',
    ['provider_id', 'provider_type', 'status']
)

PROVIDER_REQUEST_LATENCY = Histogram(
    'provider_request_latency_seconds', 
    'Provider request latency in seconds',
    ['provider_id', 'provider_type'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 60.0)
)

PROVIDER_TOKEN_USAGE = Counter(
    'provider_token_usage_total', 
    'Total number of tokens used',
    ['provider_id', 'provider_type', 'operation']
)

PROVIDER_ACTIVE = Gauge(
    'provider_active',
    'Whether a provider is active (1) or not (0)',
    ['provider_id', 'provider_type']
)

PROVIDER_INFO = Info(
    'provider',
    'Provider information',
    ['provider_id']
)

# Usage metrics
USAGE_COUNTER = Counter(
    "ade_usage_total",
    "Total number of API calls",
    ["user_id", "provider", "model", "type", "status"]
)

TOKEN_COUNTER = Counter(
    "ade_tokens_total",
    "Total number of tokens used",
    ["user_id", "provider", "model", "type"]
)

COST_COUNTER = Counter(
    "ade_cost_total",
    "Total cost in USD",
    ["user_id", "provider", "model", "type"]
)

# Latency metrics
REQUEST_LATENCY = Histogram(
    "ade_request_latency_seconds",
    "Request latency in seconds",
    ["user_id", "provider", "model", "type"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Quota metrics
QUOTA_USAGE = Gauge(
    "ade_quota_usage",
    "Current quota usage",
    ["user_id", "type"]
)

QUOTA_LIMIT = Gauge(
    "ade_quota_limit",
    "Quota limit",
    ["user_id", "type"]
)

def track_provider_request(f):
    """Decorator to track provider requests.
    
    Args:
        f: The async function to decorate.
        
    Returns:
        The decorated function that tracks metrics.
    """
    @functools.wraps(f)
    async def wrapper(self, *args, **kwargs):
        start_time = time.time()
        provider_id = getattr(self, 'provider_id', 'unknown')
        provider_type = getattr(self, 'provider_type', 'unknown')
        
        try:
            # Execute the original function
            result = await f(self, *args, **kwargs)
            
            # Record successful request
            PROVIDER_REQUEST_COUNT.labels(
                provider_id=provider_id, 
                provider_type=provider_type, 
                status='success'
            ).inc()
            
            # Record latency
            PROVIDER_REQUEST_LATENCY.labels(
                provider_id=provider_id, 
                provider_type=provider_type
            ).observe(time.time() - start_time)
            
            # Record token usage if available
            if hasattr(result, 'metadata') and result.metadata and 'tokens' in result.metadata:
                PROVIDER_TOKEN_USAGE.labels(
                    provider_id=provider_id, 
                    provider_type=provider_type,
                    operation='generate'
                ).inc(result.metadata['tokens'])
            
            return result
        except Exception as e:
            # Record failed request
            PROVIDER_REQUEST_COUNT.labels(
                provider_id=provider_id, 
                provider_type=provider_type, 
                status='error'
            ).inc()
            
            # Log the error
            logger.error(f"Provider request failed: {str(e)}")
            
            # Re-raise the exception
            raise
    
    return wrapper

def register_provider_metrics(provider) -> None:
    """Register metrics for a provider.
    
    Args:
        provider: The provider instance to register metrics for.
    """
    try:
        provider_id = provider.provider_id
        provider_type = provider.provider_type
        
        # Update active status
        PROVIDER_ACTIVE.labels(
            provider_id=provider_id, 
            provider_type=provider_type
        ).set(1 if provider.is_initialized else 0)
        
        # Set provider info
        capabilities = [c.value for c in provider.get_capabilities()]
        models = provider.list_available_models()
        
        PROVIDER_INFO.labels(provider_id=provider_id).info({
            'provider_type': provider_type,
            'capabilities': ','.join(capabilities),
            'models': ','.join(models),
            'success_rate': str(provider.performance.success_rate),
            'avg_latency': str(provider.performance.average_latency)
        })
        
        logger.info(f"Registered metrics for provider {provider_id}")
    except Exception as e:
        logger.error(f"Failed to register metrics for provider: {str(e)}")

def update_provider_status(provider_id: str, provider_type: str, active: bool) -> None:
    """Update provider active status.
    
    Args:
        provider_id: The ID of the provider.
        provider_type: The type of the provider.
        active: Whether the provider is active.
    """
    try:
        PROVIDER_ACTIVE.labels(
            provider_id=provider_id, 
            provider_type=provider_type
        ).set(1 if active else 0)
        
        logger.debug(f"Updated status for provider {provider_id}: {'active' if active else 'inactive'}")
    except Exception as e:
        logger.error(f"Failed to update provider status: {str(e)}")

def get_provider_metrics(provider_id: str) -> Dict[str, Any]:
    """Get metrics for a specific provider.
    
    Args:
        provider_id: The ID of the provider.
        
    Returns:
        Dictionary containing provider metrics.
    """
    try:
        return {
            'request_count': {
                'success': PROVIDER_REQUEST_COUNT.labels(
                    provider_id=provider_id, 
                    status='success'
                )._value.get(),
                'error': PROVIDER_REQUEST_COUNT.labels(
                    provider_id=provider_id, 
                    status='error'
                )._value.get()
            },
            'avg_latency': PROVIDER_REQUEST_LATENCY.labels(
                provider_id=provider_id
            )._sum.get() / PROVIDER_REQUEST_LATENCY.labels(
                provider_id=provider_id
            )._count.get() if PROVIDER_REQUEST_LATENCY.labels(
                provider_id=provider_id
            )._count.get() > 0 else 0,
            'token_usage': PROVIDER_TOKEN_USAGE.labels(
                provider_id=provider_id,
                operation='generate'
            )._value.get(),
            'active': PROVIDER_ACTIVE.labels(
                provider_id=provider_id
            )._value.get()
        }
    except Exception as e:
        logger.error(f"Failed to get metrics for provider {provider_id}: {str(e)}")
        return {}

def track_usage_metrics(record: UsageRecord) -> None:
    """Track usage metrics for a record"""
    try:
        # Track usage count
        USAGE_COUNTER.labels(
            user_id=record.user_id,
            provider=record.provider,
            model=record.model,
            type=record.usage_type,
            status=record.status
        ).inc()
        
        # Track tokens
        TOKEN_COUNTER.labels(
            user_id=record.user_id,
            provider=record.provider,
            model=record.model,
            type=record.usage_type
        ).inc(record.tokens_used)
        
        # Track cost
        COST_COUNTER.labels(
            user_id=record.user_id,
            provider=record.provider,
            model=record.model,
            type=record.usage_type
        ).inc(record.cost)
        
        # Track latency if available
        if "response_time" in record.metadata:
            REQUEST_LATENCY.labels(
                user_id=record.user_id,
                provider=record.provider,
                model=record.model,
                type=record.usage_type
            ).observe(record.metadata["response_time"])
        
        # Track quota usage
        if "quota_usage" in record.metadata:
            for usage_type, usage in record.metadata["quota_usage"].items():
                QUOTA_USAGE.labels(
                    user_id=record.user_id,
                    type=usage_type
                ).set(usage)
        
        # Track quota limits
        if "quota_limits" in record.metadata:
            for usage_type, limit in record.metadata["quota_limits"].items():
                QUOTA_LIMIT.labels(
                    user_id=record.user_id,
                    type=usage_type
                ).set(limit)
        
    except Exception as e:
        logger.error(f"Error tracking usage metrics: {str(e)}")

def track_provider_metrics(
    provider_id: str,
    provider_type: str,
    status: str,
    latency: float,
    error: Optional[str] = None
) -> None:
    """Track provider-specific metrics"""
    try:
        # Provider status counter
        Counter(
            "ade_provider_status_total",
            "Provider status counts",
            ["provider_id", "provider_type", "status"]
        ).labels(
            provider_id=provider_id,
            provider_type=provider_type,
            status=status
        ).inc()
        
        # Provider latency
        Histogram(
            "ade_provider_latency_seconds",
            "Provider request latency",
            ["provider_id", "provider_type"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        ).labels(
            provider_id=provider_id,
            provider_type=provider_type
        ).observe(latency)
        
        # Provider errors
        if error:
            Counter(
                "ade_provider_errors_total",
                "Provider error counts",
                ["provider_id", "provider_type", "error_type"]
            ).labels(
                provider_id=provider_id,
                provider_type=provider_type,
                error_type=type(error).__name__
            ).inc()
            
    except Exception as e:
        logger.error(f"Error tracking provider metrics: {str(e)}")

def track_rate_limit_metrics(
    user_id: str,
    provider: str,
    model: str,
    exceeded: bool
) -> None:
    """Track rate limit metrics"""
    try:
        Counter(
            "ade_rate_limit_total",
            "Rate limit events",
            ["user_id", "provider", "model", "exceeded"]
        ).labels(
            user_id=user_id,
            provider=provider,
            model=model,
            exceeded=str(exceeded).lower()
        ).inc()
        
    except Exception as e:
        logger.error(f"Error tracking rate limit metrics: {str(e)}")

def track_quota_alert_metrics(
    user_id: str,
    usage_type: str,
    current_usage: int,
    limit: int,
    threshold: float = 0.8
) -> None:
    """Track quota alert metrics"""
    try:
        usage_percentage = (current_usage / limit) * 100
        
        # Track usage percentage
        Gauge(
            "ade_quota_usage_percentage",
            "Quota usage percentage",
            ["user_id", "type"]
        ).labels(
            user_id=user_id,
            type=usage_type
        ).set(usage_percentage)
        
        # Track alert if threshold exceeded
        if usage_percentage >= (threshold * 100):
            Counter(
                "ade_quota_alert_total",
                "Quota alert events",
                ["user_id", "type", "threshold"]
            ).labels(
                user_id=user_id,
                type=usage_type,
                threshold=str(threshold)
            ).inc()
            
    except Exception as e:
        logger.error(f"Error tracking quota alert metrics: {str(e)}") 