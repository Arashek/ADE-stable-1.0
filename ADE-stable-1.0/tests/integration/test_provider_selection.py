import pytest
from unittest import mock
import random

from src.core.models.provider_registry import (
    ProviderRegistry, ModelProvider, ModelCapability, 
    ProviderSelector, ProviderPerformance
)

# Mock provider classes
class MockOpenAIProvider(ModelProvider):
    @property
    def provider_type(self) -> str:
        return "openai"
    
    def initialize(self) -> bool:
        self.is_initialized = True
        return True
    
    def list_available_models(self) -> list:
        return ["gpt-4"]
    
    def get_capabilities(self) -> list:
        return [
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CHAT
        ]
    
    async def generate(self, prompt, model=None, parameters=None, images=None):
        return "OpenAI response"

class MockAnthropicProvider(ModelProvider):
    @property
    def provider_type(self) -> str:
        return "anthropic"
    
    def initialize(self) -> bool:
        self.is_initialized = True
        return True
    
    def list_available_models(self) -> list:
        return ["claude-3"]
    
    def get_capabilities(self) -> list:
        return [
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CHAT,
            ModelCapability.IMAGE_UNDERSTANDING
        ]
    
    async def generate(self, prompt, model=None, parameters=None, images=None):
        return "Anthropic response"

class MockLocalProvider(ModelProvider):
    @property
    def provider_type(self) -> str:
        return "local"
    
    def initialize(self) -> bool:
        self.is_initialized = True
        return True
    
    def list_available_models(self) -> list:
        return ["local-model"]
    
    def get_capabilities(self) -> list:
        return [
            ModelCapability.CODE_GENERATION,
            ModelCapability.CHAT
        ]
    
    async def generate(self, prompt, model=None, parameters=None, images=None):
        return "Local response"

# Test provider selection
@pytest.fixture
def provider_registry():
    """Create a provider registry with mock providers"""
    registry = ProviderRegistry()
    
    # Register provider classes
    registry.register_provider_class("openai", MockOpenAIProvider)
    registry.register_provider_class("anthropic", MockAnthropicProvider)
    registry.register_provider_class("local", MockLocalProvider)
    
    # Create providers
    openai_provider = MockOpenAIProvider("test-openai-key", "openai-provider")
    anthropic_provider = MockAnthropicProvider("test-anthropic-key", "anthropic-provider")
    local_provider = MockLocalProvider("test-local-key", "local-provider")
    
    # Configure capabilities and performance
    openai_provider.set_capability_scores({
        ModelCapability.CODE_GENERATION: 0.9,
        ModelCapability.REASONING: 0.95,
        ModelCapability.CHAT: 0.9
    })
    openai_provider.performance.record_success(200, 500)  # 200ms, 500 tokens
    
    anthropic_provider.set_capability_scores({
        ModelCapability.CODE_GENERATION: 0.85,
        ModelCapability.REASONING: 0.9,
        ModelCapability.CHAT: 0.85,
        ModelCapability.IMAGE_UNDERSTANDING: 0.9
    })
    anthropic_provider.performance.record_success(250, 600)  # 250ms, 600 tokens
    
    local_provider.set_capability_scores({
        ModelCapability.CODE_GENERATION: 0.7,
        ModelCapability.CHAT: 0.7
    })
    local_provider.performance.record_success(100, 300)  # 100ms, 300 tokens
    
    # Add providers to registry
    registry.providers = {
        "openai-provider": openai_provider,
        "anthropic-provider": anthropic_provider,
        "local-provider": local_provider
    }
    
    return registry

def test_provider_selection_performance(provider_registry):
    """Test provider selection using performance strategy"""
    # Configure selector for performance
    provider_registry.provider_selector = ProviderSelector(strategy="performance")
    
    # Test code generation selection
    provider = provider_registry.get_provider_for_capability(ModelCapability.CODE_GENERATION)
    assert provider.provider_id == "openai-provider"
    
    # Test image understanding selection
    provider = provider_registry.get_provider_for_capability(ModelCapability.IMAGE_UNDERSTANDING)
    assert provider.provider_id == "anthropic-provider"
    
    # Test fallback for unsupported capability
    provider = provider_registry.get_provider_for_capability(ModelCapability.DOCUMENTATION)
    assert provider is not None  # Should get a fallback

def test_provider_selection_cost(provider_registry):
    """Test provider selection using cost strategy"""
    # Configure selector for cost
    provider_registry.provider_selector = ProviderSelector(strategy="cost")
    
    # Test code generation selection (should pick local as cheapest)
    provider = provider_registry.get_provider_for_capability(ModelCapability.CODE_GENERATION)
    assert provider.provider_id == "local-provider"
    
    # Test reasoning selection (local doesn't support it, should pick next cheapest)
    provider = provider_registry.get_provider_for_capability(ModelCapability.REASONING)
    assert provider.provider_id in ["openai-provider", "anthropic-provider"]

def test_provider_selection_balanced(provider_registry):
    """Test provider selection using balanced strategy"""
    # Configure selector for balanced approach
    provider_registry.provider_selector = ProviderSelector(strategy="balanced")
    
    # Fix random seed for consistent testing
    random.seed(42)
    
    # Test code generation selection multiple times
    providers_selected = set()
    for _ in range(10):
        provider = provider_registry.get_provider_for_capability(ModelCapability.CODE_GENERATION)
        providers_selected.add(provider.provider_id)
    
    # Should have selected at least 2 different providers due to randomization
    assert len(providers_selected) >= 2

def test_provider_selection_with_failures(provider_registry):
    """Test provider selection when some providers have failures"""
    # Mark openai provider as having failures
    openai_provider = provider_registry.providers["openai-provider"]
    openai_provider.performance.record_failure(500)
    openai_provider.performance.record_failure(500)
    openai_provider.performance.record_failure(500)
    openai_provider.performance.record_failure(500)  # 4 consecutive failures
    
    # Configure for performance
    provider_registry.provider_selector = ProviderSelector(strategy="performance")
    
    # Should pick anthropic now for code generation
    provider = provider_registry.get_provider_for_capability(ModelCapability.CODE_GENERATION)
    assert provider.provider_id == "anthropic-provider"

def test_provider_selection_with_capability_weights(provider_registry):
    """Test provider selection with weighted capabilities"""
    # Configure selector with custom weights
    provider_registry.provider_selector = ProviderSelector(
        strategy="performance",
        capability_weights={
            ModelCapability.CODE_GENERATION: 0.6,
            ModelCapability.REASONING: 0.4
        }
    )
    
    # Test selection with weighted capabilities
    provider = provider_registry.get_provider_for_capability(ModelCapability.CODE_GENERATION)
    assert provider.provider_id == "openai-provider"  # Best for code generation

def test_provider_selection_with_rate_limits(provider_registry):
    """Test provider selection considering rate limits"""
    # Mark providers as rate limited
    openai_provider = provider_registry.providers["openai-provider"]
    openai_provider.is_rate_limited = True
    
    # Configure for performance
    provider_registry.provider_selector = ProviderSelector(strategy="performance")
    
    # Should pick anthropic now due to rate limit
    provider = provider_registry.get_provider_for_capability(ModelCapability.CODE_GENERATION)
    assert provider.provider_id == "anthropic-provider"

def test_provider_selection_with_multiple_capabilities(provider_registry):
    """Test provider selection for multiple capabilities"""
    # Configure selector for balanced approach
    provider_registry.provider_selector = ProviderSelector(strategy="balanced")
    
    # Test selection for multiple capabilities
    capabilities = [
        ModelCapability.CODE_GENERATION,
        ModelCapability.REASONING,
        ModelCapability.CHAT
    ]
    
    provider = provider_registry.get_provider_for_capabilities(capabilities)
    assert provider.provider_id in ["openai-provider", "anthropic-provider"]  # Both support all capabilities 