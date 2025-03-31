from typing import Dict, Any, Optional, List, Set, Union, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
import json
import threading
from pathlib import Path
import yaml
from collections import defaultdict
import functools
import time
import re
from typing import TypeVar, Generic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

class CacheEntry(Generic[T]):
    """Cache entry with expiration."""
    def __init__(self, value: T, expires_at: float):
        self.value = value
        self.expires_at = expires_at

class CacheStrategy(Enum):
    """Cache strategy types."""
    TTL = "ttl"
    LRU = "lru"
    HYBRID = "hybrid"

class CacheStats:
    """Cache statistics."""
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.size = 0

class LRUCacheEntry(Generic[T]):
    """LRU cache entry with access tracking."""
    def __init__(self, value: T, expires_at: float):
        self.value = value
        self.expires_at = expires_at
        self.last_access = time.time()
        self.access_count = 0

class FeatureStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    ROLLING_OUT = "rolling_out"
    DEPRECATED = "deprecated"

@dataclass
class FeatureFlag:
    """Represents a feature flag with its configuration."""
    name: str
    description: str
    status: FeatureStatus
    created_at: datetime
    updated_at: datetime
    dependencies: List[str]
    rollout_percentage: int = 0
    tenant_overrides: Dict[str, bool] = None
    user_overrides: Dict[str, bool] = None
    conditions: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    group: Optional[str] = None
    tags: List[str] = None
    validation_rules: List[Dict[str, Any]] = None
    tier_requirements: Dict[str, Any] = None
    ab_test: Optional[str] = None
    time_rule: Optional[str] = None

@dataclass
class FeatureFlagTemplate:
    """Represents a feature flag template."""
    name: str
    description: str
    base_config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = None
    validation_rules: List[Dict[str, Any]] = None

@dataclass
class ABTestVariant:
    """Represents an A/B test variant."""
    name: str
    weight: float  # 0-1, represents percentage of traffic
    config: Dict[str, Any]
    metadata: Dict[str, Any] = None

@dataclass
class ABTest:
    """Represents an A/B test configuration."""
    name: str
    description: str
    variants: List[ABTestVariant]
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"  # active, completed, paused
    metrics: List[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class TimeBasedRule:
    """Represents a time-based activation rule."""
    name: str
    schedule: Dict[str, Any]  # cron expression or time windows
    timezone: str
    enabled: bool = True
    metadata: Dict[str, Any] = None

@dataclass
class ABTestMetrics:
    """Represents A/B test metrics."""
    test_name: str
    variant_name: str
    impressions: int = 0
    conversions: int = 0
    revenue: float = 0.0
    custom_metrics: Dict[str, float] = None
    last_updated: datetime = None

class FeatureFlagError(Exception):
    """Base class for feature flag errors."""
    pass

class FeatureFlagNotFoundError(FeatureFlagError):
    """Raised when a feature flag is not found."""
    pass

class FeatureFlagValidationError(FeatureFlagError):
    """Raised when feature flag validation fails."""
    pass

class FeatureFlagDependencyError(FeatureFlagError):
    """Raised when feature flag dependencies are not met."""
    pass

class FeatureFlagContext:
    """Context for feature flag evaluation."""
    
    def __init__(
        self,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        environment: Optional[str] = None,
        **kwargs
    ):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.environment = environment
        self.attributes = kwargs
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "environment": self.environment,
            **self.attributes
        }

class FeatureFlagEvaluator:
    """Evaluates feature flags based on context and conditions."""
    
    def __init__(self, cache_strategy: CacheStrategy = CacheStrategy.HYBRID, max_size: int = 1000):
        self._operators = {
            # Basic comparison
            "eq": lambda x, y: x == y,
            "ne": lambda x, y: x != y,
            "gt": lambda x, y: x > y,
            "lt": lambda x, y: x < y,
            "gte": lambda x, y: x >= y,
            "lte": lambda x, y: x <= y,
            
            # Collection operations
            "in": lambda x, y: x in y,
            "nin": lambda x, y: x not in y,
            "contains": lambda x, y: y in x,
            "subset": lambda x, y: set(x).issubset(set(y)),
            "superset": lambda x, y: set(x).issuperset(set(y)),
            "intersects": lambda x, y: bool(set(x) & set(y)),
            
            # String operations
            "startswith": lambda x, y: x.startswith(y),
            "endswith": lambda x, y: x.endswith(y),
            "matches": lambda x, y: bool(re.match(y, x)),
            "contains_any": lambda x, y: any(item in x for item in y),
            "contains_all": lambda x, y: all(item in x for item in y),
            
            # Numeric operations
            "between": lambda x, y: y[0] <= x <= y[1],
            "mod": lambda x, y: x % y[0] == y[1],
            "range": lambda x, y: y[0] <= x <= y[1],
            
            # Date operations
            "before": lambda x, y: x < datetime.fromisoformat(y),
            "after": lambda x, y: x > datetime.fromisoformat(y),
            "between_dates": lambda x, y: y[0] <= x <= y[1],
            
            # Custom operations
            "custom": lambda x, y: y(x) if callable(y) else False
        }
        self._cache: Dict[str, Union[CacheEntry[bool], LRUCacheEntry[bool]]] = {}
        self._cache_lock = threading.Lock()
        self._cache_ttl = 300  # 5 minutes default TTL
        self._cache_strategy = cache_strategy
        self._max_size = max_size
        self._stats = CacheStats()
        
    def set_cache_strategy(self, strategy: CacheStrategy) -> None:
        """Set cache strategy."""
        with self._cache_lock:
            self._cache_strategy = strategy
            self.clear_cache()
            
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self._cache_lock:
            return {
                "hits": self._stats.hits,
                "misses": self._stats.misses,
                "evictions": self._stats.evictions,
                "size": len(self._cache)
            }
            
    def _evict_entries(self) -> None:
        """Evict entries based on strategy."""
        if self._cache_strategy == CacheStrategy.TTL:
            current_time = time.time()
            expired = [
                key for key, entry in self._cache.items()
                if isinstance(entry, CacheEntry) and current_time >= entry.expires_at
            ]
            for key in expired:
                del self._cache[key]
                self._stats.evictions += 1
                
        elif self._cache_strategy == CacheStrategy.LRU:
            if len(self._cache) > self._max_size:
                # Sort by last access and remove oldest entries
                sorted_entries = sorted(
                    self._cache.items(),
                    key=lambda x: x[1].last_access if isinstance(x[1], LRUCacheEntry) else float('inf')
                )
                entries_to_remove = len(self._cache) - self._max_size
                for key, _ in sorted_entries[:entries_to_remove]:
                    del self._cache[key]
                    self._stats.evictions += 1
                    
        elif self._cache_strategy == CacheStrategy.HYBRID:
            current_time = time.time()
            # Remove expired entries
            expired = [
                key for key, entry in self._cache.items()
                if current_time >= entry.expires_at
            ]
            for key in expired:
                del self._cache[key]
                self._stats.evictions += 1
                
            # If still over size limit, remove oldest entries
            if len(self._cache) > self._max_size:
                sorted_entries = sorted(
                    self._cache.items(),
                    key=lambda x: x[1].last_access if isinstance(x[1], LRUCacheEntry) else float('inf')
                )
                entries_to_remove = len(self._cache) - self._max_size
                for key, _ in sorted_entries[:entries_to_remove]:
                    del self._cache[key]
                    self._stats.evictions += 1
                    
    def _get_cache_key(self, condition: Dict[str, Any], context: FeatureFlagContext) -> str:
        """Generate cache key for condition evaluation."""
        return f"{json.dumps(condition, sort_keys=True)}:{json.dumps(context.to_dict(), sort_keys=True)}"
        
    def evaluate_condition(self, condition: Dict[str, Any], context: FeatureFlagContext) -> bool:
        """Evaluate a single condition against context with enhanced caching."""
        cache_key = self._get_cache_key(condition, context)
        
        with self._cache_lock:
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                current_time = time.time()
                
                # Check if entry is expired
                if current_time >= entry.expires_at:
                    del self._cache[cache_key]
                    self._stats.misses += 1
                else:
                    if isinstance(entry, LRUCacheEntry):
                        entry.last_access = current_time
                        entry.access_count += 1
                    self._stats.hits += 1
                    return entry.value
                    
            self._stats.misses += 1
            
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")
        
        if not all([field, operator, value]):
            return False
            
        if operator not in self._operators:
            return False
            
        context_value = getattr(context, field, context.attributes.get(field))
        if context_value is None:
            return False
            
        result = self._operators[operator](context_value, value)
        
        with self._cache_lock:
            # Create appropriate cache entry based on strategy
            if self._cache_strategy == CacheStrategy.TTL:
                entry = CacheEntry(result, time.time() + self._cache_ttl)
            else:
                entry = LRUCacheEntry(result, time.time() + self._cache_ttl)
                
            self._cache[cache_key] = entry
            self._evict_entries()
            
        return result
        
    def evaluate_conditions(self, conditions: List[Dict[str, Any]], context: FeatureFlagContext) -> bool:
        """Evaluate multiple conditions against context."""
        if not conditions:
            return True
            
        return all(self.evaluate_condition(condition, context) for condition in conditions)

class FeatureFlagGroup:
    """Represents a group of feature flags."""
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.flags: Set[str] = set()
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

class ValidationRule:
    """Represents a validation rule for feature flags."""
    def __init__(self, rule_type: str, parameters: Dict[str, Any]):
        self.rule_type = rule_type
        self.parameters = parameters

class FeatureFlagService:
    """Service for managing feature flags."""
    
    def __init__(self, flags_dir: str, tier_manager: Optional['SubscriptionTierManager'] = None):
        self.flags_dir = Path(flags_dir)
        self._flags: Dict[str, FeatureFlag] = {}
        self._dependencies: Dict[str, Set[str]] = defaultdict(set)
        self._groups: Dict[str, FeatureFlagGroup] = {}
        self._lock = threading.Lock()
        self._evaluator = FeatureFlagEvaluator()
        self._validation_rules = {
            "required_fields": self._validate_required_fields,
            "format_check": self._validate_format,
            "dependency_check": self._validate_dependencies,
            "conflict_check": self._validate_conflicts,
            "custom_rule": self._validate_custom_rule,
            "value_range": self._validate_value_range,
            "enum_check": self._validate_enum,
            "regex_check": self._validate_regex,
            "date_check": self._validate_date,
            "unique_check": self._validate_unique,
            "relationship_check": self._validate_relationship
        }
        self._templates: Dict[str, FeatureFlagTemplate] = {}
        self._tier_manager = tier_manager
        self._ab_tests: Dict[str, ABTest] = {}
        self._time_rules: Dict[str, TimeBasedRule] = {}
        self._ab_test_metrics: Dict[str, Dict[str, ABTestMetrics]] = {}
        self._load_flags()
        self._load_groups()
        self._load_templates()
        self._load_ab_tests()
        self._load_time_rules()
        self._load_ab_test_metrics()
        
    def _load_flags(self) -> None:
        """Load feature flags from files."""
        for file in self.flags_dir.glob("*.yaml"):
            try:
                with open(file) as f:
                    data = yaml.safe_load(f)
                    flag = self._create_flag(data)
                    self._flags[flag.name] = flag
                    self._update_dependencies(flag)
            except Exception as e:
                logger.error(f"Failed to load feature flag from {file}: {str(e)}")
                
    def _create_flag(self, data: Dict[str, Any]) -> FeatureFlag:
        """Create feature flag from data with enhanced support."""
        # Check for template inheritance
        template_name = data.get("metadata", {}).get("template")
        if template_name:
            template = self._templates.get(template_name)
            if template:
                # Merge template validation rules
                validation_rules = data.get("validation_rules", [])
                if template.validation_rules:
                    validation_rules.extend(template.validation_rules)
                data["validation_rules"] = validation_rules
                
        # Add subscription tier support
        tier_requirements = data.get("tier_requirements", {})
        if self._tier_manager:
            for tier_name in tier_requirements.get("required_tiers", []):
                if not self._tier_manager.get_tier(tier_name):
                    raise FeatureFlagValidationError(f"Invalid required tier: {tier_name}")
                    
        # Add A/B test support
        ab_test = data.get("ab_test")
        if ab_test and ab_test not in self._ab_tests:
            raise FeatureFlagValidationError(f"Invalid A/B test: {ab_test}")
            
        # Add time-based rule support
        time_rule = data.get("time_rule")
        if time_rule and time_rule not in self._time_rules:
            raise FeatureFlagValidationError(f"Invalid time-based rule: {time_rule}")
            
        return FeatureFlag(
            name=data["name"],
            description=data.get("description", ""),
            status=FeatureStatus(data.get("status", "disabled")),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
            dependencies=data.get("dependencies", []),
            rollout_percentage=data.get("rollout_percentage", 0),
            tenant_overrides=data.get("tenant_overrides", {}),
            user_overrides=data.get("user_overrides", {}),
            conditions=data.get("conditions", []),
            metadata=data.get("metadata", {}),
            group=data.get("group"),
            tags=data.get("tags", []),
            validation_rules=data.get("validation_rules", []),
            tier_requirements=tier_requirements,
            ab_test=ab_test,
            time_rule=time_rule
        )
        
    def _update_dependencies(self, flag: FeatureFlag) -> None:
        """Update dependency graph."""
        for dep in flag.dependencies:
            self._dependencies[flag.name].add(dep)
            
    def create_flag(self, flag_data: Dict[str, Any]) -> FeatureFlag:
        """Create new feature flag."""
        with self._lock:
            flag = self._create_flag(flag_data)
            self._validate_flag(flag)
            self._flags[flag.name] = flag
            self._update_dependencies(flag)
            self._save_flag(flag)
            return flag
            
    def _validate_flag(self, flag: FeatureFlag) -> None:
        """Validate feature flag."""
        if not flag.name:
            raise FeatureFlagValidationError("Feature flag name is required")
            
        if flag.rollout_percentage < 0 or flag.rollout_percentage > 100:
            raise FeatureFlagValidationError("Rollout percentage must be between 0 and 100")
            
        # Check for circular dependencies
        self._check_circular_dependencies(flag.name)
        
        # Apply validation rules
        for rule in flag.validation_rules:
            rule_type = rule.get("type")
            if rule_type in self._validation_rules:
                self._validation_rules[rule_type](flag, ValidationRule(rule_type, rule.get("parameters", {})))
                
    def _check_circular_dependencies(self, flag_name: str, visited: Set[str] = None) -> None:
        """Check for circular dependencies."""
        if visited is None:
            visited = set()
            
        if flag_name in visited:
            raise FeatureFlagValidationError(f"Circular dependency detected for flag: {flag_name}")
            
        visited.add(flag_name)
        for dep in self._dependencies[flag_name]:
            self._check_circular_dependencies(dep, visited.copy())
            
    def _save_flag(self, flag: FeatureFlag) -> None:
        """Save feature flag to file."""
        file_path = self.flags_dir / f"{flag.name}.yaml"
        with open(file_path, "w") as f:
            yaml.dump({
                "name": flag.name,
                "description": flag.description,
                "status": flag.status.value,
                "created_at": flag.created_at.isoformat(),
                "updated_at": flag.updated_at.isoformat(),
                "dependencies": flag.dependencies,
                "rollout_percentage": flag.rollout_percentage,
                "tenant_overrides": flag.tenant_overrides,
                "user_overrides": flag.user_overrides,
                "conditions": flag.conditions,
                "metadata": flag.metadata,
                "group": flag.group,
                "tags": flag.tags,
                "validation_rules": flag.validation_rules,
                "tier_requirements": flag.tier_requirements,
                "ab_test": flag.ab_test,
                "time_rule": flag.time_rule
            }, f)
            
    def get_flag(self, name: str) -> Optional[FeatureFlag]:
        """Get feature flag by name."""
        return self._flags.get(name)
        
    def update_flag(self, name: str, updates: Dict[str, Any]) -> FeatureFlag:
        """Update feature flag."""
        with self._lock:
            flag = self.get_flag(name)
            if not flag:
                raise FeatureFlagNotFoundError(f"Feature flag not found: {name}")
                
            # Update flag attributes
            for key, value in updates.items():
                if hasattr(flag, key):
                    setattr(flag, key, value)
                    
            flag.updated_at = datetime.now()
            self._validate_flag(flag)
            self._save_flag(flag)
            return flag
            
    def delete_flag(self, name: str) -> None:
        """Delete feature flag."""
        with self._lock:
            flag = self.get_flag(name)
            if not flag:
                raise FeatureFlagNotFoundError(f"Feature flag not found: {name}")
                
            # Check if flag is a dependency
            for other_flag in self._flags.values():
                if name in other_flag.dependencies:
                    raise FeatureFlagValidationError(
                        f"Cannot delete flag {name} as it is a dependency for {other_flag.name}"
                    )
                    
            del self._flags[name]
            del self._dependencies[name]
            (self.flags_dir / f"{name}.yaml").unlink()
            
    def is_enabled(self, name: str, context: FeatureFlagContext) -> bool:
        """Check if feature flag is enabled for context with enhanced checks."""
        flag = self.get_flag(name)
        if not flag:
            raise FeatureFlagNotFoundError(f"Feature flag not found: {name}")
            
        # Check subscription tier requirements
        if flag.tier_requirements and self._tier_manager:
            required_tiers = flag.tier_requirements.get("required_tiers", [])
            if required_tiers:
                # Get user's subscription tier
                user_tier = self._tier_manager.get_user_tier(context.user_id)
                if not user_tier or user_tier.name not in required_tiers:
                    return False
                    
        # Check A/B test
        if flag.ab_test:
            test = self._ab_tests.get(flag.ab_test)
            if test and test.status == "active":
                if test.start_date <= datetime.now() <= (test.end_date or datetime.max):
                    variant = self.get_ab_test_variant(flag.ab_test, context)
                    if variant:
                        # Track impression
                        self.track_ab_test_impression(flag.ab_test, variant.name)
                        # Apply variant config
                        for key, value in variant.config.items():
                            if hasattr(flag, key):
                                setattr(flag, key, value)
                                
        # Check time-based rule
        if flag.time_rule:
            rule = self._time_rules.get(flag.time_rule)
            if rule and not self._evaluate_time_rule(rule):
                return False
                
        # Check status
        if flag.status == FeatureStatus.DISABLED:
            return False
        if flag.status == FeatureStatus.ENABLED:
            return True
            
        # Check tenant override
        if context.tenant_id and context.tenant_id in flag.tenant_overrides:
            return flag.tenant_overrides[context.tenant_id]
            
        # Check user override
        if context.user_id and context.user_id in flag.user_overrides:
            return flag.user_overrides[context.user_id]
            
        # Check dependencies
        for dep in flag.dependencies:
            if not self.is_enabled(dep, context):
                return False
                
        # Check conditions
        if flag.conditions:
            if not self._evaluator.evaluate_conditions(flag.conditions, context):
                return False
                
        # Check rollout percentage
        if flag.rollout_percentage > 0:
            # Use tenant_id or user_id for consistent hashing
            hash_value = hash(context.tenant_id or context.user_id or "")
            return (hash_value % 100) < flag.rollout_percentage
            
        return False
        
    def get_enabled_flags(self, context: FeatureFlagContext) -> List[str]:
        """Get list of enabled feature flags for context."""
        return [
            name for name, flag in self._flags.items()
            if self.is_enabled(name, context)
        ]
        
    def get_flag_dependencies(self, name: str) -> Set[str]:
        """Get all dependencies for a feature flag."""
        return self._dependencies.get(name, set())
        
    def get_dependent_flags(self, name: str) -> Set[str]:
        """Get all flags that depend on the given flag."""
        return {
            flag_name for flag_name, deps in self._dependencies.items()
            if name in deps
        }
        
    def override_flag(self, name: str, tenant_id: Optional[str] = None, user_id: Optional[str] = None, enabled: bool = True) -> None:
        """Override feature flag for tenant or user."""
        with self._lock:
            flag = self.get_flag(name)
            if not flag:
                raise FeatureFlagNotFoundError(f"Feature flag not found: {name}")
                
            if tenant_id:
                flag.tenant_overrides[tenant_id] = enabled
            if user_id:
                flag.user_overrides[user_id] = enabled
                
            flag.updated_at = datetime.now()
            self._save_flag(flag)
            
    def remove_override(self, name: str, tenant_id: Optional[str] = None, user_id: Optional[str] = None) -> None:
        """Remove feature flag override."""
        with self._lock:
            flag = self.get_flag(name)
            if not flag:
                raise FeatureFlagNotFoundError(f"Feature flag not found: {name}")
                
            if tenant_id and tenant_id in flag.tenant_overrides:
                del flag.tenant_overrides[tenant_id]
            if user_id and user_id in flag.user_overrides:
                del flag.user_overrides[user_id]
                
            flag.updated_at = datetime.now()
            self._save_flag(flag)
            
    def get_flag_metadata(self, name: str) -> Dict[str, Any]:
        """Get feature flag metadata."""
        flag = self.get_flag(name)
        if not flag:
            raise FeatureFlagNotFoundError(f"Feature flag not found: {name}")
        return flag.metadata.copy()
        
    def update_flag_metadata(self, name: str, metadata: Dict[str, Any]) -> None:
        """Update feature flag metadata."""
        with self._lock:
            flag = self.get_flag(name)
            if not flag:
                raise FeatureFlagNotFoundError(f"Feature flag not found: {name}")
                
            flag.metadata.update(metadata)
            flag.updated_at = datetime.now()
            self._save_flag(flag)
            
    def _load_groups(self) -> None:
        """Load feature flag groups from files."""
        groups_file = self.flags_dir / "groups.yaml"
        if not groups_file.exists():
            return
            
        try:
            with open(groups_file) as f:
                data = yaml.safe_load(f)
                for group_data in data:
                    group = FeatureFlagGroup(
                        name=group_data["name"],
                        description=group_data.get("description", "")
                    )
                    group.flags = set(group_data.get("flags", []))
                    group.metadata = group_data.get("metadata", {})
                    group.created_at = datetime.fromisoformat(group_data.get("created_at", datetime.now().isoformat()))
                    group.updated_at = datetime.fromisoformat(group_data.get("updated_at", datetime.now().isoformat()))
                    self._groups[group.name] = group
        except Exception as e:
            logger.error(f"Failed to load feature flag groups: {str(e)}")
            
    def _save_groups(self) -> None:
        """Save feature flag groups to file."""
        groups_file = self.flags_dir / "groups.yaml"
        with open(groups_file, "w") as f:
            yaml.dump([
                {
                    "name": group.name,
                    "description": group.description,
                    "flags": list(group.flags),
                    "metadata": group.metadata,
                    "created_at": group.created_at.isoformat(),
                    "updated_at": group.updated_at.isoformat()
                }
                for group in self._groups.values()
            ], f)
            
    def create_group(self, name: str, description: str = "") -> FeatureFlagGroup:
        """Create new feature flag group."""
        with self._lock:
            if name in self._groups:
                raise FeatureFlagValidationError(f"Group already exists: {name}")
                
            group = FeatureFlagGroup(name, description)
            self._groups[name] = group
            self._save_groups()
            return group
            
    def update_group(self, name: str, updates: Dict[str, Any]) -> FeatureFlagGroup:
        """Update feature flag group."""
        with self._lock:
            group = self._groups.get(name)
            if not group:
                raise FeatureFlagNotFoundError(f"Group not found: {name}")
                
            for key, value in updates.items():
                if hasattr(group, key):
                    setattr(group, key, value)
                    
            group.updated_at = datetime.now()
            self._save_groups()
            return group
            
    def delete_group(self, name: str) -> None:
        """Delete feature flag group."""
        with self._lock:
            if name not in self._groups:
                raise FeatureFlagNotFoundError(f"Group not found: {name}")
                
            # Remove group from all flags
            for flag in self._flags.values():
                if flag.group == name:
                    flag.group = None
                    
            del self._groups[name]
            self._save_groups()
            
    def add_flag_to_group(self, flag_name: str, group_name: str) -> None:
        """Add flag to group."""
        with self._lock:
            flag = self.get_flag(flag_name)
            if not flag:
                raise FeatureFlagNotFoundError(f"Flag not found: {flag_name}")
                
            group = self._groups.get(group_name)
            if not group:
                raise FeatureFlagNotFoundError(f"Group not found: {group_name}")
                
            flag.group = group_name
            group.flags.add(flag_name)
            group.updated_at = datetime.now()
            self._save_groups()
            
    def remove_flag_from_group(self, flag_name: str, group_name: str) -> None:
        """Remove flag from group."""
        with self._lock:
            flag = self.get_flag(flag_name)
            if not flag:
                raise FeatureFlagNotFoundError(f"Flag not found: {flag_name}")
                
            group = self._groups.get(group_name)
            if not group:
                raise FeatureFlagNotFoundError(f"Group not found: {group_name}")
                
            if flag.group == group_name:
                flag.group = None
                
            group.flags.discard(flag_name)
            group.updated_at = datetime.now()
            self._save_groups()
            
    def get_group_flags(self, group_name: str) -> List[str]:
        """Get all flags in a group."""
        group = self._groups.get(group_name)
        if not group:
            raise FeatureFlagNotFoundError(f"Group not found: {group_name}")
        return list(group.flags)
        
    def get_flag_group(self, flag_name: str) -> Optional[str]:
        """Get group name for a flag."""
        flag = self.get_flag(flag_name)
        if not flag:
            raise FeatureFlagNotFoundError(f"Flag not found: {flag_name}")
        return flag.group
        
    def _validate_required_fields(self, flag: FeatureFlag, rule: ValidationRule) -> None:
        """Validate required fields."""
        required = rule.parameters.get("fields", [])
        for field in required:
            if not getattr(flag, field):
                raise FeatureFlagValidationError(f"Required field missing: {field}")
                
    def _validate_format(self, flag: FeatureFlag, rule: ValidationRule) -> None:
        """Validate field format."""
        field = rule.parameters.get("field")
        pattern = rule.parameters.get("pattern")
        if not field or not pattern:
            return
            
        value = getattr(flag, field)
        if value and not re.match(pattern, str(value)):
            raise FeatureFlagValidationError(f"Invalid format for field {field}")
            
    def _validate_dependencies(self, flag: FeatureFlag, rule: ValidationRule) -> None:
        """Validate dependencies."""
        required_deps = rule.parameters.get("dependencies", [])
        for dep in required_deps:
            if dep not in flag.dependencies:
                raise FeatureFlagValidationError(f"Missing required dependency: {dep}")
                
    def _validate_conflicts(self, flag: FeatureFlag, rule: ValidationRule) -> None:
        """Validate conflicts with other flags."""
        conflicts = rule.parameters.get("conflicts", [])
        for conflict in conflicts:
            if conflict in flag.dependencies:
                raise FeatureFlagValidationError(f"Conflicting dependency: {conflict}")
                
    def _validate_custom_rule(self, flag: FeatureFlag, rule: ValidationRule) -> None:
        """Validate using custom rule function."""
        func = rule.parameters.get("function")
        if not callable(func):
            return
            
        if not func(flag):
            raise FeatureFlagValidationError(f"Custom validation failed for flag: {flag.name}")
            
    def get_flags_by_group(self, group_name: str) -> List[FeatureFlag]:
        """Get all flags in a group."""
        return [
            flag for flag in self._flags.values()
            if flag.group == group_name
        ]
        
    def get_flags_by_tag(self, tag: str) -> List[FeatureFlag]:
        """Get all flags with a specific tag."""
        return [
            flag for flag in self._flags.values()
            if flag.tags and tag in flag.tags
        ]
        
    def get_flags_by_tags(self, tags: List[str], match_all: bool = False) -> List[FeatureFlag]:
        """Get all flags matching tags."""
        if match_all:
            return [
                flag for flag in self._flags.values()
                if flag.tags and all(tag in flag.tags for tag in tags)
            ]
        return [
            flag for flag in self._flags.values()
            if flag.tags and any(tag in flag.tags for tag in tags)
        ]
        
    def _validate_value_range(self, flag: FeatureFlag, rule: ValidationRule) -> None:
        """Validate numeric value range."""
        field = rule.parameters.get("field")
        min_val = rule.parameters.get("min")
        max_val = rule.parameters.get("max")
        
        if not field or (min_val is None and max_val is None):
            return
            
        value = getattr(flag, field)
        if value is None:
            return
            
        if min_val is not None and value < min_val:
            raise FeatureFlagValidationError(f"Value {value} is below minimum {min_val}")
            
        if max_val is not None and value > max_val:
            raise FeatureFlagValidationError(f"Value {value} is above maximum {max_val}")
            
    def _validate_enum(self, flag: FeatureFlag, rule: ValidationRule) -> None:
        """Validate enum value."""
        field = rule.parameters.get("field")
        allowed_values = rule.parameters.get("values", [])
        
        if not field or not allowed_values:
            return
            
        value = getattr(flag, field)
        if value is None:
            return
            
        if value not in allowed_values:
            raise FeatureFlagValidationError(f"Value {value} is not in allowed values {allowed_values}")
            
    def _validate_regex(self, flag: FeatureFlag, rule: ValidationRule) -> None:
        """Validate regex pattern."""
        field = rule.parameters.get("field")
        pattern = rule.parameters.get("pattern")
        
        if not field or not pattern:
            return
            
        value = getattr(flag, field)
        if value is None:
            return
            
        if not re.match(pattern, str(value)):
            raise FeatureFlagValidationError(f"Value {value} does not match pattern {pattern}")
            
    def _validate_date(self, flag: FeatureFlag, rule: ValidationRule) -> None:
        """Validate date constraints."""
        field = rule.parameters.get("field")
        min_date = rule.parameters.get("min_date")
        max_date = rule.parameters.get("max_date")
        
        if not field or (min_date is None and max_date is None):
            return
            
        value = getattr(flag, field)
        if value is None:
            return
            
        if min_date and value < datetime.fromisoformat(min_date):
            raise FeatureFlagValidationError(f"Date {value} is before minimum {min_date}")
            
        if max_date and value > datetime.fromisoformat(max_date):
            raise FeatureFlagValidationError(f"Date {value} is after maximum {max_date}")
            
    def _validate_unique(self, flag: FeatureFlag, rule: ValidationRule) -> None:
        """Validate uniqueness constraint."""
        field = rule.parameters.get("field")
        
        if not field:
            return
            
        value = getattr(flag, field)
        if value is None:
            return
            
        # Check uniqueness across all flags
        for other_flag in self._flags.values():
            if other_flag.name != flag.name and getattr(other_flag, field) == value:
                raise FeatureFlagValidationError(f"Value {value} is not unique for field {field}")
                
    def _validate_relationship(self, flag: FeatureFlag, rule: ValidationRule) -> None:
        """Validate relationships between flags."""
        field = rule.parameters.get("field")
        related_field = rule.parameters.get("related_field")
        relationship_type = rule.parameters.get("relationship_type")
        
        if not all([field, related_field, relationship_type]):
            return
            
        value = getattr(flag, field)
        if value is None:
            return
            
        if relationship_type == "parent_child":
            # Validate parent-child relationship
            parent = self.get_flag(value)
            if not parent or getattr(parent, related_field) != flag.name:
                raise FeatureFlagValidationError(f"Invalid parent-child relationship")
                
        elif relationship_type == "sibling":
            # Validate sibling relationship
            sibling = self.get_flag(value)
            if not sibling or getattr(sibling, related_field) != getattr(flag, related_field):
                raise FeatureFlagValidationError(f"Invalid sibling relationship")

    def _load_templates(self) -> None:
        """Load feature flag templates from files."""
        templates_file = self.flags_dir / "templates.yaml"
        if not templates_file.exists():
            return
            
        try:
            with open(templates_file) as f:
                data = yaml.safe_load(f)
                for template_data in data:
                    template = FeatureFlagTemplate(
                        name=template_data["name"],
                        description=template_data.get("description", ""),
                        base_config=template_data.get("base_config", {}),
                        created_at=datetime.fromisoformat(template_data.get("created_at", datetime.now().isoformat())),
                        updated_at=datetime.fromisoformat(template_data.get("updated_at", datetime.now().isoformat())),
                        metadata=template_data.get("metadata", {}),
                        validation_rules=template_data.get("validation_rules", [])
                    )
                    self._templates[template.name] = template
        except Exception as e:
            logger.error(f"Failed to load feature flag templates: {str(e)}")
            
    def _save_templates(self) -> None:
        """Save feature flag templates to file."""
        templates_file = self.flags_dir / "templates.yaml"
        with open(templates_file, "w") as f:
            yaml.dump([
                {
                    "name": template.name,
                    "description": template.description,
                    "base_config": template.base_config,
                    "created_at": template.created_at.isoformat(),
                    "updated_at": template.updated_at.isoformat(),
                    "metadata": template.metadata,
                    "validation_rules": template.validation_rules
                }
                for template in self._templates.values()
            ], f)
            
    def create_template(self, name: str, description: str, base_config: Dict[str, Any]) -> FeatureFlagTemplate:
        """Create new feature flag template."""
        with self._lock:
            if name in self._templates:
                raise FeatureFlagValidationError(f"Template already exists: {name}")
                
            template = FeatureFlagTemplate(
                name=name,
                description=description,
                base_config=base_config,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self._templates[name] = template
            self._save_templates()
            return template
            
    def update_template(self, name: str, updates: Dict[str, Any]) -> FeatureFlagTemplate:
        """Update feature flag template."""
        with self._lock:
            template = self._templates.get(name)
            if not template:
                raise FeatureFlagNotFoundError(f"Template not found: {name}")
                
            for key, value in updates.items():
                if hasattr(template, key):
                    setattr(template, key, value)
                    
            template.updated_at = datetime.now()
            self._save_templates()
            return template
            
    def delete_template(self, name: str) -> None:
        """Delete feature flag template."""
        with self._lock:
            if name not in self._templates:
                raise FeatureFlagNotFoundError(f"Template not found: {name}")
                
            # Check if template is in use
            for flag in self._flags.values():
                if flag.metadata and flag.metadata.get("template") == name:
                    raise FeatureFlagValidationError(f"Cannot delete template {name} as it is in use")
                    
            del self._templates[name]
            self._save_templates()
            
    def create_flag_from_template(self, template_name: str, flag_data: Dict[str, Any]) -> FeatureFlag:
        """Create a new flag from a template."""
        with self._lock:
            template = self._templates.get(template_name)
            if not template:
                raise FeatureFlagNotFoundError(f"Template not found: {template_name}")
                
            # Merge template config with flag data
            merged_data = {
                **template.base_config,
                **flag_data,
                "metadata": {
                    **(template.base_config.get("metadata", {})),
                    **(flag_data.get("metadata", {})),
                    "template": template_name
                }
            }
            
            return self.create_flag(merged_data)
            
    def get_flags_by_template(self, template_name: str) -> List[FeatureFlag]:
        """Get all flags created from a template."""
        return [
            flag for flag in self._flags.values()
            if flag.metadata and flag.metadata.get("template") == template_name
        ]
        
    def update_template_flags(self, template_name: str, updates: Dict[str, Any]) -> List[FeatureFlag]:
        """Update all flags created from a template."""
        with self._lock:
            template = self._templates.get(template_name)
            if not template:
                raise FeatureFlagNotFoundError(f"Template not found: {template_name}")
                
            updated_flags = []
            for flag in self.get_flags_by_template(template_name):
                # Apply updates while preserving flag-specific values
                for key, value in updates.items():
                    if key not in ["name", "created_at"]:  # Preserve these values
                        setattr(flag, key, value)
                flag.updated_at = datetime.now()
                self._save_flag(flag)
                updated_flags.append(flag)
                
            return updated_flags
            
    def get_template_usage_stats(self, template_name: str) -> Dict[str, Any]:
        """Get usage statistics for a template."""
        template = self._templates.get(template_name)
        if not template:
            raise FeatureFlagNotFoundError(f"Template not found: {template_name}")
            
        flags = self.get_flags_by_template(template_name)
        return {
            "total_flags": len(flags),
            "enabled_flags": len([f for f in flags if f.status == FeatureStatus.ENABLED]),
            "disabled_flags": len([f for f in flags if f.status == FeatureStatus.DISABLED]),
            "rolling_out_flags": len([f for f in flags if f.status == FeatureStatus.ROLLING_OUT]),
            "deprecated_flags": len([f for f in flags if f.status == FeatureStatus.DEPRECATED])
        }
        
    def _load_ab_tests(self) -> None:
        """Load A/B tests from files."""
        tests_file = self.flags_dir / "ab_tests.yaml"
        if not tests_file.exists():
            return
            
        try:
            with open(tests_file) as f:
                data = yaml.safe_load(f)
                for test_data in data:
                    test = ABTest(
                        name=test_data["name"],
                        description=test_data.get("description", ""),
                        variants=[
                            ABTestVariant(
                                name=v["name"],
                                weight=v["weight"],
                                config=v["config"],
                                metadata=v.get("metadata", {})
                            )
                            for v in test_data["variants"]
                        ],
                        start_date=datetime.fromisoformat(test_data["start_date"]),
                        end_date=datetime.fromisoformat(test_data["end_date"])
                        if test_data.get("end_date") else None,
                        status=test_data.get("status", "active"),
                        metrics=test_data.get("metrics", []),
                        metadata=test_data.get("metadata", {})
                    )
                    self._ab_tests[test.name] = test
        except Exception as e:
            logger.error(f"Failed to load A/B tests: {str(e)}")
            
    def _save_ab_tests(self) -> None:
        """Save A/B tests to file."""
        tests_file = self.flags_dir / "ab_tests.yaml"
        with open(tests_file, "w") as f:
            yaml.dump([
                {
                    "name": test.name,
                    "description": test.description,
                    "variants": [
                        {
                            "name": v.name,
                            "weight": v.weight,
                            "config": v.config,
                            "metadata": v.metadata
                        }
                        for v in test.variants
                    ],
                    "start_date": test.start_date.isoformat(),
                    "end_date": test.end_date.isoformat() if test.end_date else None,
                    "status": test.status,
                    "metrics": test.metrics,
                    "metadata": test.metadata
                }
                for test in self._ab_tests.values()
            ], f)
            
    def _load_time_rules(self) -> None:
        """Load time-based rules from files."""
        rules_file = self.flags_dir / "time_rules.yaml"
        if not rules_file.exists():
            return
            
        try:
            with open(rules_file) as f:
                data = yaml.safe_load(f)
                for rule_data in data:
                    rule = TimeBasedRule(
                        name=rule_data["name"],
                        schedule=rule_data["schedule"],
                        timezone=rule_data["timezone"],
                        enabled=rule_data.get("enabled", True),
                        metadata=rule_data.get("metadata", {})
                    )
                    self._time_rules[rule.name] = rule
        except Exception as e:
            logger.error(f"Failed to load time-based rules: {str(e)}")
            
    def _save_time_rules(self) -> None:
        """Save time-based rules to file."""
        rules_file = self.flags_dir / "time_rules.yaml"
        with open(rules_file, "w") as f:
            yaml.dump([
                {
                    "name": rule.name,
                    "schedule": rule.schedule,
                    "timezone": rule.timezone,
                    "enabled": rule.enabled,
                    "metadata": rule.metadata
                }
                for rule in self._time_rules.values()
            ], f)
            
    def create_ab_test(self, test_data: Dict[str, Any]) -> ABTest:
        """Create new A/B test."""
        with self._lock:
            test = ABTest(
                name=test_data["name"],
                description=test_data.get("description", ""),
                variants=[
                    ABTestVariant(
                        name=v["name"],
                        weight=v["weight"],
                        config=v["config"],
                        metadata=v.get("metadata", {})
                    )
                    for v in test_data["variants"]
                ],
                start_date=datetime.fromisoformat(test_data["start_date"]),
                end_date=datetime.fromisoformat(test_data["end_date"])
                if test_data.get("end_date") else None,
                status=test_data.get("status", "active"),
                metrics=test_data.get("metrics", []),
                metadata=test_data.get("metadata", {})
            )
            
            if test.name in self._ab_tests:
                raise FeatureFlagValidationError(f"A/B test already exists: {test.name}")
                
            self._ab_tests[test.name] = test
            self._save_ab_tests()
            return test
            
    def create_time_rule(self, rule_data: Dict[str, Any]) -> TimeBasedRule:
        """Create new time-based rule."""
        with self._lock:
            rule = TimeBasedRule(
                name=rule_data["name"],
                schedule=rule_data["schedule"],
                timezone=rule_data["timezone"],
                enabled=rule_data.get("enabled", True),
                metadata=rule_data.get("metadata", {})
            )
            
            if rule.name in self._time_rules:
                raise FeatureFlagValidationError(f"Time-based rule already exists: {rule.name}")
                
            self._time_rules[rule.name] = rule
            self._save_time_rules()
            return rule
            
    def get_ab_test_variant(self, test_name: str, context: FeatureFlagContext) -> Optional[ABTestVariant]:
        """Get A/B test variant for context."""
        test = self._ab_tests.get(test_name)
        if not test or test.status != "active":
            return None
            
        if test.start_date <= datetime.now() <= (test.end_date or datetime.max):
            hash_value = hash(f"{context.tenant_id}:{context.user_id}:{test.name}")
            cumulative_weight = 0
            for variant in test.variants:
                cumulative_weight += variant.weight
                if hash_value % 100 < cumulative_weight * 100:
                    return variant
                    
        return None
        
    def get_time_rule_status(self, rule_name: str) -> Dict[str, Any]:
        """Get status of time-based rule."""
        rule = self._time_rules.get(rule_name)
        if not rule:
            raise FeatureFlagNotFoundError(f"Time-based rule not found: {rule_name}")
            
        is_active = self._evaluate_time_rule(rule)
        return {
            "name": rule.name,
            "enabled": rule.enabled,
            "active": is_active,
            "schedule": rule.schedule,
            "timezone": rule.timezone,
            "next_run": self._get_next_rule_run(rule) if is_active else None
        }
        
    def _get_next_rule_run(self, rule: TimeBasedRule) -> Optional[datetime]:
        """Get next scheduled run time for a rule."""
        now = datetime.now()
        schedule = rule.schedule
        
        if "cron" in schedule:
            try:
                from croniter import croniter
                cron = croniter(schedule["cron"], now)
                return cron.get_next(datetime)
            except ImportError:
                return None
                
        if "windows" in schedule:
            next_run = None
            for window in schedule["windows"]:
                start_time = datetime.strptime(window["start"], "%H:%M").time()
                next_window = datetime.combine(now.date(), start_time)
                if next_window < now:
                    next_window = datetime.combine(now.date().replace(day=now.day + 1), start_time)
                if next_run is None or next_window < next_run:
                    next_run = next_window
            return next_run
            
        if "dates" in schedule:
            next_run = None
            for date_range in schedule["dates"]:
                start_date = datetime.fromisoformat(date_range["start"])
                if start_date > now and (next_run is None or start_date < next_run):
                    next_run = start_date
            return next_run
            
        return None
        
    def _evaluate_time_rule(self, rule: TimeBasedRule) -> bool:
        """Evaluate time-based rule."""
        if not rule.enabled:
            return False
            
        now = datetime.now()
        schedule = rule.schedule
        
        # Handle cron expression
        if "cron" in schedule:
            try:
                from croniter import croniter
                cron = croniter(schedule["cron"], now)
                next_run = cron.get_next(datetime)
                return now >= next_run
            except ImportError:
                logger.error("croniter package not installed")
                return False
                
        # Handle time windows
        if "windows" in schedule:
            for window in schedule["windows"]:
                start_time = datetime.strptime(window["start"], "%H:%M").time()
                end_time = datetime.strptime(window["end"], "%H:%M").time()
                current_time = now.time()
                
                if start_time <= current_time <= end_time:
                    return True
                    
        # Handle specific dates
        if "dates" in schedule:
            for date_range in schedule["dates"]:
                start_date = datetime.fromisoformat(date_range["start"])
                end_date = datetime.fromisoformat(date_range["end"])
                if start_date <= now <= end_date:
                    return True
                    
        return False
        
    def _load_ab_test_metrics(self) -> None:
        """Load A/B test metrics from file."""
        metrics_file = self.flags_dir / "ab_test_metrics.yaml"
        if not metrics_file.exists():
            return
            
        try:
            with open(metrics_file) as f:
                data = yaml.safe_load(f)
                for test_name, variants in data.items():
                    self._ab_test_metrics[test_name] = {}
                    for variant_name, metrics_data in variants.items():
                        self._ab_test_metrics[test_name][variant_name] = ABTestMetrics(
                            test_name=test_name,
                            variant_name=variant_name,
                            impressions=metrics_data.get("impressions", 0),
                            conversions=metrics_data.get("conversions", 0),
                            revenue=metrics_data.get("revenue", 0.0),
                            custom_metrics=metrics_data.get("custom_metrics", {}),
                            last_updated=datetime.fromisoformat(metrics_data.get("last_updated", datetime.now().isoformat()))
                        )
        except Exception as e:
            logger.error(f"Failed to load A/B test metrics: {str(e)}")
            
    def _save_ab_test_metrics(self) -> None:
        """Save A/B test metrics to file."""
        metrics_file = self.flags_dir / "ab_test_metrics.yaml"
        with open(metrics_file, "w") as f:
            yaml.dump({
                test_name: {
                    variant_name: {
                        "impressions": metrics.impressions,
                        "conversions": metrics.conversions,
                        "revenue": metrics.revenue,
                        "custom_metrics": metrics.custom_metrics,
                        "last_updated": metrics.last_updated.isoformat()
                    }
                    for variant_name, metrics in variants.items()
                }
                for test_name, variants in self._ab_test_metrics.items()
            }, f)
            
    def track_ab_test_impression(self, test_name: str, variant_name: str) -> None:
        """Track A/B test impression."""
        with self._lock:
            if test_name not in self._ab_test_metrics:
                self._ab_test_metrics[test_name] = {}
                
            if variant_name not in self._ab_test_metrics[test_name]:
                self._ab_test_metrics[test_name][variant_name] = ABTestMetrics(
                    test_name=test_name,
                    variant_name=variant_name
                )
                
            metrics = self._ab_test_metrics[test_name][variant_name]
            metrics.impressions += 1
            metrics.last_updated = datetime.now()
            self._save_ab_test_metrics()
            
    def track_ab_test_conversion(self, test_name: str, variant_name: str, revenue: float = 0.0, custom_metrics: Dict[str, float] = None) -> None:
        """Track A/B test conversion."""
        with self._lock:
            if test_name not in self._ab_test_metrics or variant_name not in self._ab_test_metrics[test_name]:
                raise FeatureFlagValidationError(f"Invalid test or variant: {test_name}/{variant_name}")
                
            metrics = self._ab_test_metrics[test_name][variant_name]
            metrics.conversions += 1
            metrics.revenue += revenue
            if custom_metrics:
                if not metrics.custom_metrics:
                    metrics.custom_metrics = {}
                for metric_name, value in custom_metrics.items():
                    metrics.custom_metrics[metric_name] = metrics.custom_metrics.get(metric_name, 0) + value
                    
            metrics.last_updated = datetime.now()
            self._save_ab_test_metrics()
            
    def get_ab_test_metrics(self, test_name: str) -> Dict[str, ABTestMetrics]:
        """Get metrics for an A/B test."""
        return self._ab_test_metrics.get(test_name, {}).copy()
        
    def get_ab_test_stats(self, test_name: str) -> Dict[str, Any]:
        """Get statistical analysis for an A/B test."""
        metrics = self._ab_test_metrics.get(test_name, {})
        if not metrics:
            return {}
            
        stats = {}
        for variant_name, variant_metrics in metrics.items():
            stats[variant_name] = {
                "impressions": variant_metrics.impressions,
                "conversions": variant_metrics.conversions,
                "conversion_rate": variant_metrics.conversions / variant_metrics.impressions if variant_metrics.impressions > 0 else 0,
                "revenue": variant_metrics.revenue,
                "revenue_per_impression": variant_metrics.revenue / variant_metrics.impressions if variant_metrics.impressions > 0 else 0,
                "custom_metrics": variant_metrics.custom_metrics,
                "last_updated": variant_metrics.last_updated
            }
            
        return stats 