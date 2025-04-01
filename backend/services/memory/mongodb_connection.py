"""
MongoDB Connection Manager for Memory Service

This module provides a connection manager for MongoDB, which is used to store
conversation history, project artifacts, and other memory-related data.
"""

import logging
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, OperationFailure
from config.settings import settings

logger = logging.getLogger(__name__)

class MongoDBConnectionManager:
    """MongoDB connection manager for the memory service"""
    
    _instance = None
    
    def __new__(cls):
        """Create a singleton instance of the MongoDB connection manager"""
        if cls._instance is None:
            cls._instance = super(MongoDBConnectionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the MongoDB connection manager"""
        if self._initialized:
            return
            
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self._initialized = True
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            # Get MongoDB connection string from settings
            mongodb_uri = settings.MONGODB_URI
            mongodb_db = settings.MONGODB_DB
            
            # Create MongoDB client
            self.client = AsyncIOMotorClient(mongodb_uri)
            
            # Verify connection
            await self.client.admin.command('ping')
            
            # Get database
            self.db = self.client[mongodb_db]
            
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
            raise
            
    async def disconnect(self):
        """Disconnect from MongoDB"""
        try:
            if self.client:
                self.client.close()
                self.client = None
                self.db = None
                logger.info("Successfully disconnected from MongoDB")
        except Exception as e:
            logger.error(f"Error disconnecting from MongoDB: {str(e)}")
            raise
            
    async def get_collection(self, collection_name: str):
        """Get a MongoDB collection"""
        if not self.db:
            raise RuntimeError("MongoDB connection not initialized")
        return self.db[collection_name]
        
    async def create_indexes(self):
        """Create indexes for MongoDB collections"""
        try:
            # Create indexes for conversation history
            conversation_collection = self.db["conversation_history"]
            await conversation_collection.create_index([("project_id", 1)])
            await conversation_collection.create_index([("timestamp", -1)])
            await conversation_collection.create_index([("user_id", 1)])
            
            # Create indexes for knowledge graph
            knowledge_collection = self.db["knowledge_graph"]
            await knowledge_collection.create_index([("project_id", 1)])
            await knowledge_collection.create_index([("entity_type", 1)])
            await knowledge_collection.create_index([("entity_id", 1)])
            
            # Create indexes for decision memory
            decision_collection = self.db["decision_memory"]
            await decision_collection.create_index([("project_id", 1)])
            await decision_collection.create_index([("timestamp", -1)])
            await decision_collection.create_index([("category", 1)])
            
            # Create indexes for vector embeddings
            embedding_collection = self.db["vector_embeddings"]
            await embedding_collection.create_index([("project_id", 1)])
            await embedding_collection.create_index([("content_id", 1)])
            
            logger.info("Successfully created MongoDB indexes")
        except OperationFailure as e:
            logger.error(f"Failed to create MongoDB indexes: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating MongoDB indexes: {str(e)}")
            raise

# Create a global instance of the MongoDB connection manager
mongodb_manager = MongoDBConnectionManager()
