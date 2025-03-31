from typing import Dict, List, Optional, Any, TypeVar, Type, Union
from datetime import datetime
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .models import Plan, Task, TaskStatus
from .indexes import get_indexes

T = TypeVar('T', Plan, Task)

class MongoDBRepository:
    """MongoDB repository with advanced features"""
    
    def __init__(
        self,
        connection_string: str,
        database_name: str,
        max_pool_size: int = 100,
        min_pool_size: int = 10,
        max_idle_time_ms: int = 60000,
        retry_attempts: int = 3,
        retry_wait_base: float = 1.0
    ):
        """
        Initialize the MongoDB repository
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database
            max_pool_size: Maximum number of connections in the pool
            min_pool_size: Minimum number of connections in the pool
            max_idle_time_ms: Maximum time a connection can be idle
            retry_attempts: Number of retry attempts for failed operations
            retry_wait_base: Base wait time for exponential backoff
        """
        self.client = AsyncIOMotorClient(
            connection_string,
            maxPoolSize=max_pool_size,
            minPoolSize=min_pool_size,
            maxIdleTimeMS=max_idle_time_ms
        )
        self.db: AsyncIOMotorDatabase = self.client[database_name]
        self.retry_attempts = retry_attempts
        self.retry_wait_base = retry_wait_base
        
    async def initialize(self):
        """Initialize the repository and create indexes"""
        # Create indexes for all collections
        indexes = get_indexes()
        for collection_name, collection_indexes in indexes.items():
            collection = self.db[collection_name]
            for index in collection_indexes:
                await collection.create_index(**index)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationFailure, ServerSelectionTimeoutError))
    )
    async def _execute_with_retry(self, operation):
        """Execute an operation with retry logic"""
        try:
            return await operation()
        except (OperationFailure, ServerSelectionTimeoutError) as e:
            # Log the error here if needed
            raise
    
    async def _with_transaction(self, operation):
        """Execute an operation within a transaction"""
        session = self.client.start_session()
        try:
            async with session.start_transaction():
                result = await operation(session)
                await session.commit_transaction()
                return result
        except Exception as e:
            await session.abort_transaction()
            raise
        finally:
            await session.end_session()
    
    async def create(self, model: T) -> T:
        """Create a new document with transaction support"""
        async def _create(session):
            collection = self.db[model.__class__.__name__.lower()]
            result = await collection.insert_one(model.dict(), session=session)
            model.id = str(result.inserted_id)
            return model
            
        return await self._execute_with_retry(
            lambda: self._with_transaction(_create)
        )
    
    async def bulk_create(self, models: List[T]) -> List[T]:
        """Create multiple documents in a single transaction"""
        async def _bulk_create(session):
            if not models:
                return []
                
            collection = self.db[models[0].__class__.__name__.lower()]
            documents = [model.dict() for model in models]
            result = await collection.insert_many(documents, session=session)
            
            # Update models with their IDs
            for model, inserted_id in zip(models, result.inserted_ids):
                model.id = str(inserted_id)
                
            return models
            
        return await self._execute_with_retry(
            lambda: self._with_transaction(_bulk_create)
        )
    
    async def get(self, model_class: Type[T], id: str) -> Optional[T]:
        """Get a document by ID with retry logic"""
        async def _get():
            collection = self.db[model_class.__name__.lower()]
            result = await collection.find_one({"_id": id})
            return model_class(**result) if result else None
            
        return await self._execute_with_retry(_get)
    
    async def update(self, model: T) -> T:
        """Update a document with transaction support"""
        async def _update(session):
            collection = self.db[model.__class__.__name__.lower()]
            data = model.dict(exclude={'id'})
            await collection.update_one(
                {"_id": model.id},
                {"$set": data},
                session=session
            )
            return model
            
        return await self._execute_with_retry(
            lambda: self._with_transaction(_update)
        )
    
    async def bulk_update(self, models: List[T]) -> List[T]:
        """Update multiple documents in a single transaction"""
        async def _bulk_update(session):
            if not models:
                return []
                
            collection = self.db[models[0].__class__.__name__.lower()]
            operations = [
                {
                    "update_one": {
                        "filter": {"_id": model.id},
                        "update": {"$set": model.dict(exclude={'id'})},
                        "upsert": False
                    }
                }
                for model in models
            ]
            
            await collection.bulk_write(operations, session=session)
            return models
            
        return await self._execute_with_retry(
            lambda: self._with_transaction(_bulk_update)
        )
    
    async def delete(self, model: T) -> bool:
        """Delete a document with transaction support"""
        async def _delete(session):
            collection = self.db[model.__class__.__name__.lower()]
            result = await collection.delete_one(
                {"_id": model.id},
                session=session
            )
            return result.deleted_count > 0
            
        return await self._execute_with_retry(
            lambda: self._with_transaction(_delete)
        )
    
    async def bulk_delete(self, models: List[T]) -> int:
        """Delete multiple documents in a single transaction"""
        async def _bulk_delete(session):
            if not models:
                return 0
                
            collection = self.db[models[0].__class__.__name__.lower()]
            operations = [
                {
                    "delete_one": {
                        "filter": {"_id": model.id}
                    }
                }
                for model in models
            ]
            
            result = await collection.bulk_write(operations, session=session)
            return result.deleted_count
            
        return await self._execute_with_retry(
            lambda: self._with_transaction(_bulk_delete)
        )
    
    async def find(
        self,
        model_class: Type[T],
        query: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        sort: Optional[List[tuple]] = None
    ) -> List[T]:
        """Find documents with retry logic and pagination"""
        async def _find():
            collection = self.db[model_class.__name__.lower()]
            cursor = collection.find(query)
            
            if sort:
                cursor = cursor.sort(sort)
                
            cursor = cursor.skip(skip).limit(limit)
            results = await cursor.to_list(length=limit)
            return [model_class(**result) for result in results]
            
        return await self._execute_with_retry(_find)
    
    async def count(
        self,
        model_class: Type[T],
        query: Dict[str, Any]
    ) -> int:
        """Count documents with retry logic"""
        async def _count():
            collection = self.db[model_class.__name__.lower()]
            return await collection.count_documents(query)
            
        return await self._execute_with_retry(_count)
    
    async def text_search(
        self,
        model_class: Type[T],
        text: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[T]:
        """Perform text search with retry logic"""
        async def _text_search():
            collection = self.db[model_class.__name__.lower()]
            cursor = collection.find(
                {"$text": {"$search": text}},
                {"score": {"$meta": "textScore"}}
            )
            cursor = cursor.sort([("score", {"$meta": "textScore"})])
            cursor = cursor.skip(skip).limit(limit)
            results = await cursor.to_list(length=limit)
            return [model_class(**result) for result in results]
            
        return await self._execute_with_retry(_text_search)
    
    async def close(self):
        """Close the database connection"""
        self.client.close() 