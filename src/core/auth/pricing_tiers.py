from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from pydantic import BaseModel, Field

class FeatureFlag(str, Enum):
    """Enumeration of available feature flags"""
    PROJECTS = "projects"
    COMPUTE_HOURS = "compute_hours"
    STORAGE_GB = "storage_gb"
    TEAM_MEMBERS = "team_members"
    API_CALLS = "api_calls"
    CUSTOM_DOMAINS = "custom_domains"
    ADVANCED_ANALYTICS = "advanced_analytics"
    PRIORITY_SUPPORT = "priority_support"
    SSO = "sso"
    AUDIT_LOGS = "audit_logs"

@dataclass
class FeatureLimit:
    """Defines limits for a specific feature"""
    value: int
    period: str = "monthly"  # monthly, yearly, lifetime
    is_hard_limit: bool = True

class PricingTier(BaseModel):
    """Defines a pricing tier with its features and limits"""
    name: str
    description: str
    price: float
    billing_period: str = "monthly"  # monthly, yearly
    features: Dict[FeatureFlag, FeatureLimit] = Field(default_factory=dict)
    trial_days: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PricingTierManager:
    """Manages pricing tiers and feature access"""
    
    def __init__(self):
        self._tiers: Dict[str, PricingTier] = {}
        self._default_tier = "free"
        self._initialize_default_tiers()
    
    def _initialize_default_tiers(self):
        """Initialize default pricing tiers"""
        # Free tier
        self._tiers["free"] = PricingTier(
            name="Free",
            description="Perfect for individual developers",
            price=0,
            features={
                FeatureFlag.PROJECTS: FeatureLimit(3),
                FeatureFlag.COMPUTE_HOURS: FeatureLimit(50),
                FeatureFlag.STORAGE_GB: FeatureLimit(5),
                FeatureFlag.API_CALLS: FeatureLimit(1000),
            }
        )
        
        # Professional tier
        self._tiers["professional"] = PricingTier(
            name="Professional",
            description="For professional developers and small teams",
            price=29.99,
            features={
                FeatureFlag.PROJECTS: FeatureLimit(10),
                FeatureFlag.COMPUTE_HOURS: FeatureLimit(200),
                FeatureFlag.STORAGE_GB: FeatureLimit(20),
                FeatureFlag.API_CALLS: FeatureLimit(5000),
                FeatureFlag.CUSTOM_DOMAINS: FeatureLimit(1),
                FeatureFlag.ADVANCED_ANALYTICS: FeatureLimit(1),
            }
        )
        
        # Team tier
        self._tiers["team"] = PricingTier(
            name="Team",
            description="For growing teams and organizations",
            price=99.99,
            features={
                FeatureFlag.PROJECTS: FeatureLimit(30),
                FeatureFlag.COMPUTE_HOURS: FeatureLimit(1000),
                FeatureFlag.STORAGE_GB: FeatureLimit(100),
                FeatureFlag.API_CALLS: FeatureLimit(20000),
                FeatureFlag.TEAM_MEMBERS: FeatureLimit(5),
                FeatureFlag.CUSTOM_DOMAINS: FeatureLimit(3),
                FeatureFlag.ADVANCED_ANALYTICS: FeatureLimit(1),
                FeatureFlag.PRIORITY_SUPPORT: FeatureLimit(1),
            }
        )
        
        # Enterprise tier
        self._tiers["enterprise"] = PricingTier(
            name="Enterprise",
            description="For large organizations with custom needs",
            price=299.99,
            features={
                FeatureFlag.PROJECTS: FeatureLimit(100),
                FeatureFlag.COMPUTE_HOURS: FeatureLimit(5000),
                FeatureFlag.STORAGE_GB: FeatureLimit(500),
                FeatureFlag.API_CALLS: FeatureLimit(100000),
                FeatureFlag.TEAM_MEMBERS: FeatureLimit(20),
                FeatureFlag.CUSTOM_DOMAINS: FeatureLimit(10),
                FeatureFlag.ADVANCED_ANALYTICS: FeatureLimit(1),
                FeatureFlag.PRIORITY_SUPPORT: FeatureLimit(1),
                FeatureFlag.SSO: FeatureLimit(1),
                FeatureFlag.AUDIT_LOGS: FeatureLimit(1),
            }
        )
    
    def get_tier(self, tier_name: str) -> Optional[PricingTier]:
        """Get a pricing tier by name"""
        return self._tiers.get(tier_name)
    
    def get_all_tiers(self) -> List[PricingTier]:
        """Get all available pricing tiers"""
        return list(self._tiers.values())
    
    def create_tier(self, tier: PricingTier) -> bool:
        """Create a new pricing tier"""
        if tier.name.lower() in self._tiers:
            return False
        self._tiers[tier.name.lower()] = tier
        return True
    
    def update_tier(self, tier_name: str, tier: PricingTier) -> bool:
        """Update an existing pricing tier"""
        if tier_name.lower() not in self._tiers:
            return False
        self._tiers[tier_name.lower()] = tier
        return True
    
    def delete_tier(self, tier_name: str) -> bool:
        """Delete a pricing tier"""
        if tier_name.lower() == self._default_tier:
            return False
        return bool(self._tiers.pop(tier_name.lower(), None))
    
    def check_feature_access(self, tier_name: str, feature: FeatureFlag) -> bool:
        """Check if a tier has access to a specific feature"""
        tier = self.get_tier(tier_name)
        if not tier:
            return False
        return feature in tier.features
    
    def get_feature_limit(self, tier_name: str, feature: FeatureFlag) -> Optional[FeatureLimit]:
        """Get the limit for a specific feature in a tier"""
        tier = self.get_tier(tier_name)
        if not tier:
            return None
        return tier.features.get(feature)
    
    def get_upgrade_path(self, current_tier: str) -> List[PricingTier]:
        """Get available upgrade paths from current tier"""
        current_price = self._tiers[current_tier].price
        return [
            tier for tier in self._tiers.values()
            if tier.price > current_price and tier.is_active
        ]
    
    def get_downgrade_path(self, current_tier: str) -> List[PricingTier]:
        """Get available downgrade paths from current tier"""
        current_price = self._tiers[current_tier].price
        return [
            tier for tier in self._tiers.values()
            if tier.price < current_price and tier.is_active
        ]

# Global instance for use throughout the application
pricing_manager = PricingTierManager() 