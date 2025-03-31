"""MongoDB connection wrapper for document storage."""
from typing import Optional, List, Type, TypeVar
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class MongoDBConnection:
    """MongoDB connection wrapper for document storage."""
    
    def __init__(
        self,
        connection_string: str,
        database_name: str,
        max_pool_size: int = 100,
        min_pool_size: int = 10,
        max_idle_time_ms: int = 60000
    ):
        """Initialize the MongoDB connection.
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database
            max_pool_size: Maximum number of connections in the pool
            min_pool_size: Minimum number of connections in the pool
            max_idle_time_ms: Maximum time a connection can be idle
        """
        self.client = AsyncIOMotorClient(
            connection_string,
            maxPoolSize=max_pool_size,
            minPoolSize=min_pool_size,
            maxIdleTimeMS=max_idle_time_ms
        )
        self.database_name = database_name
        self.db = self.client[database_name]
    
    async def close(self):
        """Close the MongoDB connection."""
        self.client.close()
        
    async def find_all(self, model_class: Type[T]) -> List[T]:
        """Find all documents of a given model type.
        
        Args:
            model_class: The Pydantic model class to query for
            
        Returns:
            List of model instances
        """
        collection = self.db[model_class.__name__.lower()]
        cursor = collection.find({})
        documents = await cursor.to_list(length=None)
        return [model_class(**doc) for doc in documents] 