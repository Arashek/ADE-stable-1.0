import pytest
from unittest.mock import patch, MagicMock, call

from core.models.provider_registry import ProviderRegistry, ModelProvider, ProviderCapability
from core.models.providers import OpenAIProvider, AnthropicProvider, GoogleAIProvider
from core.models.provider_factory import ProviderFactory
from core.models.types import ModelCapability

class TestProviderRegistry:
    """Test cases for the Provider Registry"""
    
    def test_registry_initialization(self):
        """Test that the registry initializes with empty providers"""
        registry = ProviderRegistry()
        assert len(registry.providers) == 0
    
    def test_register_provider(self):
        """Test registering a new provider"""
        registry = ProviderRegistry()
        
        # Create a mock provider
        provider = MagicMock(spec=ModelProvider)
        provider.name = "test_provider"
        provider.capabilities = {ProviderCapability.TEXT_GENERATION}
        
        # Register the provider
        registry.register_provider(provider)
        
        # Check that the provider was registered
        assert len(registry.providers) == 1
        assert "test_provider" in registry.providers
        assert registry.providers["test_provider"] == provider
    
    def test_get_provider_by_name(self):
        """Test retrieving a provider by name"""
        registry = ProviderRegistry()
        
        # Create a mock provider
        provider = MagicMock(spec=ModelProvider)
        provider.name = "test_provider"
        provider.capabilities = {ProviderCapability.TEXT_GENERATION}
        
        # Register the provider
        registry.register_provider(provider)
        
        # Retrieve the provider
        result = registry.get_provider("test_provider")
        
        # Check the result
        assert result == provider
    
    def test_get_provider_by_name_nonexistent(self):
        """Test retrieving a non-existent provider by name"""
        registry = ProviderRegistry()
        
        # Retrieve a non-existent provider
        result = registry.get_provider("nonexistent")
        
        # Check the result
        assert result is None
    
    def test_get_provider_for_capability(self):
        """Test retrieving a provider for a specific capability"""
        registry = ProviderRegistry()
        
        # Create mock providers with different capabilities
        text_provider = MagicMock(spec=ModelProvider)
        text_provider.name = "text_provider"
        text_provider.capabilities = {ProviderCapability.TEXT_GENERATION}
        text_provider.has_capability.side_effect = lambda cap: cap == ProviderCapability.TEXT_GENERATION
        
        code_provider = MagicMock(spec=ModelProvider)
        code_provider.name = "code_provider"
        code_provider.capabilities = {ProviderCapability.CODE_GENERATION}
        code_provider.has_capability.side_effect = lambda cap: cap == ProviderCapability.CODE_GENERATION
        
        # Register the providers
        registry.register_provider(text_provider)
        registry.register_provider(code_provider)
        
        # Retrieve a provider for a specific capability
        text_result = registry.get_provider_for_capability(ProviderCapability.TEXT_GENERATION)
        code_result = registry.get_provider_for_capability(ProviderCapability.CODE_GENERATION)
        
        # Check the results
        assert text_result == text_provider
        assert code_result == code_provider
        
        # Verify the has_capability method was called
        text_provider.has_capability.assert_any_call(ProviderCapability.TEXT_GENERATION)
        code_provider.has_capability.assert_any_call(ProviderCapability.CODE_GENERATION)
    
    def test_get_provider_for_capability_nonexistent(self):
        """Test retrieving a provider for a capability that no provider supports"""
        registry = ProviderRegistry()
        
        # Create a mock provider with limited capabilities
        provider = MagicMock(spec=ModelProvider)
        provider.name = "test_provider"
        provider.capabilities = {ProviderCapability.TEXT_GENERATION}
        provider.has_capability.return_value = False
        
        # Register the provider
        registry.register_provider(provider)
        
        # Retrieve a provider for an unsupported capability
        result = registry.get_provider_for_capability(ProviderCapability.AUDIO_TRANSCRIPTION)
        
        # Check the result
        assert result is None
        
        # Verify the has_capability method was called
        provider.has_capability.assert_called_with(ProviderCapability.AUDIO_TRANSCRIPTION)
    
    def test_execute_with_capability(self):
        """Test executing a request with a specific capability"""
        registry = ProviderRegistry()
        
        # Create a mock provider
        provider = MagicMock(spec=ModelProvider)
        provider.name = "test_provider"
        provider.capabilities = {ProviderCapability.TEXT_GENERATION}
        provider.has_capability.return_value = True
        provider.execute.return_value = "Mock response"
        
        # Register the provider
        registry.register_provider(provider)
        
        # Execute a request
        result = registry.execute_with_capability(
            capability=ProviderCapability.TEXT_GENERATION,
            prompt="Test prompt",
            temperature=0.5
        )
        
        # Check the result
        assert result == "Mock response"
        
        # Verify the methods were called
        provider.has_capability.assert_called_with(ProviderCapability.TEXT_GENERATION)
        provider.execute.assert_called_with(prompt="Test prompt", temperature=0.5)
    
    def test_execute_with_capability_no_provider(self):
        """Test executing a request with a capability that no provider supports"""
        registry = ProviderRegistry()
        
        # Execute a request with no providers registered
        result = registry.execute_with_capability(
            capability=ProviderCapability.TEXT_GENERATION,
            prompt="Test prompt"
        )
        
        # Check the result
        assert result is None

class TestProviderFactory:
    """Test cases for the Provider Factory"""
    
    def test_create_openai_provider(self):
        """Test creating an OpenAI provider"""
        config = {
            "api_key": "test-api-key",
            "model": "gpt-4"
        }
        
        provider = ProviderFactory.create_provider("openai", config)
        
        assert isinstance(provider, OpenAIProvider)
        assert provider.name == "openai"
        assert provider.api_key == "test-api-key"
        assert provider.model == "gpt-4"
        assert ProviderCapability.TEXT_GENERATION in provider.capabilities
        assert ProviderCapability.CODE_GENERATION in provider.capabilities
    
    def test_create_anthropic_provider(self):
        """Test creating an Anthropic provider"""
        config = {
            "api_key": "test-api-key",
            "model": "claude-3-sonnet"
        }
        
        provider = ProviderFactory.create_provider("anthropic", config)
        
        assert isinstance(provider, AnthropicProvider)
        assert provider.name == "anthropic"
        assert provider.api_key == "test-api-key"
        assert provider.model == "claude-3-sonnet"
        assert ProviderCapability.TEXT_GENERATION in provider.capabilities
        assert ProviderCapability.CODE_GENERATION in provider.capabilities
    
    def test_create_google_provider(self):
        """Test creating a Google provider"""
        config = {
            "api_key": "test-api-key",
            "model": "gemini-pro"
        }
        
        provider = ProviderFactory.create_provider("google", config)
        
        assert isinstance(provider, GoogleAIProvider)
        assert provider.name == "google"
        assert provider.api_key == "test-api-key"
        assert provider.model == "gemini-pro"
        assert ProviderCapability.TEXT_GENERATION in provider.capabilities
        assert ProviderCapability.IMAGE_UNDERSTANDING in provider.capabilities
    
    def test_create_provider_no_api_key(self):
        """Test creating a provider with no API key"""
        config = {
            "model": "gpt-4"
        }
        
        provider = ProviderFactory.create_provider("openai", config)
        
        assert provider is None
    
    def test_create_provider_unsupported_type(self):
        """Test creating a provider with an unsupported type"""
        config = {
            "api_key": "test-api-key",
            "model": "test-model"
        }
        
        provider = ProviderFactory.create_provider("unsupported", config)
        
        assert provider is None
    
    def test_create_registry_from_config(self):
        """Test creating a registry from configuration"""
        config = {
            "providers": {
                "openai": {
                    "enabled": True,
                    "api_key": "openai-api-key",
                    "model": "gpt-4"
                },
                "anthropic": {
                    "enabled": True,
                    "api_key": "anthropic-api-key",
                    "model": "claude-3-opus"
                }
            }
        }
        
        with patch("core.models.provider_factory.ProviderFactory.create_provider") as mock_create:
            # Set up the mock to return mock providers
            openai_provider = MagicMock(spec=OpenAIProvider)
            openai_provider.name = "openai"
            
            anthropic_provider = MagicMock(spec=AnthropicProvider)
            anthropic_provider.name = "anthropic"
            
            mock_create.side_effect = lambda provider_type, provider_config: {
                "openai": openai_provider,
                "anthropic": anthropic_provider
            }.get(provider_type)
            
            # Create the registry
            registry = ProviderFactory.create_registry_from_config(config)
            
            # Check that the providers were registered
            assert len(registry.providers) == 2
            assert "openai" in registry.providers
            assert "anthropic" in registry.providers
            assert registry.providers["openai"] == openai_provider
            assert registry.providers["anthropic"] == anthropic_provider
            
            # Verify the create_provider method was called
            assert mock_create.call_count == 2
            mock_create.assert_any_call("openai", {
                "enabled": True,
                "api_key": "openai-api-key",
                "model": "gpt-4"
            })
            mock_create.assert_any_call("anthropic", {
                "enabled": True,
                "api_key": "anthropic-api-key",
                "model": "claude-3-opus"
            })
    
    def test_create_registry_with_disabled_provider(self):
        """Test creating a registry with a disabled provider"""
        config = {
            "providers": {
                "openai": {
                    "enabled": True,
                    "api_key": "openai-api-key",
                    "model": "gpt-4"
                },
                "anthropic": {
                    "enabled": False,
                    "api_key": "anthropic-api-key",
                    "model": "claude-3-opus"
                }
            }
        }
        
        with patch("core.models.provider_factory.ProviderFactory.create_provider") as mock_create:
            # Set up the mock to return a mock provider only for OpenAI
            openai_provider = MagicMock(spec=OpenAIProvider)
            openai_provider.name = "openai"
            
            mock_create.side_effect = lambda provider_type, provider_config: {
                "openai": openai_provider
            }.get(provider_type)
            
            # Create the registry
            registry = ProviderFactory.create_registry_from_config(config)
            
            # Check that only the enabled provider was registered
            assert len(registry.providers) == 1
            assert "openai" in registry.providers
            assert "anthropic" not in registry.providers
            assert registry.providers["openai"] == openai_provider
            
            # Verify the create_provider method was called only for the enabled provider
            mock_create.assert_called_once_with("openai", {
                "enabled": True,
                "api_key": "openai-api-key",
                "model": "gpt-4"
            }) 