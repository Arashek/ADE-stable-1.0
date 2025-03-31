"""Provider repository module."""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient

from src.storage.document.repositories.base import BaseRepository
from src.utils.encryption import encrypt_value, decrypt_value

class ProviderConfig(BaseModel):
    """Provider configuration stored in database"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider_type: str
    provider_id: str
    encrypted_api_key: str
    model_map: Dict[str, str] = Field(default_factory=dict)
    default_parameters: Dict[str, Any] = Field(default_factory=dict)
    capability_scores: Dict[str, float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True
    
    @property
    def api_key(self) -> str:
        """Get decrypted API key"""
        return decrypt_value(self.encrypted_api_key)
    
    @api_key.setter
    def api_key(self, value: str):
        """Set encrypted API key"""
        self.encrypted_api_key = encrypt_value(value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return self.model_dump(exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProviderConfig':
        """Create from dictionary"""
        return cls(**data)

class ProviderRepository(BaseRepository[ProviderConfig]):
    """Repository for ProviderConfig objects"""
    
    def __init__(self, client: AsyncIOMotorClient, database: str):
        super().__init__(client, database)
        self.collection = "providers"
    
    async def get_by_provider_id(self, provider_id: str) -> Optional[ProviderConfig]:
        """Get provider config by provider_id"""
        data = await self.find_one(self.collection, {"provider_id": provider_id})
        return ProviderConfig.from_dict(data) if data else None
    
    async def get_by_provider_type(self, provider_type: str) -> List[ProviderConfig]:
        """Get all provider configs by provider_type"""
        data = await self.find_many(self.collection, {"provider_type": provider_type})
        return [ProviderConfig.from_dict(d) for d in data]
    
    async def update_capability_scores(
        self,
        provider_id: str,
        scores: Dict[str, float]
    ) -> Optional[ProviderConfig]:
        """Update provider capability scores"""
        data = await self.find_one(self.collection, {"provider_id": provider_id})
        if not data:
            return None
            
        data["capability_scores"] = scores
        data["updated_at"] = datetime.now()
        
        await self.update_one(
            self.collection,
            {"provider_id": provider_id},
            {"$set": data}
        )
        
        return ProviderConfig.from_dict(data)
    
    async def get_by_capability(self, capability: str) -> List[ProviderConfig]:
        """Get providers that support a specific capability"""
        data = await self.find_many(
            self.collection,
            {f"capability_scores.{capability}": {"$exists": True}}
        )
        return [ProviderConfig.from_dict(d) for d in data]
    
    async def get_best_provider_for_capability(
        self,
        capability: str,
        limit: int = 1
    ) -> List[ProviderConfig]:
        """Get providers sorted by capability score"""
        providers = await self.get_by_capability(capability)
        return sorted(
            providers,
            key=lambda p: p.capability_scores.get(capability, 0),
            reverse=True
        )[:limit] 