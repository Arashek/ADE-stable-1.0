from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass, field

class ProviderTier(Enum):
    """Provider tiers indicating quality and capabilities"""
    FREE = 0
    STANDARD = 1
    PREMIUM = 2
    ENTERPRISE = 3

class Capability(Enum):
    """Capabilities that providers can support"""
    CODE_COMPLETION = "code_completion"
    PLANNING = "planning"
    CONTEXT_AWARENESS = "context_awareness"
    CODE_ANALYSIS = "code_analysis"
    REFACTORING = "refactoring"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"
    DEBUGGING = "debugging"

class ProviderCredentials(BaseModel):
    """Provider authentication credentials"""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    organization_id: Optional[str] = None

class RateLimits(BaseModel):
    """Rate limits for a provider"""
    requests_per_minute: Optional[int] = None
    tokens_per_minute: Optional[int] = None
    concurrent_requests: Optional[int] = None

class CostLimits(BaseModel):
    """Cost limits for a provider"""
    max_daily_cost: Optional[float] = None
    max_request_cost: Optional[float] = None
    alert_threshold: Optional[float] = None

@dataclass
class ProviderConfig:
    """Configuration for an AI provider"""
    tier: ProviderTier
    model_path: str
    enabled: bool = True
    server_url: Optional[str] = None
    device: str = "cuda"
    batch_size: int = 1
    quantization: Optional[str] = None
    capabilities: Dict[Capability, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default capabilities if none provided"""
        if not self.capabilities:
            self.capabilities = {
                Capability.CODE_COMPLETION: 0.8,
                Capability.PLANNING: 0.7,
                Capability.CONTEXT_AWARENESS: 0.8
            }

@dataclass
class ProprietaryModelConfig(ProviderConfig):
    model_path: str
    device: str = "cuda"
    batch_size: int = 1
    quantization: Optional[str] = None

class ProviderConfig(BaseModel):
    """Configuration for a provider"""
    enabled: bool = True
    tier: ProviderTier = ProviderTier.STANDARD
    credentials: ProviderCredentials = Field(default_factory=ProviderCredentials)
    default_model: Optional[str] = None
    server_url: Optional[str] = None
    rate_limit: Optional[int] = None
    capabilities: Dict[Capability, float] = Field(default_factory=dict)
    fallback_providers: Optional[list[str]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[list[str]] = None
    extra_params: Dict[str, Any] = Field(default_factory=dict)
    rate_limits: RateLimits = Field(default_factory=RateLimits)
    cost_limits: CostLimits = Field(default_factory=CostLimits)
    fallback: Optional[str] = None
    priority: int = 0  # Lower numbers = higher priority
    
    class Config:
        # Allow extra fields for provider-specific configuration
        extra = "allow"


