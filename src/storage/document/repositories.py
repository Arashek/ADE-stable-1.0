"""Document repositories for MongoDB storage."""
from typing import List, Optional, Dict, Any, Type, TypeVar, Generic
from datetime import datetime
import uuid
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient

from src.storage.document.connection import MongoDBConnection
from src.utils.encryption import encrypt_value, decrypt_value

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    """Base repository for MongoDB operations"""
    
    def __init__(self, connection: MongoDBConnection, model: Type[T], collection_name: str):
        """Initialize the repository.
        
        Args:
            connection: MongoDB connection instance
            model: Pydantic model class
            collection_name: Name of the MongoDB collection
        """
        self.connection = connection
        self.model = model
        self.collection = connection.client[connection.database_name][collection_name]
    
    async def create(self, document: T) -> T:
        """Create a new document.
        
        Args:
            document: Document to create
            
        Returns:
            Created document
        """
        data = document.model_dump()
        await self.collection.insert_one(data)
        return document
    
    async def get(self, document_id: str) -> Optional[T]:
        """Get a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document if found, None otherwise
        """
        data = await self.collection.find_one({"id": document_id})
        return self.model(**data) if data else None
    
    async def list(self, query: Dict[str, Any] = None) -> List[T]:
        """List documents matching the query.
        
        Args:
            query: MongoDB query dictionary
            
        Returns:
            List of matching documents
        """
        query = query or {}
        cursor = self.collection.find(query)
        documents = await cursor.to_list(length=None)
        return [self.model(**doc) for doc in documents]
    
    async def update(self, document_id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update a document.
        
        Args:
            document_id: Document ID
            data: Update data
            
        Returns:
            Updated document if found, None otherwise
        """
        data["updated_at"] = datetime.utcnow()
        result = await self.collection.find_one_and_update(
            {"id": document_id},
            {"$set": data},
            return_document=True
        )
        return self.model(**result) if result else None
    
    async def delete(self, document_id: str) -> bool:
        """Delete a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deleted, False otherwise
        """
        result = await self.collection.delete_one({"id": document_id})
        return result.deleted_count > 0

class UserProviderPreference(BaseModel):
    """User-specific provider preferences"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    provider_id: str
    priority: int = 0  # Higher values mean higher priority
    disabled: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True

class UserProviderPreferenceRepository(BaseRepository[UserProviderPreference]):
    """Repository for UserProviderPreference objects"""
    
    def __init__(self, connection: MongoDBConnection):
        super().__init__(connection, UserProviderPreference, "user_provider_preferences")
    
    async def get_user_preferences(self, user_id: str) -> List[UserProviderPreference]:
        """Get all provider preferences for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of provider preferences
        """
        return await self.list({"user_id": user_id})
    
    async def get_user_preference(self, user_id: str, provider_id: str) -> Optional[UserProviderPreference]:
        """Get a specific provider preference for a user.
        
        Args:
            user_id: User ID
            provider_id: Provider ID
            
        Returns:
            Provider preference if found, None otherwise
        """
        data = await self.collection.find_one({
            "user_id": user_id,
            "provider_id": provider_id
        })
        return self.model(**data) if data else None
    
    async def update_user_preference(
        self,
        user_id: str,
        provider_id: str,
        priority: Optional[int] = None,
        disabled: Optional[bool] = None
    ) -> Optional[UserProviderPreference]:
        """Update a user's provider preference.
        
        Args:
            user_id: User ID
            provider_id: Provider ID
            priority: New priority value
            disabled: New disabled status
            
        Returns:
            Updated preference if found, None otherwise
        """
        update_data = {}
        if priority is not None:
            update_data["priority"] = priority
        if disabled is not None:
            update_data["disabled"] = disabled
            
        if not update_data:
            return None
            
        result = await self.collection.find_one_and_update(
            {"user_id": user_id, "provider_id": provider_id},
            {"$set": update_data},
            return_document=True
        )
        return self.model(**result) if result else None
    
    async def delete_user_preference(self, user_id: str, provider_id: str) -> bool:
        """Delete a user's provider preference.
        
        Args:
            user_id: User ID
            provider_id: Provider ID
            
        Returns:
            True if deleted, False otherwise
        """
        result = await self.collection.delete_one({
            "user_id": user_id,
            "provider_id": provider_id
        })
        return result.deleted_count > 0
    
    async def get_active_preferences(self, user_id: str) -> List[UserProviderPreference]:
        """Get all active provider preferences for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of active provider preferences
        """
        return await self.list({
            "user_id": user_id,
            "disabled": False
        })
    
    async def get_prioritized_preferences(self, user_id: str) -> List[UserProviderPreference]:
        """Get provider preferences for a user, sorted by priority.
        
        Args:
            user_id: User ID
            
        Returns:
            List of provider preferences sorted by priority
        """
        preferences = await self.get_active_preferences(user_id)
        return sorted(preferences, key=lambda x: x.priority, reverse=True)

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
    
    def __init__(self, connection: MongoDBConnection):
        super().__init__(connection, ProviderConfig, "providers")
    
    async def get_by_provider_id(self, provider_id: str) -> Optional[ProviderConfig]:
        """Get provider config by provider_id"""
        configs = await self.list({"provider_id": provider_id})
        if not configs:
            return None
        return configs[0]
    
    async def get_by_provider_type(self, provider_type: str) -> List[ProviderConfig]:
        """Get all provider configs by provider_type"""
        return await self.list({"provider_type": provider_type})
    
    async def update_capability_scores(
        self,
        provider_id: str,
        scores: Dict[str, float]
    ) -> Optional[ProviderConfig]:
        """Update provider capability scores"""
        return await self.update(
            provider_id,
            {"capability_scores": scores}
        )
    
    async def get_by_capability(self, capability: str) -> List[ProviderConfig]:
        """Get providers that support a specific capability"""
        return await self.list({
            f"capability_scores.{capability}": {"$exists": True}
        })
    
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

class Usage(BaseModel):
    """Usage tracking record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    provider_id: str
    model_id: str
    tokens_input: int = 0
    tokens_output: int = 0
    cost: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True

class UsageRepository(BaseRepository[Usage]):
    """Repository for Usage records"""
    
    def __init__(self, client: AsyncIOMotorClient, database_name: str):
        self.collection = client[database_name]["usage"]
    
    async def create_usage(
        self,
        user_id: str,
        provider_id: str,
        model_id: str,
        tokens_input: int,
        tokens_output: int,
        cost: float
    ) -> Usage:
        """Create a new usage record"""
        usage = Usage(
            user_id=user_id,
            provider_id=provider_id,
            model_id=model_id,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost=cost
        )
        await self.collection.insert_one(usage.model_dump())
        return usage
    
    async def get_user_usage(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Usage]:
        """Get usage records for a user within a date range"""
        query = {"user_id": user_id}
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        cursor = self.collection.find(query)
        documents = await cursor.to_list(length=None)
        return [Usage(**doc) for doc in documents]
    
    async def delete_old_records(self, cutoff_date: datetime):
        """Delete usage records older than the cutoff date"""
        return await self.collection.delete_many({
            "created_at": {"$lt": cutoff_date}
        })

class User(BaseModel):
    """User model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    hashed_password: str
    disabled: bool = False
    roles: List[str] = Field(default_factory=lambda: ["viewer"])
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True

class UserRepository(BaseRepository[User]):
    """Repository for User objects"""
    
    def __init__(self, connection: MongoDBConnection):
        super().__init__(connection, User, "users")
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username.
        
        Args:
            username: Username to look up
            
        Returns:
            User if found, None otherwise
        """
        data = await self.collection.find_one({"username": username})
        return self.model(**data) if data else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email.
        
        Args:
            email: Email to look up
            
        Returns:
            User if found, None otherwise
        """
        data = await self.collection.find_one({"email": email})
        return self.model(**data) if data else None
    
    async def update_roles(self, user_id: str, roles: List[str]) -> Optional[User]:
        """Update a user's roles.
        
        Args:
            user_id: User ID
            roles: New list of roles
            
        Returns:
            Updated user if found, None otherwise
        """
        return await self.update(user_id, {"roles": roles})
    
    async def update_password(self, user_id: str, hashed_password: str) -> Optional[User]:
        """Update a user's password.
        
        Args:
            user_id: User ID
            hashed_password: New hashed password
            
        Returns:
            Updated user if found, None otherwise
        """
        return await self.update(user_id, {"hashed_password": hashed_password})
    
    async def update_status(self, user_id: str, disabled: bool) -> Optional[User]:
        """Update a user's disabled status.
        
        Args:
            user_id: User ID
            disabled: New disabled status
            
        Returns:
            Updated user if found, None otherwise
        """
        return await self.update(user_id, {"disabled": disabled}) 