"""Provider registry dependency."""
from typing import Optional
from functools import lru_cache

from src.core.models.provider_registry import ProviderRegistry
from src.core.models.types import ModelCapability
from src.storage.document.connection import MongoDBConnection
from src.storage.document.repositories import ProviderConfig

@lru_cache()
def get_provider_registry(
    db_connector: Optional[MongoDBConnection] = None
) -> ProviderRegistry:
    """Get or create a provider registry instance.
    
    Args:
        db_connector: Optional MongoDB connector for persistence
        
    Returns:
        Provider registry instance
    """
    registry = ProviderRegistry()
    
    if db_connector:
        # Load providers from database
        provider_configs = db_connector.find_all(ProviderConfig)
        for config in provider_configs:
            registry.register_provider(
                provider_type=config.provider_type,
                api_key=config.api_key,
                model_map=config.model_map,
                default_parameters=config.default_parameters,
                capability_scores={
                    ModelCapability(k): v
                    for k, v in config.capability_scores.items()
                }
            )
    
    return registry 