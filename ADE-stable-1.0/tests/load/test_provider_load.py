import pytest
import asyncio
import time
import random
from concurrent.futures import ThreadPoolExecutor
from unittest import mock

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

# Load test configuration
NUM_CONCURRENT_REQUESTS = 50
NUM_REQUESTS_PER_CLIENT = 10
CAPABILITIES_TO_TEST = [
    ModelCapability.CODE_GENERATION,
    ModelCapability.REASONING,
    ModelCapability.CHAT,
    ModelCapability.IMAGE_UNDERSTANDING
]

@pytest.fixture
def provider_registry():
    """Create a provider registry with mock providers for load testing"""
    registry = ProviderRegistry()
    
    # Register provider classes
    registry.register_provider_class("openai", MockOpenAIProvider)
    registry.register_provider_class("anthropic", MockAnthropicProvider)
    registry.register_provider_class("local", MockLocalProvider)
    
    # Create providers with varying performance characteristics
    providers = {
        "openai": MockOpenAIProvider("test-openai-key", "openai-provider"),
        "anthropic": MockAnthropicProvider("test-anthropic-key", "anthropic-provider"),
        "local": MockLocalProvider("test-local-key", "local-provider")
    }
    
    # Configure capabilities and performance for each provider
    for provider_id, provider in providers.items():
        # Set capability scores
        if provider_id == "openai":
            provider.set_capability_scores({
                ModelCapability.CODE_GENERATION: 0.9,
                ModelCapability.REASONING: 0.95,
                ModelCapability.CHAT: 0.9
            })
            # Record some initial performance metrics
            for _ in range(5):
                provider.performance.record_success(200, 500)
        elif provider_id == "anthropic":
            provider.set_capability_scores({
                ModelCapability.CODE_GENERATION: 0.85,
                ModelCapability.REASONING: 0.9,
                ModelCapability.CHAT: 0.85,
                ModelCapability.IMAGE_UNDERSTANDING: 0.9
            })
            for _ in range(5):
                provider.performance.record_success(250, 600)
        else:  # local
            provider.set_capability_scores({
                ModelCapability.CODE_GENERATION: 0.7,
                ModelCapability.CHAT: 0.7
            })
            for _ in range(5):
                provider.performance.record_success(100, 300)
    
    # Add providers to registry
    registry.providers = {
        provider.provider_id: provider 
        for provider in providers.values()
    }
    
    return registry

async def simulate_client_requests(registry, client_id, num_requests):
    """Simulate requests from a single client"""
    results = []
    for i in range(num_requests):
        # Select random capability to test
        capability = random.choice(CAPABILITIES_TO_TEST)
        
        start_time = time.time()
        provider = registry.get_provider_for_capability(capability)
        selection_time = time.time() - start_time
        
        # Record result
        results.append({
            "client_id": client_id,
            "request_id": i,
            "capability": capability.value,
            "selected_provider": provider.provider_id if provider else None,
            "selection_time_ms": selection_time * 1000
        })
        
        # Small delay to simulate thinking time
        await asyncio.sleep(0.01)
    
    return results

@pytest.mark.asyncio
async def test_provider_selection_under_load(provider_registry):
    """Test provider selection under concurrent load"""
    # Create tasks to simulate multiple clients
    tasks = []
    for client_id in range(NUM_CONCURRENT_REQUESTS):
        task = asyncio.create_task(
            simulate_client_requests(
                provider_registry, 
                client_id, 
                NUM_REQUESTS_PER_CLIENT
            )
        )
        tasks.append(task)
    
    # Wait for all clients to complete
    results = await asyncio.gather(*tasks)
    
    # Flatten results
    all_results = [item for sublist in results for item in sublist]
    
    # Calculate metrics
    total_requests = len(all_results)
    successful_selections = sum(1 for r in all_results if r["selected_provider"] is not None)
    selection_times = [r["selection_time_ms"] for r in all_results]
    avg_selection_time = sum(selection_times) / len(selection_times)
    max_selection_time = max(selection_times)
    
    # Check results
    assert successful_selections == total_requests
    assert avg_selection_time < 10  # Should be very fast for mock providers
    
    # Analyze provider distribution
    provider_counts = {}
    for result in all_results:
        provider_id = result["selected_provider"]
        if provider_id not in provider_counts:
            provider_counts[provider_id] = 0
        provider_counts[provider_id] += 1
    
    # Assert that all providers got some traffic
    assert len(provider_counts) >= 2
    
    # Print load test results for analysis
    print(f"Load test completed: {total_requests} total requests")
    print(f"Average selection time: {avg_selection_time:.2f}ms")
    print(f"Max selection time: {max_selection_time:.2f}ms")
    print(f"Provider distribution: {provider_counts}")

@pytest.mark.asyncio
async def test_provider_selection_with_rate_limits_under_load(provider_registry):
    """Test provider selection under load with rate limits"""
    # Mark some providers as rate limited
    openai_provider = provider_registry.providers["openai-provider"]
    openai_provider.is_rate_limited = True
    
    # Run load test
    tasks = []
    for client_id in range(NUM_CONCURRENT_REQUESTS):
        task = asyncio.create_task(
            simulate_client_requests(
                provider_registry, 
                client_id, 
                NUM_REQUESTS_PER_CLIENT
            )
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    all_results = [item for sublist in results for item in sublist]
    
    # Analyze provider distribution
    provider_counts = {}
    for result in all_results:
        provider_id = result["selected_provider"]
        if provider_id not in provider_counts:
            provider_counts[provider_id] = 0
        provider_counts[provider_id] += 1
    
    # Assert that rate-limited provider got less traffic
    assert provider_counts.get("openai-provider", 0) < provider_counts.get("anthropic-provider", 0)

@pytest.mark.asyncio
async def test_provider_selection_with_failures_under_load(provider_registry):
    """Test provider selection under load with failures"""
    # Record some failures for OpenAI provider
    openai_provider = provider_registry.providers["openai-provider"]
    for _ in range(5):
        openai_provider.performance.record_failure(500)
    
    # Run load test
    tasks = []
    for client_id in range(NUM_CONCURRENT_REQUESTS):
        task = asyncio.create_task(
            simulate_client_requests(
                provider_registry, 
                client_id, 
                NUM_REQUESTS_PER_CLIENT
            )
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    all_results = [item for sublist in results for item in sublist]
    
    # Analyze provider distribution
    provider_counts = {}
    for result in all_results:
        provider_id = result["selected_provider"]
        if provider_id not in provider_counts:
            provider_counts[provider_id] = 0
        provider_counts[provider_id] += 1
    
    # Assert that failed provider got less traffic
    assert provider_counts.get("openai-provider", 0) < provider_counts.get("anthropic-provider", 0) 