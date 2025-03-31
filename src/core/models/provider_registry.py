from enum import Enum, auto
from typing import Dict, Optional, Any, List, Set, Tuple, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import statistics
from collections import defaultdict
import logging
import uuid
from pydantic import BaseModel, Field
import asyncio

from src.utils.encryption import encrypt_value, decrypt_value, encrypt_dict, decrypt_dict
from src.storage.document.repositories import ProviderRepository, ProviderConfig
from src.utils.metrics import register_provider_metrics, update_provider_status, track_provider_request
from .types import ModelCapability, ProviderType, ProviderResponse

# Configure logging
logger = logging.getLogger("ade-provider-registry")

class Provider(BaseModel):
    """Provider configuration."""
    provider_id: str = Field(..., description="Unique identifier for the provider")
    provider_type: ProviderType = Field(..., description="Type of provider")
    api_key: str = Field(..., description="API key for the provider")
    model_map: Dict[str, str] = Field(default_factory=dict, description="Mapping of model names to provider-specific model IDs")
    default_parameters: Dict[str, Any] = Field(default_factory=dict, description="Default parameters for the provider")
    description: Optional[str] = Field(None, description="Description of the provider")
    rate_limit: Optional[int] = Field(None, description="Rate limit in requests per minute")
    is_active: bool = Field(True, description="Whether the provider is active")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert provider to dictionary with encrypted sensitive data."""
        data = self.model_dump()
        return encrypt_dict(data, ["api_key"])

    @classmethod
    def from_dict(cls, data: dict) -> "Provider":
        """Create provider from dictionary with decrypted sensitive data."""
        decrypted_data = decrypt_dict(data, ["api_key"])
        return cls(**decrypted_data)

class ProviderCapability(str, Enum):
    """Capabilities supported by providers"""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    IMAGE_UNDERSTANDING = "image_understanding"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    EMBEDDING_GENERATION = "embedding_generation"

@dataclass
class ProviderPerformance:
    """Performance metrics for a provider"""
    success_count: int = 0
    failure_count: int = 0
    total_latency: float = 0.0
    total_cost: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    total_requests: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
    
    @property
    def average_latency(self) -> float:
        """Calculate average latency"""
        return self.total_latency / self.total_requests if self.total_requests > 0 else 0.0
    
    @property
    def average_cost(self) -> float:
        """Calculate average cost per request"""
        return self.total_cost / self.total_requests if self.total_requests > 0 else 0.0

class ModelProvider(ABC):
    """Abstract base class for model providers"""
    
    def __init__(self, api_key: str, provider_id: Optional[str] = None):
        """Initialize the provider with encrypted API key.
        
        Args:
            api_key: The API key to encrypt and store.
            provider_id: Optional provider ID. If not provided, generates a UUID.
        """
        self._encrypted_api_key = encrypt_value(api_key)  # Store encrypted
        self.provider_id = provider_id or str(uuid.uuid4())
        self.is_initialized = False
        self.performance = ProviderPerformance()
        self.capabilities_scores: Dict[ModelCapability, float] = {}
        logger.info(f"Initialized provider {self.provider_id}")
    
    @property
    def api_key(self) -> str:
        """Get decrypted API key.
        
        Returns:
            The decrypted API key.
            
        Raises:
            Exception: If decryption fails.
        """
        return decrypt_value(self._encrypted_api_key)
    
    def update_api_key(self, new_api_key: str) -> None:
        """Update the provider's API key.
        
        Args:
            new_api_key: The new API key to encrypt and store.
        """
        self._encrypted_api_key = encrypt_value(new_api_key)
        logger.info(f"Updated API key for provider {self.provider_id}")
    
    @abstractmethod
    def has_capability(self, capability: ModelCapability) -> bool:
        """Check if the provider supports a specific capability.
        
        Args:
            capability: The capability to check.
            
        Returns:
            True if the provider supports the capability.
        """
        return capability in self.capabilities_scores
    
    @abstractmethod
    @track_provider_request
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        images: Optional[List[bytes]] = None
    ) -> ProviderResponse:
        """Execute a request with the provider.
        
        Args:
            prompt: The prompt to send to the provider.
            model: Optional model to use.
            parameters: Optional parameters for the request.
            images: Optional list of images for multimodal models.
            
        Returns:
            The provider's response.
            
        Raises:
            Exception: If the request fails.
        """
        pass
    
    def to_dict(self) -> dict:
        """Convert provider to dictionary with encrypted sensitive data.
        
        Returns:
            Dictionary containing provider data with encrypted API key.
        """
        return {
            "provider_id": self.provider_id,
            "_encrypted_api_key": self._encrypted_api_key,
            "is_initialized": self.is_initialized,
            "capabilities_scores": self.capabilities_scores,
            "performance": {
                "success_count": self.performance.success_count,
                "failure_count": self.performance.failure_count,
                "total_latency": self.performance.total_latency,
                "total_cost": self.performance.total_cost,
                "last_success": self.performance.last_success.isoformat() if self.performance.last_success else None,
                "last_failure": self.performance.last_failure.isoformat() if self.performance.last_failure else None,
                "consecutive_failures": self.performance.consecutive_failures,
                "total_requests": self.performance.total_requests
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ModelProvider":
        """Create provider from dictionary with encrypted sensitive data.
        
        Args:
            data: Dictionary containing provider data.
            
        Returns:
            A new provider instance.
        """
        # Create a temporary instance to get the class
        instance = cls(api_key="temp")
        
        # Update instance attributes
        instance.provider_id = data["provider_id"]
        instance._encrypted_api_key = data["_encrypted_api_key"]
        instance.is_initialized = data["is_initialized"]
        instance.capabilities_scores = data["capabilities_scores"]
        
        # Update performance metrics
        perf_data = data["performance"]
        instance.performance = ProviderPerformance(
            success_count=perf_data["success_count"],
            failure_count=perf_data["failure_count"],
            total_latency=perf_data["total_latency"],
            total_cost=perf_data["total_cost"],
            last_success=datetime.fromisoformat(perf_data["last_success"]) if perf_data["last_success"] else None,
            last_failure=datetime.fromisoformat(perf_data["last_failure"]) if perf_data["last_failure"] else None,
            consecutive_failures=perf_data["consecutive_failures"],
            total_requests=perf_data["total_requests"]
        )
        
        return instance

class ProviderSelector:
    """Provider selection strategy implementation"""
    
    def __init__(self, strategy: str = "balanced"):
        """Initialize the provider selector.
        
        Args:
            strategy: Selection strategy to use. Options:
                - "balanced": Balance between performance and cost
                - "performance": Prioritize performance
                - "cost": Prioritize cost
                - "random": Random selection
        """
        self.strategy = strategy
    
    def select_provider(
        self,
        providers: List[ModelProvider],
        capability: ModelCapability,
        context: Optional[Dict] = None
    ) -> Optional[ModelProvider]:
        """Select the best provider based on the strategy.
        
        Args:
            providers: List of available providers
            capability: Required capability
            context: Optional context for selection
            
        Returns:
            Selected provider or None if no suitable provider found
        """
        if not providers:
            return None
            
        if self.strategy == "random":
            return random.choice(providers)
            
        # Calculate scores for each provider
        scores = []
        for provider in providers:
            if not provider.has_capability(capability):
                continue
                
            score = self._calculate_score(provider, capability, context or {})
            scores.append((provider, score))
            
        if not scores:
            return None
            
        # Sort by score and return the best provider
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0]
    
    def _calculate_score(
        self,
        provider: ModelProvider,
        capability: ModelCapability,
        context: Dict
    ) -> float:
        """Calculate provider score based on strategy.
        
        Args:
            provider: Provider to score
            capability: Required capability
            context: Selection context
            
        Returns:
            Provider score
        """
        perf = provider.performance
        
        if self.strategy == "performance":
            # Prioritize success rate and latency
            success_weight = 0.7
            latency_weight = 0.3
            return (
                success_weight * perf.success_rate +
                latency_weight * (1.0 / (perf.average_latency + 1.0))
            )
        elif self.strategy == "cost":
            # Prioritize cost efficiency
            return 1.0 / (perf.average_cost + 1.0)
        else:  # balanced
            # Balance between performance and cost
            perf_weight = 0.6
            cost_weight = 0.4
            perf_score = (
                0.7 * perf.success_rate +
                0.3 * (1.0 / (perf.average_latency + 1.0))
            )
            cost_score = 1.0 / (perf.average_cost + 1.0)
            return perf_weight * perf_score + cost_weight * cost_score

class ProviderRegistry:
    """Registry for model providers"""
    
    def __init__(self, provider_repository: Optional[ProviderRepository] = None, selection_strategy: str = "balanced"):
        self.providers: Dict[str, ModelProvider] = {}
        self.provider_classes: Dict[str, Type[ModelProvider]] = {}
        self.provider_selector = ProviderSelector(strategy=selection_strategy)
        self.provider_repository = provider_repository
        self.last_used: Dict[str, datetime] = {}
        self.provider_rotation: Dict[str, List[str]] = defaultdict(list)
        self.fallback_chains: Dict[str, List[str]] = {}
        self.performance: Dict[str, ProviderPerformance] = defaultdict(ProviderPerformance)
        
        # Load built-in provider classes
        self._load_built_in_providers()
    
    def _load_built_in_providers(self):
        """Load built-in provider classes"""
        try:
            # Import provider classes dynamically to avoid circular dependencies
            from src.core.models.providers.openai import OpenAIProvider
            from src.core.models.providers.anthropic import AnthropicProvider
            from src.core.models.providers.google import GoogleAIProvider
            from src.core.models.providers.deepseek import DeepSeekProvider
            from src.core.models.providers.local import LocalProvider
            
            # Register provider classes
            self.provider_classes = {
                "openai": OpenAIProvider,
                "anthropic": AnthropicProvider,
                "google": GoogleAIProvider,
                "deepseek": DeepSeekProvider,
                "local": LocalProvider
            }
            
            logger.info("Loaded built-in provider classes")
        except Exception as e:
            logger.error(f"Failed to load built-in provider classes: {str(e)}")
            self.provider_classes = {}
    
    def _create_provider_instance(
        self,
        provider_type: str,
        api_key: str,
        model_map: Optional[Dict[str, str]] = None,
        default_parameters: Optional[Dict[str, Any]] = None,
        provider_id: Optional[str] = None
    ) -> ModelProvider:
        """Create a provider instance of the specified type.
        
        Args:
            provider_type: Type of provider to create
            api_key: API key for the provider
            model_map: Optional model mapping
            default_parameters: Optional default parameters
            provider_id: Optional provider ID
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If provider type is not registered
        """
        if provider_type not in self.provider_classes:
            raise ValueError(f"Unknown provider type: {provider_type}")
            
        provider_class = self.provider_classes[provider_type]
        return provider_class(
            api_key=api_key,
            provider_id=provider_id,
            model_map=model_map,
            default_parameters=default_parameters
        )

    async def load_providers_from_database(self):
        """Load providers from database"""
        if not self.provider_repository:
            logger.warning("Provider repository not available, skipping database load")
            return
            
        try:
            # Get all provider configs
            all_configs = await self.provider_repository.list({})
            
            for config in all_configs:
                try:
                    # Check if provider type is registered
                    if config.provider_type not in self.provider_classes:
                        logger.warning(f"Unknown provider type: {config.provider_type}, skipping")
                        continue
                    
                    # Get API key
                    api_key = decrypt_value(config.encrypted_api_key)
                    
                    # Convert capability scores
                    capability_scores = {}
                    for k, v in config.capability_scores.items():
                        try:
                            capability_scores[ModelCapability(k)] = float(v)
                        except (ValueError, KeyError):
                            logger.warning(f"Invalid capability key: {k}")
                    
                    # Register provider
                    provider = self.register_provider(
                        provider_type=config.provider_type,
                        api_key=api_key,
                        provider_id=config.provider_id,
                        model_map=config.model_map,
                        default_parameters=config.default_parameters,
                        capability_scores=capability_scores
                    )
                    
                    # Register metrics for the provider
                    register_provider_metrics(provider)
                    
                    logger.info(f"Loaded provider {config.provider_id} from database")
                except Exception as e:
                    logger.error(f"Failed to load provider {config.provider_id}: {str(e)}")
            
            logger.info(f"Loaded {len(all_configs)} providers from database")
        except Exception as e:
            logger.error(f"Failed to load providers from database: {str(e)}")
    
    async def save_provider_to_database(self, provider: ModelProvider):
        """Save provider to database"""
        if not self.provider_repository:
            logger.warning("Provider repository not available, skipping database save")
            return
            
        try:
            # Get existing config if any
            existing_config = await self.provider_repository.get_by_provider_id(provider.provider_id)
            
            # Create provider config
            config = ProviderConfig(
                provider_type=provider.provider_type,
                provider_id=provider.provider_id,
                encrypted_api_key=provider._encrypted_api_key,
                model_map=getattr(provider, "model_map", {}),
                default_parameters=getattr(provider, "default_parameters", {}),
                capability_scores={k.value: float(v) for k, v in provider.capabilities_scores.items()},
                updated_at=datetime.now()
            )
            
            # Update or create
            if existing_config:
                config.id = existing_config.id
                config.created_at = existing_config.created_at
                await self.provider_repository.update(existing_config.id, config)
                logger.info(f"Updated provider {provider.provider_id} in database")
            else:
                await self.provider_repository.create(config)
                logger.info(f"Created provider {provider.provider_id} in database")
        except Exception as e:
            logger.error(f"Failed to save provider {provider.provider_id} to database: {str(e)}")
    
    async def register_provider(
        self,
        provider_type: str,
        api_key: str,
        model_map: Optional[Dict[str, str]] = None,
        default_parameters: Optional[Dict[str, Any]] = None,
        provider_id: Optional[str] = None,
        capability_scores: Optional[Dict[ModelCapability, float]] = None
    ) -> ModelProvider:
        """Register a new provider"""
        # Create provider as before
        provider = self._create_provider_instance(
            provider_type, api_key, model_map, default_parameters, provider_id
        )
        
        # Set capability scores if provided
        if capability_scores:
            provider.set_capability_scores(capability_scores)
        
        # Initialize provider
        success = provider.initialize()
        if not success:
            raise Exception(f"Provider initialization failed")
        
        # Add to registry
        self.providers[provider.provider_id] = provider
        
        # Register metrics for the provider
        register_provider_metrics(provider)
        
        # Save to database (async)
        asyncio.create_task(self.save_provider_to_database(provider))
        
        return provider
    
    async def unregister_provider(self, provider_id: str) -> bool:
        """Unregister a provider"""
        if provider_id not in self.providers:
            return False
        
        provider = self.providers[provider_id]
        
        # Update provider status in metrics
        update_provider_status(provider_id, provider.provider_type, False)
        
        # Remove from registry
        del self.providers[provider_id]
        
        # Remove from database
        if self.provider_repository:
            try:
                existing_config = await self.provider_repository.get_by_provider_id(provider_id)
                if existing_config:
                    await self.provider_repository.delete(existing_config.id)
                    logger.info(f"Removed provider {provider_id} from database")
            except Exception as e:
                logger.error(f"Failed to remove provider {provider_id} from database: {str(e)}")
        
        return True

    def get_provider(self, provider_id: str) -> Optional[ModelProvider]:
        """Get a provider by ID.
        
        Args:
            provider_id: ID of the provider to retrieve.
            
        Returns:
            The provider if found, None otherwise.
        """
        if provider_id not in self.providers:
            return None
            
        return self.providers[provider_id]

    def list_providers(self, include_inactive: bool = False) -> List[ModelProvider]:
        """List all registered providers.
        
        Args:
            include_inactive: Whether to include inactive providers.
            
        Returns:
            List of providers.
        """
        providers = self.providers.values()
        if not include_inactive:
            providers = [p for p in providers if p.is_initialized]
        return list(providers)

    def update_provider(self, provider_id: str, **kwargs) -> bool:
        """Update a provider's configuration"""
        if provider_id not in self.providers:
            return False
            
        provider = self.providers[provider_id]
        update_data = provider.model_dump()
        update_data.update(kwargs)
        
        # Encrypt sensitive data before updating
        if "api_key" in kwargs:
            update_data = encrypt_dict(update_data, ["api_key"])
            
        self.providers[provider_id] = ModelProvider(**update_data)
        
        # Update provider metrics
        register_provider_metrics(self.providers[provider_id])
        
        return True

    def get_capabilities(self, provider_id: str) -> List[ModelCapability]:
        """Get capabilities for a provider.
        
        Args:
            provider_id: ID of the provider.
            
        Returns:
            List of capabilities.
        """
        provider = self.get_provider(provider_id)
        if provider:
            return list(provider.capabilities_scores.keys())
        else:
            return []

    def test_provider(self, provider_id: str) -> Dict[str, Any]:
        """Test a provider's connection and capabilities.
        
        Args:
            provider_id: ID of the provider to test.
            
        Returns:
            Dictionary containing test results.
        """
        provider = self.get_provider(provider_id)
        if not provider:
            return {
                "success": False,
                "message": f"Provider {provider_id} not found",
                "capabilities_tested": [],
                "errors": ["Provider not found"]
            }
            
        # TODO: Implement actual provider testing
        # This is a placeholder implementation
        return {
            "success": True,
            "message": "Provider test successful",
            "capabilities_tested": ["text_generation", "planning"],
            "errors": []
        }

    def get_provider_for_capability(
        self,
        capability: ProviderCapability,
        context: Optional[Dict] = None
    ) -> Optional[ModelProvider]:
        """Get the best provider for a specific capability using scoring"""
        context = context or {}
        available_providers = [
            provider for provider in self.providers.values()
            if capability in self.get_capabilities(provider.provider_id)
        ]
        
        if not available_providers:
            return None
            
        # Score each provider
        provider_scores = []
        for provider in available_providers:
            score = self._calculate_provider_score(provider, capability, context)
            provider_scores.append((provider, score))
            
        # Sort by score and select the best provider
        provider_scores.sort(key=lambda x: x[1], reverse=True)
        best_provider = provider_scores[0][0]
        
        # Update rotation tracking
        self._update_provider_rotation(best_provider.provider_id)
        
        return best_provider
    
    def _calculate_provider_score(
        self,
        provider: ModelProvider,
        capability: ProviderCapability,
        context: Dict
    ) -> float:
        """Calculate a score for provider selection"""
        metrics = self.performance[provider.provider_id]
        
        # Base score components
        capability_match = 1.0 if capability in self.get_capabilities(provider.provider_id) else 0.0
        success_rate = metrics.success_rate
        latency_score = 1.0 / (1.0 + metrics.average_latency)  # Lower latency = higher score
        cost_score = 1.0 / (1.0 + metrics.average_cost)  # Lower cost = higher score
        availability_score = 1.0 if metrics.consecutive_failures < 3 else 0.0
        
        # Load balancing factor
        last_used = self.last_used.get(provider.provider_id, datetime.min)
        time_since_last_use = (datetime.utcnow() - last_used).total_seconds()
        load_balance_score = min(1.0, time_since_last_use / 3600)  # Normalize to 1 hour
        
        # Weighted scoring
        weights = {
            'capability': 0.3,
            'success': 0.2,
            'latency': 0.2,
            'cost': 0.15,
            'availability': 0.1,
            'load_balance': 0.05
        }
        
        score = (
            weights['capability'] * capability_match +
            weights['success'] * success_rate +
            weights['latency'] * latency_score +
            weights['cost'] * cost_score +
            weights['availability'] * availability_score +
            weights['load_balance'] * load_balance_score
        )
        
        return score
    
    def _update_provider_rotation(self, provider_id: str) -> None:
        """Update provider rotation tracking"""
        self.last_used[provider_id] = datetime.utcnow()
        
        # Update rotation list
        if provider_id in self.provider_rotation:
            self.provider_rotation[provider_id].append(datetime.utcnow().isoformat())
            # Keep only last 100 uses
            self.provider_rotation[provider_id] = self.provider_rotation[provider_id][-100:]
    
    def update_metrics(
        self,
        provider_id: str,
        success: bool,
        latency: float,
        cost: float
    ) -> None:
        """Update provider metrics"""
        metrics = self.performance[provider_id]
        metrics.total_requests += 1
        
        if success:
            metrics.success_count += 1
            metrics.last_success = datetime.utcnow()
            metrics.consecutive_failures = 0
        else:
            metrics.failure_count += 1
            metrics.last_failure = datetime.utcnow()
            metrics.consecutive_failures += 1
            
        metrics.total_latency += latency
        metrics.total_cost += cost
    
    def get_fallback_provider(
        self,
        capability: ProviderCapability,
        failed_provider_id: str
    ) -> Optional[ModelProvider]:
        """Get a fallback provider when the primary provider fails"""
        # Get the fallback chain for the failed provider
        fallback_chain = self.fallback_chains.get(failed_provider_id, [])
        
        # Try each provider in the fallback chain
        for provider_id in fallback_chain:
            provider = self.get_provider(provider_id)
            if provider and capability in self.get_capabilities(provider.provider_id):
                return provider
                
        # If no fallback chain exists or all fallbacks failed,
        # try to find any available provider with the capability
        return self.get_provider_for_capability(capability)
    
    def set_fallback_chain(
        self,
        provider_id: str,
        fallback_chain: List[str]
    ) -> None:
        """Set the fallback chain for a provider"""
        self.fallback_chains[provider_id] = fallback_chain
    
    def get_provider_stats(self, provider_id: str) -> Dict:
        """Get statistics for a provider"""
        metrics = self.performance.get(provider_id)
        if not metrics:
            return {}
            
        return {
            "success_rate": metrics.success_rate,
            "average_latency": metrics.average_latency,
            "average_cost": metrics.average_cost,
            "total_requests": metrics.total_requests,
            "consecutive_failures": metrics.consecutive_failures,
            "last_success": metrics.last_success.isoformat() if metrics.last_success else None,
            "last_failure": metrics.last_failure.isoformat() if metrics.last_failure else None
        }
    
    def get_rotation_stats(self, provider_id: str) -> Dict:
        """Get rotation statistics for a provider"""
        rotation = self.provider_rotation.get(provider_id, [])
        if not rotation:
            return {}
            
        # Calculate time between uses
        use_times = [datetime.fromisoformat(t) for t in rotation]
        time_diffs = [
            (use_times[i] - use_times[i-1]).total_seconds()
            for i in range(1, len(use_times))
        ]
        
        return {
            "total_uses": len(rotation),
            "average_time_between_uses": statistics.mean(time_diffs) if time_diffs else 0,
            "last_used": rotation[-1] if rotation else None
        }

# Create global instance
provider_registry = ProviderRegistry() 