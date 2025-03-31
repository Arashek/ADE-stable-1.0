import logging
from typing import Dict, List, Any, Optional, Tuple, Type
from .config import ProviderConfig, Capability, ProviderTier
from .adapters.base import BaseProviderAdapter
from .adapters.ollama import OllamaAdapter
from .adapters.groq import GroqAdapter
from ..models.proprietary.adapters import CodeCompletionAdapter

logger = logging.getLogger(__name__)

class ProviderRegistry:
    """Registry of available AI providers and their configurations"""
    
    def __init__(self):
        # Initialize standard providers with default configs
        self.providers: Dict[str, ProviderConfig] = {
            "openai": ProviderConfig(
                tier=ProviderTier.PREMIUM,
                model_path="gpt-4",
                capabilities={
                    Capability.CODE_COMPLETION: 0.9,
                    Capability.PLANNING: 0.85,
                    Capability.CONTEXT_AWARENESS: 0.95
                }
            ),
            "anthropic": ProviderConfig(
                tier=ProviderTier.PREMIUM,
                model_path="claude-3",
                capabilities={
                    Capability.CODE_COMPLETION: 0.95,
                    Capability.PLANNING: 0.9,
                    Capability.CONTEXT_AWARENESS: 0.98
                }
            ),
            "google": ProviderConfig(
                tier=ProviderTier.PREMIUM,
                model_path="gemini-pro",
                capabilities={
                    Capability.CODE_COMPLETION: 0.85,
                    Capability.PLANNING: 0.8,
                    Capability.CONTEXT_AWARENESS: 0.9
                }
            ),
            "groq": ProviderConfig(
                tier=ProviderTier.PREMIUM,
                model_path="mixtral-8x7b-32768",
                capabilities={
                    Capability.CODE_COMPLETION: 0.9,
                    Capability.PLANNING: 0.85,
                    Capability.CONTEXT_AWARENESS: 0.95
                }
            ),
            "ollama": ProviderConfig(
                tier=ProviderTier.FREE,
                model_path="codellama",
                enabled=True,
                server_url="http://localhost:11434",
                capabilities={
                    Capability.CODE_COMPLETION: 0.8,
                    Capability.PLANNING: 0.75,
                    Capability.CONTEXT_AWARENESS: 0.85
                }
            ),
        }
        
        # Map of provider_name -> adapter_class
        self._adapter_classes: Dict[str, Type[BaseProviderAdapter]] = {
            "ollama": OllamaAdapter,
            "groq": GroqAdapter,
            "proprietary": CodeCompletionAdapter,
        }
        
        # Cache of initialized adapters
        self._adapter_instances: Dict[str, BaseProviderAdapter] = {}
        
        # Default tier configuration
        self.default_tier = ProviderTier.STANDARD
    
    def register_provider(
        self,
        name: str,
        config: ProviderConfig,
        adapter_class: Type[BaseProviderAdapter]
    ) -> bool:
        """Register a new provider with the registry"""
        try:
            if name in self.providers:
                logger.warning(f"Overwriting existing provider configuration for {name}")
            
            self.providers[name] = config
            self._adapter_classes[name] = adapter_class
            
            # Clear instance if it exists
            if name in self._adapter_instances:
                del self._adapter_instances[name]
                
            logger.info(f"Registered provider: {name} (tier: {config.tier})")
            return True
        except Exception as e:
            logger.error(f"Error registering provider {name}: {str(e)}")
            return False
    
    def register_proprietary_model(
        self,
        name: str,
        model_path: str,
        capabilities: Dict[Capability, float],
        device: str = "cuda",
        batch_size: int = 1,
        quantization: Optional[str] = None
    ) -> bool:
        """Register a proprietary model with the registry"""
        try:
            config = ProviderConfig(
                tier=ProviderTier.PREMIUM,
                model_path=model_path,
                device=device,
                batch_size=batch_size,
                quantization=quantization,
                capabilities=capabilities
            )
            
            return self.register_provider(
                name=name,
                config=config,
                adapter_class=CodeCompletionAdapter
            )
            
        except Exception as e:
            logger.error(f"Error registering proprietary model {name}: {str(e)}")
            return False
    
    def get_provider(self, name: str) -> Optional[BaseProviderAdapter]:
        """Get a provider adapter by name"""
        if name not in self._adapter_instances:
            if name not in self.providers or name not in self._adapter_classes:
                return None
                
            config = self.providers[name]
            adapter_class = self._adapter_classes[name]
            
            try:
                adapter = adapter_class(config)
                self._adapter_instances[name] = adapter
            except Exception as e:
                logger.error(f"Error initializing provider {name}: {str(e)}")
                return None
                
        return self._adapter_instances[name]
    
    def list_providers(self) -> List[str]:
        """List all registered providers"""
        return list(self.providers.keys())
    
    def get_provider_config(self, name: str) -> Optional[ProviderConfig]:
        """Get configuration for a provider"""
        return self.providers.get(name)
    
    def remove_provider(self, name: str) -> bool:
        """Remove a provider from the registry"""
        try:
            if name in self.providers:
                del self.providers[name]
            if name in self._adapter_classes:
                del self._adapter_classes[name]
            if name in self._adapter_instances:
                del self._adapter_instances[name]
            return True
        except Exception as e:
            logger.error(f"Error removing provider {name}: {str(e)}")
            return False


