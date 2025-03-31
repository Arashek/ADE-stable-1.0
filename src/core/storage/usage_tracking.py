from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pydantic import BaseModel, Field
from ..auth.pricing_tiers import FeatureFlag, pricing_manager

class UsageMetrics(BaseModel):
    """Tracks usage metrics for a specific feature"""
    current_value: float = 0
    last_reset: datetime = Field(default_factory=datetime.utcnow)
    limit: Optional[float] = None
    period: str = "monthly"  # monthly, yearly, lifetime

class UsageTracker:
    """Tracks and enforces usage limits for different features"""
    
    def __init__(self):
        self._usage: Dict[str, Dict[FeatureFlag, UsageMetrics]] = {}
    
    def initialize_user_usage(self, user_id: str, tier_name: str):
        """Initialize usage tracking for a new user"""
        tier = pricing_manager.get_tier(tier_name)
        if not tier:
            raise ValueError(f"Invalid tier: {tier_name}")
        
        self._usage[user_id] = {}
        for feature, limit in tier.features.items():
            self._usage[user_id][feature] = UsageMetrics(
                limit=limit.value,
                period=limit.period
            )
    
    def get_usage(self, user_id: str, feature: FeatureFlag) -> Optional[UsageMetrics]:
        """Get usage metrics for a specific feature"""
        if user_id not in self._usage:
            return None
        return self._usage[user_id].get(feature)
    
    def increment_usage(self, user_id: str, feature: FeatureFlag, amount: float = 1.0) -> bool:
        """Increment usage for a feature and check if within limits"""
        if user_id not in self._usage:
            return False
        
        metrics = self._usage[user_id].get(feature)
        if not metrics:
            return False
        
        # Check if we need to reset based on period
        self._check_and_reset_period(metrics)
        
        # Check if we're within limits
        if metrics.limit is not None and metrics.current_value + amount > metrics.limit:
            return False
        
        metrics.current_value += amount
        return True
    
    def _check_and_reset_period(self, metrics: UsageMetrics):
        """Check if we need to reset the usage based on the period"""
        now = datetime.utcnow()
        
        if metrics.period == "monthly":
            if now.month != metrics.last_reset.month or now.year != metrics.last_reset.year:
                metrics.current_value = 0
                metrics.last_reset = now
        elif metrics.period == "yearly":
            if now.year != metrics.last_reset.year:
                metrics.current_value = 0
                metrics.last_reset = now
        # lifetime period doesn't need reset
    
    def get_usage_summary(self, user_id: str) -> Dict[FeatureFlag, Dict[str, float]]:
        """Get a summary of all usage metrics for a user"""
        if user_id not in self._usage:
            return {}
        
        summary = {}
        for feature, metrics in self._usage[user_id].items():
            summary[feature] = {
                "current": metrics.current_value,
                "limit": metrics.limit,
                "remaining": metrics.limit - metrics.current_value if metrics.limit else None
            }
        return summary
    
    def reset_usage(self, user_id: str, feature: Optional[FeatureFlag] = None):
        """Reset usage for a feature or all features for a user"""
        if user_id not in self._usage:
            return
        
        if feature:
            if feature in self._usage[user_id]:
                self._usage[user_id][feature].current_value = 0
                self._usage[user_id][feature].last_reset = datetime.utcnow()
        else:
            for metrics in self._usage[user_id].values():
                metrics.current_value = 0
                metrics.last_reset = datetime.utcnow()
    
    def update_tier(self, user_id: str, new_tier: str):
        """Update usage limits when a user changes tiers"""
        tier = pricing_manager.get_tier(new_tier)
        if not tier:
            raise ValueError(f"Invalid tier: {new_tier}")
        
        if user_id not in self._usage:
            self.initialize_user_usage(user_id, new_tier)
            return
        
        # Update limits for existing features
        for feature, limit in tier.features.items():
            if feature in self._usage[user_id]:
                self._usage[user_id][feature].limit = limit.value
                self._usage[user_id][feature].period = limit.period
            else:
                self._usage[user_id][feature] = UsageMetrics(
                    limit=limit.value,
                    period=limit.period
                )
        
        # Remove features that are no longer available
        for feature in list(self._usage[user_id].keys()):
            if feature not in tier.features:
                del self._usage[user_id][feature]

# Global instance for use throughout the application
usage_tracker = UsageTracker() 