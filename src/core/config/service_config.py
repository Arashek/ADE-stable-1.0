from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import json
import logging
from dataclasses import dataclass
from enum import Enum
import yaml
from pathlib import Path
import redis
from ..auth.user_management import Organization

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    BETA = "beta"
    DEPRECATED = "deprecated"

@dataclass
class FeatureFlag:
    name: str
    description: str
    status: FeatureStatus
    enabled_for: Set[str]  # Set of organization IDs or subscription tiers
    rollout_percentage: float
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

@dataclass
class GlobalSetting:
    key: str
    value: Any
    description: str
    is_sensitive: bool
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

class ServiceConfig:
    def __init__(self, redis_url: str, config_dir: str):
        self.redis_client = redis.from_url(redis_url)
        self.config_dir = Path(config_dir)
        self._load_configs()
        
    def _load_configs(self):
        """Load configuration files from config directory."""
        self.feature_flags: Dict[str, FeatureFlag] = {}
        self.global_settings: Dict[str, GlobalSetting] = {}
        
        # Load feature flags
        feature_file = self.config_dir / "features.yaml"
        if feature_file.exists():
            with open(feature_file) as f:
                features_data = yaml.safe_load(f)
                for name, data in features_data.items():
                    self.feature_flags[name] = FeatureFlag(
                        name=name,
                        description=data["description"],
                        status=FeatureStatus(data["status"]),
                        enabled_for=set(data["enabled_for"]),
                        rollout_percentage=float(data["rollout_percentage"]),
                        created_at=datetime.fromisoformat(data["created_at"]),
                        updated_at=datetime.fromisoformat(data["updated_at"]),
                        metadata=data.get("metadata", {})
                    )
                    
        # Load global settings
        settings_file = self.config_dir / "settings.yaml"
        if settings_file.exists():
            with open(settings_file) as f:
                settings_data = yaml.safe_load(f)
                for key, data in settings_data.items():
                    self.global_settings[key] = GlobalSetting(
                        key=key,
                        value=data["value"],
                        description=data["description"],
                        is_sensitive=data.get("is_sensitive", False),
                        created_at=datetime.fromisoformat(data["created_at"]),
                        updated_at=datetime.fromisoformat(data["updated_at"]),
                        metadata=data.get("metadata", {})
                    )
                    
    def _save_configs(self):
        """Save configuration to files."""
        # Save feature flags
        features_data = {
            name: {
                "description": flag.description,
                "status": flag.status.value,
                "enabled_for": list(flag.enabled_for),
                "rollout_percentage": flag.rollout_percentage,
                "created_at": flag.created_at.isoformat(),
                "updated_at": flag.updated_at.isoformat(),
                "metadata": flag.metadata
            }
            for name, flag in self.feature_flags.items()
        }
        
        with open(self.config_dir / "features.yaml", "w") as f:
            yaml.dump(features_data, f)
            
        # Save global settings
        settings_data = {
            key: {
                "value": setting.value,
                "description": setting.description,
                "is_sensitive": setting.is_sensitive,
                "created_at": setting.created_at.isoformat(),
                "updated_at": setting.updated_at.isoformat(),
                "metadata": setting.metadata
            }
            for key, setting in self.global_settings.items()
        }
        
        with open(self.config_dir / "settings.yaml", "w") as f:
            yaml.dump(settings_data, f)
            
    def is_feature_enabled(self, feature_name: str,
                         organization: Organization) -> bool:
        """Check if a feature is enabled for an organization."""
        flag = self.feature_flags.get(feature_name)
        if not flag:
            return False
            
        if flag.status == FeatureStatus.DISABLED:
            return False
            
        if flag.status == FeatureStatus.DEPRECATED:
            logger.warning(f"Feature {feature_name} is deprecated")
            return False
            
        # Check if feature is enabled for organization or subscription tier
        if (organization.id in flag.enabled_for or
            organization.subscription_tier in flag.enabled_for):
            return True
            
        # Check rollout percentage
        if flag.rollout_percentage > 0:
            # Use organization ID as deterministic seed
            hash_value = hash(f"{organization.id}:{feature_name}")
            return (hash_value % 100) < flag.rollout_percentage
            
        return False
        
    def get_feature_status(self, feature_name: str) -> Optional[FeatureStatus]:
        """Get current status of a feature."""
        flag = self.feature_flags.get(feature_name)
        return flag.status if flag else None
        
    def update_feature_flag(self, feature_name: str,
                          updates: Dict[str, Any]) -> Optional[FeatureFlag]:
        """Update feature flag configuration."""
        flag = self.feature_flags.get(feature_name)
        if not flag:
            return None
            
        # Update fields
        for key, value in updates.items():
            if hasattr(flag, key):
                setattr(flag, key, value)
                
        flag.updated_at = datetime.utcnow()
        self.feature_flags[feature_name] = flag
        self._save_configs()
        
        return flag
        
    def create_feature_flag(self, name: str, description: str,
                          status: FeatureStatus = FeatureStatus.BETA,
                          enabled_for: Set[str] = None,
                          rollout_percentage: float = 0.0,
                          metadata: Dict[str, Any] = None) -> FeatureFlag:
        """Create a new feature flag."""
        if name in self.feature_flags:
            raise ValueError(f"Feature flag {name} already exists")
            
        now = datetime.utcnow()
        flag = FeatureFlag(
            name=name,
            description=description,
            status=status,
            enabled_for=enabled_for or set(),
            rollout_percentage=rollout_percentage,
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
        
        self.feature_flags[name] = flag
        self._save_configs()
        
        return flag
        
    def get_global_setting(self, key: str) -> Optional[Any]:
        """Get value of a global setting."""
        setting = self.global_settings.get(key)
        return setting.value if setting else None
        
    def update_global_setting(self, key: str, value: Any,
                            description: str = None,
                            is_sensitive: bool = None,
                            metadata: Dict[str, Any] = None) -> Optional[GlobalSetting]:
        """Update or create a global setting."""
        setting = self.global_settings.get(key)
        now = datetime.utcnow()
        
        if setting:
            # Update existing setting
            setting.value = value
            if description is not None:
                setting.description = description
            if is_sensitive is not None:
                setting.is_sensitive = is_sensitive
            if metadata is not None:
                setting.metadata = metadata
            setting.updated_at = now
        else:
            # Create new setting
            setting = GlobalSetting(
                key=key,
                value=value,
                description=description or "",
                is_sensitive=is_sensitive or False,
                created_at=now,
                updated_at=now,
                metadata=metadata or {}
            )
            
        self.global_settings[key] = setting
        self._save_configs()
        
        return setting
        
    def get_organization_features(self, organization: Organization) -> Set[str]:
        """Get all enabled features for an organization."""
        return {
            name for name, flag in self.feature_flags.items()
            if self.is_feature_enabled(name, organization)
        }
        
    def get_feature_metadata(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a feature."""
        flag = self.feature_flags.get(feature_name)
        return flag.metadata if flag else None
        
    def get_setting_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a global setting."""
        setting = self.global_settings.get(key)
        return setting.metadata if setting else None
        
    def cache_feature_status(self, feature_name: str,
                           organization_id: str,
                           is_enabled: bool,
                           ttl: int = 3600):
        """Cache feature status for faster lookups."""
        cache_key = f"feature:{feature_name}:org:{organization_id}"
        self.redis_client.setex(
            cache_key,
            ttl,
            "1" if is_enabled else "0"
        )
        
    def get_cached_feature_status(self, feature_name: str,
                                organization_id: str) -> Optional[bool]:
        """Get cached feature status."""
        cache_key = f"feature:{feature_name}:org:{organization_id}"
        value = self.redis_client.get(cache_key)
        return bool(int(value)) if value is not None else None 