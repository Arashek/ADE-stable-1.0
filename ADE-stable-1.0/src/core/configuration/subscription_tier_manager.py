from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta
import json
import threading
from pathlib import Path
import yaml
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TierCapability:
    """Represents a capability available in a subscription tier."""
    def __init__(self, name: str, description: str, quota: Optional[int] = None):
        self.name = name
        self.description = description
        self.quota = quota

class TierStatus(Enum):
    """Subscription tier status."""
    ACTIVE = "active"
    TRIAL = "trial"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"

@dataclass
class TierQuota:
    """Represents quota limits for a subscription tier."""
    name: str
    limit: int
    period: str  # daily, monthly, yearly
    reset_on: str  # period_start, custom_date
    custom_reset_date: Optional[datetime] = None

@dataclass
class TierUpgradePath:
    """Represents an upgrade path between tiers."""
    from_tier: str
    to_tier: str
    proration_type: str  # full, partial, none
    grace_period_days: int = 0
    auto_upgrade: bool = False
    conditions: List[Dict[str, Any]] = None

@dataclass
class SubscriptionTier:
    """Represents a subscription tier with its capabilities and limits."""
    name: str
    description: str
    price: float
    billing_period: str  # monthly, yearly
    capabilities: List[TierCapability]
    quotas: List[TierQuota]
    upgrade_paths: List[TierUpgradePath]
    downgrade_paths: List[TierUpgradePath]
    trial_period_days: int = 0
    features: List[str] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class SubscriptionUsage:
    """Tracks usage of tier quotas."""
    tier_name: str
    quota_name: str
    current_usage: int
    last_reset: datetime
    next_reset: datetime

class SubscriptionError(Exception):
    """Base class for subscription errors."""
    pass

class QuotaExceededError(SubscriptionError):
    """Raised when a quota limit is exceeded."""
    pass

class TierNotFoundError(SubscriptionError):
    """Raised when a tier is not found."""
    pass

class InvalidUpgradeError(SubscriptionError):
    """Raised when an upgrade path is invalid."""
    pass

class SubscriptionTierManager:
    """Manages subscription tiers, quotas, and trial periods."""
    
    def __init__(self, tiers_dir: str):
        self.tiers_dir = Path(tiers_dir)
        self._tiers: Dict[str, SubscriptionTier] = {}
        self._usage: Dict[str, Dict[str, SubscriptionUsage]] = defaultdict(dict)
        self._lock = threading.Lock()
        self._load_tiers()
        
    def _load_tiers(self) -> None:
        """Load subscription tiers from files."""
        for file in self.tiers_dir.glob("*.yaml"):
            try:
                with open(file) as f:
                    data = yaml.safe_load(f)
                    tier = self._create_tier(data)
                    self._tiers[tier.name] = tier
            except Exception as e:
                logger.error(f"Failed to load subscription tier from {file}: {str(e)}")
                
    def _create_tier(self, data: Dict[str, Any]) -> SubscriptionTier:
        """Create subscription tier from data."""
        capabilities = [
            TierCapability(
                name=cap["name"],
                description=cap.get("description", ""),
                quota=cap.get("quota")
            )
            for cap in data.get("capabilities", [])
        ]
        
        quotas = [
            TierQuota(
                name=quota["name"],
                limit=quota["limit"],
                period=quota["period"],
                reset_on=quota["reset_on"],
                custom_reset_date=datetime.fromisoformat(quota["custom_reset_date"])
                if quota.get("custom_reset_date") else None
            )
            for quota in data.get("quotas", [])
        ]
        
        upgrade_paths = [
            TierUpgradePath(
                from_tier=path["from_tier"],
                to_tier=path["to_tier"],
                proration_type=path["proration_type"],
                grace_period_days=path.get("grace_period_days", 0),
                auto_upgrade=path.get("auto_upgrade", False),
                conditions=path.get("conditions", [])
            )
            for path in data.get("upgrade_paths", [])
        ]
        
        downgrade_paths = [
            TierUpgradePath(
                from_tier=path["from_tier"],
                to_tier=path["to_tier"],
                proration_type=path["proration_type"],
                grace_period_days=path.get("grace_period_days", 0),
                auto_upgrade=path.get("auto_upgrade", False),
                conditions=path.get("conditions", [])
            )
            for path in data.get("downgrade_paths", [])
        ]
        
        return SubscriptionTier(
            name=data["name"],
            description=data.get("description", ""),
            price=data["price"],
            billing_period=data["billing_period"],
            capabilities=capabilities,
            quotas=quotas,
            upgrade_paths=upgrade_paths,
            downgrade_paths=downgrade_paths,
            trial_period_days=data.get("trial_period_days", 0),
            features=data.get("features", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )
        
    def _save_tier(self, tier: SubscriptionTier) -> None:
        """Save subscription tier to file."""
        file_path = self.tiers_dir / f"{tier.name}.yaml"
        with open(file_path, "w") as f:
            yaml.dump({
                "name": tier.name,
                "description": tier.description,
                "price": tier.price,
                "billing_period": tier.billing_period,
                "capabilities": [
                    {
                        "name": cap.name,
                        "description": cap.description,
                        "quota": cap.quota
                    }
                    for cap in tier.capabilities
                ],
                "quotas": [
                    {
                        "name": quota.name,
                        "limit": quota.limit,
                        "period": quota.period,
                        "reset_on": quota.reset_on,
                        "custom_reset_date": quota.custom_reset_date.isoformat()
                        if quota.custom_reset_date else None
                    }
                    for quota in tier.quotas
                ],
                "upgrade_paths": [
                    {
                        "from_tier": path.from_tier,
                        "to_tier": path.to_tier,
                        "proration_type": path.proration_type,
                        "grace_period_days": path.grace_period_days,
                        "auto_upgrade": path.auto_upgrade,
                        "conditions": path.conditions
                    }
                    for path in tier.upgrade_paths
                ],
                "downgrade_paths": [
                    {
                        "from_tier": path.from_tier,
                        "to_tier": path.to_tier,
                        "proration_type": path.proration_type,
                        "grace_period_days": path.grace_period_days,
                        "auto_upgrade": path.auto_upgrade,
                        "conditions": path.conditions
                    }
                    for path in tier.downgrade_paths
                ],
                "trial_period_days": tier.trial_period_days,
                "features": tier.features,
                "metadata": tier.metadata,
                "created_at": tier.created_at.isoformat(),
                "updated_at": tier.updated_at.isoformat()
            }, f)
            
    def create_tier(self, tier_data: Dict[str, Any]) -> SubscriptionTier:
        """Create new subscription tier."""
        with self._lock:
            tier = self._create_tier(tier_data)
            if tier.name in self._tiers:
                raise SubscriptionError(f"Tier already exists: {tier.name}")
                
            self._tiers[tier.name] = tier
            self._save_tier(tier)
            return tier
            
    def update_tier(self, name: str, updates: Dict[str, Any]) -> SubscriptionTier:
        """Update subscription tier."""
        with self._lock:
            tier = self._tiers.get(name)
            if not tier:
                raise TierNotFoundError(f"Tier not found: {name}")
                
            # Update tier attributes
            for key, value in updates.items():
                if hasattr(tier, key):
                    setattr(tier, key, value)
                    
            tier.updated_at = datetime.now()
            self._save_tier(tier)
            return tier
            
    def delete_tier(self, name: str) -> None:
        """Delete subscription tier."""
        with self._lock:
            if name not in self._tiers:
                raise TierNotFoundError(f"Tier not found: {name}")
                
            # Check if tier is in use
            for usage in self._usage.values():
                if any(u.tier_name == name for u in usage.values()):
                    raise SubscriptionError(f"Cannot delete tier {name} as it is in use")
                    
            del self._tiers[name]
            (self.tiers_dir / f"{name}.yaml").unlink()
            
    def get_tier(self, name: str) -> Optional[SubscriptionTier]:
        """Get subscription tier by name."""
        return self._tiers.get(name)
        
    def get_tier_capabilities(self, name: str) -> List[TierCapability]:
        """Get capabilities for a tier."""
        tier = self.get_tier(name)
        if not tier:
            raise TierNotFoundError(f"Tier not found: {name}")
        return tier.capabilities
        
    def check_quota(self, tier_name: str, quota_name: str, amount: int = 1) -> bool:
        """Check if quota usage would exceed limit."""
        with self._lock:
            tier = self.get_tier(tier_name)
            if not tier:
                raise TierNotFoundError(f"Tier not found: {tier_name}")
                
            quota = next((q for q in tier.quotas if q.name == quota_name), None)
            if not quota:
                return True  # No quota defined
                
            usage = self._usage.get(tier_name, {}).get(quota_name)
            if not usage:
                return amount <= quota.limit
                
            # Check if quota needs reset
            if datetime.now() >= usage.next_reset:
                return amount <= quota.limit
                
            return (usage.current_usage + amount) <= quota.limit
            
    def increment_quota(self, tier_name: str, quota_name: str, amount: int = 1) -> None:
        """Increment quota usage."""
        with self._lock:
            tier = self.get_tier(tier_name)
            if not tier:
                raise TierNotFoundError(f"Tier not found: {tier_name}")
                
            quota = next((q for q in tier.quotas if q.name == quota_name), None)
            if not quota:
                return  # No quota defined
                
            usage = self._usage.get(tier_name, {}).get(quota_name)
            if not usage:
                usage = SubscriptionUsage(
                    tier_name=tier_name,
                    quota_name=quota_name,
                    current_usage=0,
                    last_reset=datetime.now(),
                    next_reset=self._calculate_next_reset(quota)
                )
                self._usage[tier_name][quota_name] = usage
                
            # Check if quota needs reset
            if datetime.now() >= usage.next_reset:
                usage.current_usage = 0
                usage.last_reset = datetime.now()
                usage.next_reset = self._calculate_next_reset(quota)
                
            if (usage.current_usage + amount) > quota.limit:
                raise QuotaExceededError(f"Quota limit exceeded for {quota_name}")
                
            usage.current_usage += amount
            
    def _calculate_next_reset(self, quota: TierQuota) -> datetime:
        """Calculate next quota reset date."""
        now = datetime.now()
        
        if quota.reset_on == "period_start":
            if quota.period == "daily":
                return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif quota.period == "monthly":
                if now.month == 12:
                    return now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                return now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            elif quota.period == "yearly":
                return now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif quota.reset_on == "custom_date" and quota.custom_reset_date:
            next_reset = quota.custom_reset_date
            while next_reset <= now:
                if quota.period == "daily":
                    next_reset += timedelta(days=1)
                elif quota.period == "monthly":
                    if next_reset.month == 12:
                        next_reset = next_reset.replace(year=next_reset.year + 1, month=1)
                    else:
                        next_reset = next_reset.replace(month=next_reset.month + 1)
                elif quota.period == "yearly":
                    next_reset = next_reset.replace(year=next_reset.year + 1)
            return next_reset
            
        return now + timedelta(days=1)  # Default to daily reset
        
    def get_upgrade_paths(self, tier_name: str) -> List[TierUpgradePath]:
        """Get available upgrade paths for a tier."""
        tier = self.get_tier(tier_name)
        if not tier:
            raise TierNotFoundError(f"Tier not found: {tier_name}")
        return tier.upgrade_paths
        
    def get_downgrade_paths(self, tier_name: str) -> List[TierUpgradePath]:
        """Get available downgrade paths for a tier."""
        tier = self.get_tier(tier_name)
        if not tier:
            raise TierNotFoundError(f"Tier not found: {tier_name}")
        return tier.downgrade_paths
        
    def validate_upgrade(self, from_tier: str, to_tier: str) -> bool:
        """Validate if upgrade path exists and conditions are met."""
        from_tier_obj = self.get_tier(from_tier)
        if not from_tier_obj:
            raise TierNotFoundError(f"Source tier not found: {from_tier}")
            
        to_tier_obj = self.get_tier(to_tier)
        if not to_tier_obj:
            raise TierNotFoundError(f"Target tier not found: {to_tier}")
            
        upgrade_path = next(
            (path for path in from_tier_obj.upgrade_paths if path.to_tier == to_tier),
            None
        )
        
        if not upgrade_path:
            raise InvalidUpgradeError(f"No upgrade path from {from_tier} to {to_tier}")
            
        # Check conditions if any
        if upgrade_path.conditions:
            # TODO: Implement condition evaluation
            pass
            
        return True
        
    def get_trial_status(self, tier_name: str, start_date: datetime) -> Dict[str, Any]:
        """Get trial status for a tier."""
        tier = self.get_tier(tier_name)
        if not tier:
            raise TierNotFoundError(f"Tier not found: {tier_name}")
            
        if tier.trial_period_days == 0:
            return {"has_trial": False}
            
        trial_end = start_date + timedelta(days=tier.trial_period_days)
        now = datetime.now()
        
        return {
            "has_trial": True,
            "trial_days": tier.trial_period_days,
            "trial_start": start_date,
            "trial_end": trial_end,
            "is_active": now <= trial_end,
            "days_remaining": (trial_end - now).days if now <= trial_end else 0
        }
        
    def get_tier_usage(self, tier_name: str) -> Dict[str, Any]:
        """Get usage statistics for a tier."""
        tier = self.get_tier(tier_name)
        if not tier:
            raise TierNotFoundError(f"Tier not found: {tier_name}")
            
        usage_data = {}
        for quota in tier.quotas:
            usage = self._usage.get(tier_name, {}).get(quota.name)
            if usage:
                usage_data[quota.name] = {
                    "current_usage": usage.current_usage,
                    "limit": quota.limit,
                    "last_reset": usage.last_reset,
                    "next_reset": usage.next_reset
                }
                
        return usage_data 