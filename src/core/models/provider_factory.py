from typing import Dict, Optional, Any
import logging

from .provider_registry import ProviderRegistry, ModelProvider

# Configure logging
logger = logging.getLogger("ade-provider-factory")

class ProviderFactory:
    """Factory for creating model providers"""
    
    @staticmethod
    def create_provider(provider_type: str, config: Dict[str, Any]) -> Optional[ModelProvider]:
        """Create a provider instance based on type and configuration"""
        if "api_key" not in config:
            return None
            
        api_key = config["api_key"]
        model = config.get("model", "")
        
        try:
            # Import provider classes dynamically to avoid circular dependencies
            if provider_type == "openai":
                from .providers.openai import OpenAIProvider
                provider_class = OpenAIProvider
            elif provider_type == "anthropic":
                from .providers.anthropic import AnthropicProvider
                provider_class = AnthropicProvider
            elif provider_type == "google":
                from .providers.google import GoogleAIProvider
                provider_class = GoogleAIProvider
            elif provider_type == "deepseek":
                from .providers.deepseek import DeepSeekProvider
                provider_class = DeepSeekProvider
            elif provider_type == "local":
                from .providers.local import LocalProvider
                provider_class = LocalProvider
            else:
                logger.error(f"Unknown provider type: {provider_type}")
                return None
            
            # Create provider instance
            provider = provider_class(
                api_key=api_key,
                provider_id=config.get("provider_id"),
                model_map=config.get("model_map", {}),
                default_parameters=config.get("default_parameters", {})
            )
            
            # Initialize provider
            if not provider.initialize():
                logger.error(f"Failed to initialize provider: {provider_type}")
                return None
            
            return provider
            
        except Exception as e:
            logger.error(f"Failed to create provider {provider_type}: {str(e)}")
            return None
    
    @staticmethod
    def create_registry_from_config(config: Dict[str, Any]) -> ProviderRegistry:
        """Create a provider registry from configuration"""
        registry = ProviderRegistry()
        
        # Load providers from config
        providers = config.get("providers", [])
        for provider_config in providers:
            provider_type = provider_config.get("type")
            if not provider_type:
                continue
                
            provider = ProviderFactory.create_provider(provider_type, provider_config)
            if provider:
                registry.register_provider(provider)
        
        return registry 