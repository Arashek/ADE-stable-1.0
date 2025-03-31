from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime
import json
from abc import ABC, abstractmethod
import uuid

from .memory_manager import MemoryEntry, MemoryType

logger = logging.getLogger(__name__)

class VectorDatabase(ABC):
    """Abstract base class for vector database operations"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize database connection"""
        pass
    
    @abstractmethod
    async def store(self, memory: MemoryEntry) -> None:
        """Store memory entry with embedding"""
        pass
    
    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Search for similar memories"""
        pass
    
    @abstractmethod
    async def update(self, memory: MemoryEntry) -> None:
        """Update existing memory entry"""
        pass
    
    @abstractmethod
    async def delete(self, memory_id: str) -> None:
        """Delete memory entry"""
        pass

class DocumentDatabase(ABC):
    """Abstract base class for document database operations"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize database connection"""
        pass
    
    @abstractmethod
    async def store(self, memory: MemoryEntry) -> None:
        """Store memory entry"""
        pass
    
    @abstractmethod
    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get memory entry by ID"""
        pass
    
    @abstractmethod
    async def update(self, memory: MemoryEntry) -> None:
        """Update existing memory entry"""
        pass
    
    @abstractmethod
    async def delete(self, memory_id: str) -> None:
        """Delete memory entry"""
        pass
    
    @abstractmethod
    async def query(
        self,
        filters: Dict[str, Any],
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Query memory entries"""
        pass

class ChromaVectorDB(VectorDatabase):
    """ChromaDB implementation for vector storage"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.collection = None
    
    async def initialize(self) -> None:
        """Initialize ChromaDB connection"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.config.get("persist_directory", "./chroma_db")
            ))
            
            self.collection = self.client.get_or_create_collection(
                name=self.config.get("collection_name", "memories")
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    async def store(self, memory: MemoryEntry) -> None:
        """Store memory in ChromaDB"""
        try:
            if not memory.embedding:
                raise ValueError("Memory must have embedding to store in vector database")
            
            self.collection.add(
                embeddings=[memory.embedding],
                documents=[json.dumps(memory.content)],
                metadatas=[{
                    "id": memory.id,
                    "type": memory.type.value,
                    "project_id": memory.project_id,
                    "agent_id": memory.agent_id,
                    "session_id": memory.session_id,
                    "tags": memory.tags,
                    "created_at": memory.created_at,
                    "updated_at": memory.updated_at
                }],
                ids=[memory.id]
            )
            
        except Exception as e:
            logger.error(f"Failed to store memory in ChromaDB: {str(e)}")
            raise
    
    async def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Search for similar memories in ChromaDB"""
        try:
            # Prepare where clause for filters
            where = {}
            if filters:
                for key, value in filters.items():
                    where[key] = value
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where
            )
            
            # Convert results to MemoryEntry objects
            memories = []
            for i in range(len(results["ids"][0])):
                memory = MemoryEntry(
                    id=results["ids"][0][i],
                    type=MemoryType(results["metadatas"][0][i]["type"]),
                    content=json.loads(results["documents"][0][i]),
                    metadata=results["metadatas"][0][i],
                    embedding=results["embeddings"][0][i],
                    project_id=results["metadatas"][0][i].get("project_id"),
                    agent_id=results["metadatas"][0][i].get("agent_id"),
                    session_id=results["metadatas"][0][i].get("session_id"),
                    tags=results["metadatas"][0][i].get("tags", []),
                    created_at=results["metadatas"][0][i]["created_at"],
                    updated_at=results["metadatas"][0][i]["updated_at"]
                )
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to search ChromaDB: {str(e)}")
            raise
    
    async def update(self, memory: MemoryEntry) -> None:
        """Update memory in ChromaDB"""
        try:
            if not memory.embedding:
                raise ValueError("Memory must have embedding to update in vector database")
            
            self.collection.update(
                embeddings=[memory.embedding],
                documents=[json.dumps(memory.content)],
                metadatas=[{
                    "id": memory.id,
                    "type": memory.type.value,
                    "project_id": memory.project_id,
                    "agent_id": memory.agent_id,
                    "session_id": memory.session_id,
                    "tags": memory.tags,
                    "created_at": memory.created_at,
                    "updated_at": memory.updated_at
                }],
                ids=[memory.id]
            )
            
        except Exception as e:
            logger.error(f"Failed to update memory in ChromaDB: {str(e)}")
            raise
    
    async def delete(self, memory_id: str) -> None:
        """Delete memory from ChromaDB"""
        try:
            self.collection.delete(ids=[memory_id])
            
        except Exception as e:
            logger.error(f"Failed to delete memory from ChromaDB: {str(e)}")
            raise

class MongoDBDocumentDB(DocumentDatabase):
    """MongoDB implementation for document storage"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.db = None
        self.collection = None
    
    async def initialize(self) -> None:
        """Initialize MongoDB connection"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            self.client = AsyncIOMotorClient(self.config["connection_string"])
            self.db = self.client[self.config.get("database_name", "ade_memory")]
            self.collection = self.db[self.config.get("collection_name", "memories")]
            
            # Create indexes
            await self.collection.create_index("id", unique=True)
            await self.collection.create_index("project_id")
            await self.collection.create_index("agent_id")
            await self.collection.create_index("session_id")
            await self.collection.create_index("type")
            await self.collection.create_index("tags")
            
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB: {str(e)}")
            raise
    
    async def store(self, memory: MemoryEntry) -> None:
        """Store memory in MongoDB"""
        try:
            document = {
                "id": memory.id,
                "type": memory.type.value,
                "content": memory.content,
                "metadata": memory.metadata,
                "project_id": memory.project_id,
                "agent_id": memory.agent_id,
                "session_id": memory.session_id,
                "tags": memory.tags,
                "created_at": memory.created_at,
                "updated_at": memory.updated_at
            }
            
            await self.collection.insert_one(document)
            
        except Exception as e:
            logger.error(f"Failed to store memory in MongoDB: {str(e)}")
            raise
    
    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get memory from MongoDB"""
        try:
            document = await self.collection.find_one({"id": memory_id})
            if not document:
                return None
            
            return MemoryEntry(
                id=document["id"],
                type=MemoryType(document["type"]),
                content=document["content"],
                metadata=document["metadata"],
                project_id=document.get("project_id"),
                agent_id=document.get("agent_id"),
                session_id=document.get("session_id"),
                tags=document.get("tags", []),
                created_at=document["created_at"],
                updated_at=document["updated_at"]
            )
            
        except Exception as e:
            logger.error(f"Failed to get memory from MongoDB: {str(e)}")
            raise
    
    async def update(self, memory: MemoryEntry) -> None:
        """Update memory in MongoDB"""
        try:
            document = {
                "id": memory.id,
                "type": memory.type.value,
                "content": memory.content,
                "metadata": memory.metadata,
                "project_id": memory.project_id,
                "agent_id": memory.agent_id,
                "session_id": memory.session_id,
                "tags": memory.tags,
                "created_at": memory.created_at,
                "updated_at": memory.updated_at
            }
            
            await self.collection.update_one(
                {"id": memory.id},
                {"$set": document}
            )
            
        except Exception as e:
            logger.error(f"Failed to update memory in MongoDB: {str(e)}")
            raise
    
    async def delete(self, memory_id: str) -> None:
        """Delete memory from MongoDB"""
        try:
            await self.collection.delete_one({"id": memory_id})
            
        except Exception as e:
            logger.error(f"Failed to delete memory from MongoDB: {str(e)}")
            raise
    
    async def query(
        self,
        filters: Dict[str, Any],
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Query memories from MongoDB"""
        try:
            cursor = self.collection.find(filters).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            memories = []
            for document in documents:
                memory = MemoryEntry(
                    id=document["id"],
                    type=MemoryType(document["type"]),
                    content=document["content"],
                    metadata=document["metadata"],
                    project_id=document.get("project_id"),
                    agent_id=document.get("agent_id"),
                    session_id=document.get("session_id"),
                    tags=document.get("tags", []),
                    created_at=document["created_at"],
                    updated_at=document["updated_at"]
                )
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to query MongoDB: {str(e)}")
            raise

class KnowledgePersistence:
    """Coordinator for knowledge persistence operations"""
    
    def __init__(
        self,
        vector_db_config: Dict[str, Any],
        document_db_config: Dict[str, Any]
    ):
        self.vector_db = ChromaVectorDB(vector_db_config)
        self.document_db = MongoDBDocumentDB(document_db_config)
    
    async def initialize(self) -> None:
        """Initialize both databases"""
        try:
            await self.vector_db.initialize()
            await self.document_db.initialize()
            
        except Exception as e:
            logger.error(f"Failed to initialize persistence layer: {str(e)}")
            raise
    
    async def store_memory(self, memory: MemoryEntry) -> None:
        """Store memory in both databases"""
        try:
            await self.vector_db.store(memory)
            await self.document_db.store(memory)
            
        except Exception as e:
            logger.error(f"Failed to store memory: {str(e)}")
            raise
    
    async def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get memory from document database"""
        try:
            return await self.document_db.get(memory_id)
            
        except Exception as e:
            logger.error(f"Failed to get memory: {str(e)}")
            raise
    
    async def search_memories(
        self,
        query_embedding: List[float],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Search for similar memories using vector database"""
        try:
            return await self.vector_db.search(
                query_embedding=query_embedding,
                filters=filters,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Failed to search memories: {str(e)}")
            raise
    
    async def update_memory(self, memory: MemoryEntry) -> None:
        """Update memory in both databases"""
        try:
            await self.vector_db.update(memory)
            await self.document_db.update(memory)
            
        except Exception as e:
            logger.error(f"Failed to update memory: {str(e)}")
            raise
    
    async def delete_memory(self, memory_id: str) -> None:
        """Delete memory from both databases"""
        try:
            await self.vector_db.delete(memory_id)
            await self.document_db.delete(memory_id)
            
        except Exception as e:
            logger.error(f"Failed to delete memory: {str(e)}")
            raise
    
    async def query_memories(
        self,
        filters: Dict[str, Any],
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Query memories from document database"""
        try:
            return await self.document_db.query(filters, limit)
            
        except Exception as e:
            logger.error(f"Failed to query memories: {str(e)}")
            raise 