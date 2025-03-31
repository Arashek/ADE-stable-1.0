from typing import Dict
from src.storage.document.models.usage import BillingTier, BillingTierConfig

# Default tier configurations
DEFAULT_TIER_CONFIGS: Dict[BillingTier, BillingTierConfig] = {
    BillingTier.FREE: BillingTierConfig(
        tier=BillingTier.FREE,
        monthly_price=0.0,
        quota_limits={
            "text_generation": 1000,
            "code_generation": 500,
            "embedding": 1000,
            "vision": 100,
            "audio": 100
        },
        features=["basic_ai_features", "standard_support"],
        priority=1,
        rate_limits={"requests_per_minute": 10}
    ),
    BillingTier.STANDARD: BillingTierConfig(
        tier=BillingTier.STANDARD,
        monthly_price=49.99,
        quota_limits={
            "text_generation": 10000,
            "code_generation": 5000,
            "embedding": 10000,
            "vision": 1000,
            "audio": 1000
        },
        features=["basic_ai_features", "standard_support", "priority_routing"],
        priority=2,
        rate_limits={"requests_per_minute": 60}
    ),
    BillingTier.PREMIUM: BillingTierConfig(
        tier=BillingTier.PREMIUM,
        monthly_price=149.99,
        quota_limits={
            "text_generation": 100000,
            "code_generation": 50000,
            "embedding": 100000,
            "vision": 10000,
            "audio": 10000
        },
        features=["basic_ai_features", "premium_support", "priority_routing", "custom_models"],
        priority=3,
        rate_limits={"requests_per_minute": 300}
    ),
    BillingTier.ENTERPRISE: BillingTierConfig(
        tier=BillingTier.ENTERPRISE,
        monthly_price=499.99,
        quota_limits={
            "text_generation": 1000000,
            "code_generation": 500000,
            "embedding": 1000000,
            "vision": 100000,
            "audio": 100000
        },
        features=["basic_ai_features", "enterprise_support", "priority_routing", "custom_models", "dedicated_support"],
        priority=4,
        rate_limits={"requests_per_minute": 1000},
        custom_limits={
            "max_concurrent_requests": 100,
            "max_batch_size": 1000,
            "custom_model_training": True
        }
    )
}

# Usage tracking settings
USAGE_TRACKING_SETTINGS = {
    "token_estimation_ratio": 4,  # Characters per token for estimation
    "quota_alert_threshold": 0.8,  # Alert when usage reaches 80% of limit
    "summary_update_interval": 300,  # Update summary every 5 minutes
    "retention_days": 90,  # Keep usage records for 90 days
    "export_batch_size": 1000,  # Number of records to export at once
    "metrics_update_interval": 60,  # Update metrics every minute
}

# MongoDB collection names
MONGODB_COLLECTIONS = {
    "usage_records": "usage_records",
    "usage_summaries": "usage_summaries",
    "billing_tiers": "billing_tiers"
}

# API rate limiting settings
RATE_LIMIT_SETTINGS = {
    "window_seconds": 60,  # 1 minute window
    "max_requests_per_window": {
        BillingTier.FREE: 10,
        BillingTier.STANDARD: 60,
        BillingTier.PREMIUM: 300,
        BillingTier.ENTERPRISE: 1000
    }
} 