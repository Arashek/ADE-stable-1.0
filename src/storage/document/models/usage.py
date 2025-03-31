from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class UsageType(str, Enum):
    """Types of usage that can be tracked"""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    EMBEDDING = "embedding"
    VISION = "vision"
    AUDIO = "audio"

class BillingTier(str, Enum):
    """Available billing tiers"""
    FREE = "free"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class UsageRecord(BaseModel):
    """Individual usage record for an API call"""
    id: str = Field(..., description="Unique identifier for the usage record")
    user_id: str = Field(..., description="ID of the user making the request")
    project_id: Optional[str] = Field(None, description="ID of the project if applicable")
    provider: str = Field(..., description="Name of the AI provider used")
    model: str = Field(..., description="Model used for the request")
    usage_type: UsageType = Field(..., description="Type of usage")
    tokens_used: int = Field(..., description="Number of tokens used")
    cost: float = Field(..., description="Cost of the request in USD")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(..., description="Status of the request (success/failure)")
    error_message: Optional[str] = Field(None, description="Error message if request failed")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata about the request")

class UserUsageSummary(BaseModel):
    """Aggregated usage metrics for a user"""
    user_id: str = Field(..., description="ID of the user")
    billing_tier: BillingTier = Field(..., description="Current billing tier")
    total_tokens: int = Field(default=0, description="Total tokens used")
    total_cost: float = Field(default=0.0, description="Total cost in USD")
    usage_by_type: Dict[UsageType, int] = Field(default_factory=dict, description="Usage breakdown by type")
    usage_by_provider: Dict[str, int] = Field(default_factory=dict, description="Usage breakdown by provider")
    usage_by_model: Dict[str, int] = Field(default_factory=dict, description="Usage breakdown by model")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    quota_limits: Dict[str, int] = Field(default_factory=dict, description="Quota limits for the tier")
    quota_usage: Dict[str, int] = Field(default_factory=dict, description="Current quota usage")

class BillingTierConfig(BaseModel):
    """Configuration for a billing tier"""
    tier: BillingTier = Field(..., description="Name of the billing tier")
    monthly_price: float = Field(..., description="Monthly price in USD")
    quota_limits: Dict[str, int] = Field(..., description="Quota limits for different usage types")
    features: List[str] = Field(..., description="Features included in this tier")
    priority: int = Field(..., description="Priority level for request routing")
    rate_limits: Dict[str, int] = Field(..., description="Rate limits per minute")
    custom_limits: Optional[Dict[str, int]] = Field(None, description="Custom limits for enterprise tier") 