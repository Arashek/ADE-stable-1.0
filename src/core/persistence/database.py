from typing import Optional, Dict, Any
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, OperationFailure
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections with error handling and connection pooling"""
    
    def __init__(
        self,
        connection_string: str,
        database_name: str,
        max_pool_size: int = 100,
        min_pool_size: int = 10,
        max_idle_time_ms: int = 45000,
        retry_attempts: int = 3
    ):
        self.connection_string = connection_string
        self.database_name = database_name
        self.max_pool_size = max_pool_size
        self.min_pool_size = min_pool_size
        self.max_idle_time_ms = max_idle_time_ms
        self.retry_attempts = retry_attempts
        self._client: Optional[AsyncIOMotorClient] = None
        self._db = None
        self._is_connected = False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def connect(self) -> None:
        """Establish database connection with retry logic"""
        try:
            if self._is_connected:
                return
                
            self._client = AsyncIOMotorClient(
                self.connection_string,
                maxPoolSize=self.max_pool_size,
                minPoolSize=self.min_pool_size,
                maxIdleTimeMS=self.max_idle_time_ms,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            # Verify connection
            await self._client.admin.command('ping')
            self._db = self._client[self.database_name]
            self._is_connected = True
            logger.info(f"Successfully connected to database: {self.database_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            self._is_connected = False
            raise
    
    async def disconnect(self) -> None:
        """Safely close database connection"""
        if self._client:
            self._client.close()
            self._is_connected = False
            logger.info("Database connection closed")
    
    async def get_collection(self, collection_name: str):
        """Get a collection with connection verification"""
        if not self._is_connected:
            await self.connect()
        return self._db[collection_name]
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def execute_operation(self, operation, *args, **kwargs) -> Any:
        """Execute database operation with retry logic"""
        try:
            if not self._is_connected:
                await self.connect()
            return await operation(*args, **kwargs)
        except OperationFailure as e:
            logger.error(f"Database operation failed: {str(e)}")
            raise
        except ConnectionFailure as e:
            logger.error(f"Database connection lost: {str(e)}")
            self._is_connected = False
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            if not self._is_connected:
                await self.connect()
            
            # Check connection
            await self._client.admin.command('ping')
            
            # Get database stats
            stats = await self._db.command("dbStats")
            
            return {
                "status": "healthy",
                "connected": True,
                "database": self.database_name,
                "collections": stats.get("collections", 0),
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0)
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            } 