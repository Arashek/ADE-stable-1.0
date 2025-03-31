"""Provider repository implementation."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from ..utils.encryption import encrypt_value, decrypt_value
from .base_repository import BaseRepository
from .connection import MongoDBConnection

class ProviderConfig(BaseModel):
    """Provider configuration model."""
    id: str
    provider_type: str
    provider_id: str
    encrypted_api_key: str
    model_map: Dict[str, str]
    default_parameters: Dict[str, Any]
    capability_scores: Dict[str, float]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def api_key(self) -> str:
        """Get decrypted API key."""
        return decrypt_value(self.encrypted_api_key)

    @api_key.setter
    def api_key(self, value: str) -> None:
        """Set encrypted API key."""
        self.encrypted_api_key = encrypt_value(value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProviderConfig':
        """Create from dictionary."""
        return cls(**data)

class ProviderRepository(BaseRepository):
    """Repository for managing provider configurations."""

    def __init__(self, connection: MongoDBConnection):
        """Initialize repository."""
        super().__init__(connection, "providers")

    async def create(self, config: ProviderConfig) -> ProviderConfig:
        """Create a new provider configuration."""
        await self.collection.insert_one(config.to_dict())
        return config

    async def get(self, provider_id: str) -> Optional[ProviderConfig]:
        """Get provider configuration by ID."""
        data = await self.collection.find_one({"id": provider_id})
        return ProviderConfig.from_dict(data) if data else None

    async def get_by_provider_id(self, provider_id: str) -> Optional[ProviderConfig]:
        """Get provider configuration by provider_id."""
        cursor = self.collection.find({"provider_id": provider_id})
        data = await cursor.to_list(length=1)
        return ProviderConfig.from_dict(data[0]) if data else None

    async def get_by_provider_type(self, provider_type: str) -> List[ProviderConfig]:
        """Get provider configurations by provider_type."""
        cursor = self.collection.find({"provider_type": provider_type})
        data = await cursor.to_list(length=None)
        return [ProviderConfig.from_dict(item) for item in data]

    async def update_capability_scores(
        self,
        provider_id: str,
        scores: Dict[str, float]
    ) -> Optional[ProviderConfig]:
        """Update provider capability scores."""
        data = await self.collection.find_one_and_update(
            {"id": provider_id},
            {
                "$set": {
                    "capability_scores": scores,
                    "updated_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        return ProviderConfig.from_dict(data) if data else None

    async def get_by_capability(self, capability: str) -> List[ProviderConfig]:
        """Get providers that support a specific capability."""
        cursor = self.collection.find({
            f"capability_scores.{capability}": {"$exists": True}
        })
        data = await cursor.to_list(length=None)
        return [ProviderConfig.from_dict(item) for item in data]

    async def get_best_provider_for_capability(
        self,
        capability: str,
        limit: int = 1
    ) -> List[ProviderConfig]:
        """Get best providers for a specific capability."""
        cursor = self.collection.find({
            f"capability_scores.{capability}": {"$exists": True}
        }).sort(f"capability_scores.{capability}", -1).limit(limit)
        data = await cursor.to_list(length=None)
        return [ProviderConfig.from_dict(item) for item in data]

__all__ = ['ProviderConfig', 'ProviderRepository'] 