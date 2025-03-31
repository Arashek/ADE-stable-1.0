import pytest
from unittest.mock import Mock, patch
from src.core.providers import (
    ProviderRegistry,
    ProviderConfig,
    Capability,
    BaseProviderAdapter,
    AuthenticationError
)

class TestProviderRegistry:
    def test_init_creates_default_providers(self):
        """Test that the registry initializes with default providers"""
        registry = ProviderRegistry()
        assert "openai" in registry.providers
        assert "anthropic" in registry.providers
        assert "google" in registry.providers
        assert "local" in registry.providers
        
        # Check that local is enabled by default
        assert registry.providers["local"].enabled is True
    
    def test_register_provider(self):
        """Test registering a new provider"""
        registry = ProviderRegistry()
        config = ProviderConfig(enabled=True)
        mock_adapter = Mock(spec=BaseProviderAdapter)
        
        # Register new provider
        success = registry.register_provider("test_provider", config, mock_adapter)
        assert success is True
        assert "test_provider" in registry.providers
        assert registry.providers["test_provider"] == config
        assert registry._adapter_classes["test_provider"] == mock_adapter
    
    def test_register_provider_overwrites_existing(self):
        """Test that registering an existing provider overwrites it"""
        registry = ProviderRegistry()
        config1 = ProviderConfig(enabled=True)
        config2 = ProviderConfig(enabled=False)
        mock_adapter1 = Mock(spec=BaseProviderAdapter)
        mock_adapter2 = Mock(spec=BaseProviderAdapter)
        
        # Register provider twice
        registry.register_provider("test_provider", config1, mock_adapter1)
        registry.register_provider("test_provider", config2, mock_adapter2)
        
        assert registry.providers["test_provider"] == config2
        assert registry._adapter_classes["test_provider"] == mock_adapter2
    
    def test_configure_provider(self):
        """Test configuring an existing provider"""
        registry = ProviderRegistry()
        
        # Configure OpenAI provider
        updates = {
            "enabled": True,
            "priority": 1,
            "fallback": "anthropic"
        }
        
        success = registry.configure_provider("openai", updates)
        assert success is True
        assert registry.providers["openai"].enabled is True
        assert registry.providers["openai"].priority == 1
        assert registry.providers["openai"].fallback == "anthropic"
    
    def test_configure_nonexistent_provider(self):
        """Test that configuring a non-existent provider fails"""
        registry = ProviderRegistry()
        success = registry.configure_provider("nonexistent", {"enabled": True})
        assert success is False
    
    def test_get_provider(self):
        """Test getting an initialized provider adapter"""
        registry = ProviderRegistry()
        config = ProviderConfig(enabled=True)
        mock_adapter_class = Mock(spec=BaseProviderAdapter)
        mock_adapter_instance = Mock(spec=BaseProviderAdapter)
        mock_adapter_class.return_value = mock_adapter_instance
        
        # Register provider
        registry.register_provider("test_provider", config, mock_adapter_class)
        
        # Get provider
        adapter = registry.get_provider("test_provider")
        assert adapter == mock_adapter_instance
        mock_adapter_class.assert_called_once_with(config)
    
    def test_get_provider_caches_instance(self):
        """Test that get_provider caches the adapter instance"""
        registry = ProviderRegistry()
        config = ProviderConfig(enabled=True)
        mock_adapter_class = Mock(spec=BaseProviderAdapter)
        mock_adapter_instance = Mock(spec=BaseProviderAdapter)
        mock_adapter_class.return_value = mock_adapter_instance
        
        registry.register_provider("test_provider", config, mock_adapter_class)
        
        # Get provider twice
        adapter1 = registry.get_provider("test_provider")
        adapter2 = registry.get_provider("test_provider")
        
        assert adapter1 == adapter2
        mock_adapter_class.assert_called_once()  # Should only be called once
    
    def test_get_provider_initialization_error(self):
        """Test that get_provider handles initialization errors"""
        registry = ProviderRegistry()
        config = ProviderConfig(enabled=True)
        mock_adapter_class = Mock(spec=BaseProviderAdapter)
        mock_adapter_class.side_effect = AuthenticationError("Invalid API key")
        
        registry.register_provider("test_provider", config, mock_adapter_class)
        
        adapter = registry.get_provider("test_provider")
        assert adapter is None
    
    def test_get_available_providers(self):
        """Test getting list of available providers"""
        registry = ProviderRegistry()
        providers = registry.get_available_providers()
        
        assert isinstance(providers, list)
        assert "openai" in providers
        assert "anthropic" in providers
        assert "google" in providers
        assert "local" in providers
    
    def test_get_provider_capabilities(self):
        """Test getting capabilities of a provider"""
        registry = ProviderRegistry()
        config = ProviderConfig(enabled=True)
        mock_adapter = Mock(spec=BaseProviderAdapter)
        mock_capabilities = {
            Capability.TEXT_GENERATION: 1.0,
            Capability.CODE_GENERATION: 0.9
        }
        mock_adapter.get_capabilities.return_value = mock_capabilities
        
        registry.register_provider("test_provider", config, mock_adapter)
        registry._adapter_instances["test_provider"] = mock_adapter
        
        capabilities = registry.get_provider_capabilities("test_provider")
        assert capabilities == mock_capabilities
    
    def test_get_best_provider(self):
        """Test finding the best provider for given capabilities"""
        registry = ProviderRegistry()
        
        # Set up two providers with different capabilities
        provider1_config = ProviderConfig(enabled=True)
        provider1_adapter = Mock(spec=BaseProviderAdapter)
        provider1_adapter.get_capabilities.return_value = {
            Capability.TEXT_GENERATION: 1.0,
            Capability.CODE_GENERATION: 0.5
        }
        
        provider2_config = ProviderConfig(enabled=True)
        provider2_adapter = Mock(spec=BaseProviderAdapter)
        provider2_adapter.get_capabilities.return_value = {
            Capability.TEXT_GENERATION: 0.8,
            Capability.CODE_GENERATION: 0.9
        }
        
        registry.register_provider("provider1", provider1_config, provider1_adapter)
        registry.register_provider("provider2", provider2_config, provider2_adapter)
        registry._adapter_instances["provider1"] = provider1_adapter
        registry._adapter_instances["provider2"] = provider2_adapter
        
        # Test finding best provider for text generation
        best_text = registry.get_best_provider([Capability.TEXT_GENERATION])
        assert best_text[0] == "provider1"  # Higher text generation score
        
        # Test finding best provider for code generation
        best_code = registry.get_best_provider([Capability.CODE_GENERATION])
        assert best_code[0] == "provider2"  # Higher code generation score
    
    def test_remove_provider(self):
        """Test removing a provider"""
        registry = ProviderRegistry()
        config = ProviderConfig(enabled=True)
        mock_adapter = Mock(spec=BaseProviderAdapter)
        
        # Register and then remove provider
        registry.register_provider("test_provider", config, mock_adapter)
        success = registry.remove_provider("test_provider")
        
        assert success is True
        assert "test_provider" not in registry.providers
        assert "test_provider" not in registry._adapter_classes
        assert "test_provider" not in registry._adapter_instances
    
    def test_remove_nonexistent_provider(self):
        """Test that removing a non-existent provider fails gracefully"""
        registry = ProviderRegistry()
        success = registry.remove_provider("nonexistent")
        assert success is False


