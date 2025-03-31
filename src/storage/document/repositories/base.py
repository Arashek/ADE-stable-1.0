from typing import Any, Dict, List, Optional, TypeVar, Generic
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Base repository class for MongoDB operations"""
    
    def __init__(self, client: AsyncIOMotorClient, database: str):
        """Initialize the repository with a MongoDB client and database name"""
        self.client = client
        self.db: AsyncIOMotorDatabase = client[database]
    
    async def find_one(self, collection: str, query: Dict) -> Optional[Dict[str, Any]]:
        """Find a single document in the specified collection"""
        return await self.db[collection].find_one(query)
    
    async def find_many(
        self,
        collection: str,
        query: Dict,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_order: int = -1
    ) -> List[Dict[str, Any]]:
        """Find multiple documents in the specified collection"""
        cursor = self.db[collection].find(query)
        
        if sort_by:
            cursor = cursor.sort(sort_by, sort_order)
        
        cursor = cursor.skip(skip).limit(limit)
        return await cursor.to_list(length=None)
    
    async def insert_one(self, collection: str, document: Dict) -> str:
        """Insert a single document into the specified collection"""
        result = await self.db[collection].insert_one(document)
        return str(result.inserted_id)
    
    async def insert_many(self, collection: str, documents: List[Dict]) -> List[str]:
        """Insert multiple documents into the specified collection"""
        result = await self.db[collection].insert_many(documents)
        return [str(id_) for id_ in result.inserted_ids]
    
    async def update_one(
        self,
        collection: str,
        query: Dict,
        update: Dict,
        upsert: bool = False
    ) -> bool:
        """Update a single document in the specified collection"""
        result = await self.db[collection].update_one(query, update, upsert=upsert)
        return result.modified_count > 0 or (upsert and result.upserted_id is not None)
    
    async def update_many(
        self,
        collection: str,
        query: Dict,
        update: Dict
    ) -> int:
        """Update multiple documents in the specified collection"""
        result = await self.db[collection].update_many(query, update)
        return result.modified_count
    
    async def delete_one(self, collection: str, query: Dict) -> bool:
        """Delete a single document from the specified collection"""
        result = await self.db[collection].delete_one(query)
        return result.deleted_count > 0
    
    async def delete_many(self, collection: str, query: Dict) -> int:
        """Delete multiple documents from the specified collection"""
        result = await self.db[collection].delete_many(query)
        return result.deleted_count
    
    async def count_documents(self, collection: str, query: Dict) -> int:
        """Count documents in the specified collection that match the query"""
        return await self.db[collection].count_documents(query)
    
    async def create_index(self, collection: str, keys: List[tuple], unique: bool = False):
        """Create an index on the specified collection"""
        await self.db[collection].create_index(keys, unique=unique) 