"""Base class for model providers."""
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging
from datetime import datetime
import uuid

from src.core.models.types import ModelCapability, ProviderResponse

# Configure logging
logger = logging.getLogger("ade-base-provider")

class ModelProvider(ABC):
    """Base class for model providers"""
    
    def __init__(self, api_key: str, provider_id: Optional[str] = None):
        self.api_key = api_key
        self.provider_id = provider_id or str(uuid.uuid4())
        self.is_initialized = False
        self.created_at = datetime.now()
        self.last_used = None
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0
    
    @property
    @abstractmethod
    def provider_type(self) -> str:
        """Return the type of provider"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the provider"""
        pass
    
    @abstractmethod
    def list_available_models(self) -> List[str]:
        """List all available models from this provider"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[ModelCapability]:
        """Return the capabilities this provider supports"""
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        images: Optional[List[bytes]] = None
    ) -> ProviderResponse:
        """Generate text from a prompt"""
        pass
    
    def update_metrics(
        self,
        success: bool,
        tokens: int = 0,
        cost: float = 0.0
    ) -> None:
        """Update provider metrics"""
        self.last_used = datetime.now()
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        self.total_tokens += tokens
        self.total_cost += cost
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get provider metrics"""
        return {
            "provider_id": self.provider_id,
            "provider_type": self.provider_type,
            "is_initialized": self.is_initialized,
            "created_at": self.created_at,
            "last_used": self.last_used,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / self.total_requests if self.total_requests > 0 else 0,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "average_cost_per_request": self.total_cost / self.total_requests if self.total_requests > 0 else 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert provider to dictionary"""
        return {
            "provider_id": self.provider_id,
            "provider_type": self.provider_type,
            "api_key": self.api_key,
            "is_initialized": self.is_initialized,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "metrics": self.get_metrics()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelProvider":
        """Create provider from dictionary"""
        provider = cls(
            api_key=data["api_key"],
            provider_id=data["provider_id"]
        )
        provider.is_initialized = data["is_initialized"]
        provider.created_at = datetime.fromisoformat(data["created_at"])
        if data["last_used"]:
            provider.last_used = datetime.fromisoformat(data["last_used"])
        
        # Update metrics
        metrics = data.get("metrics", {})
        provider.total_requests = metrics.get("total_requests", 0)
        provider.successful_requests = metrics.get("successful_requests", 0)
        provider.failed_requests = metrics.get("failed_requests", 0)
        provider.total_tokens = metrics.get("total_tokens", 0)
        provider.total_cost = metrics.get("total_cost", 0.0)
        
        return provider 