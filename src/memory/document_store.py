from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import json
import os
import shutil

from .memory_manager import MemoryEntry, MemoryType
from .context_manager import ContextReference, ContextType

logger = logging.getLogger(__name__)

class DocumentStore:
    def __init__(self, mongo_uri: str, database: str = "ade_memory"):
        """Initialize document store with MongoDB
        
        Args:
            mongo_uri: MongoDB connection URI
            database: Database name
        """
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[database]
        self.memories = self.db.memories
        self.contexts = self.db.contexts
        
        # Create indexes
        self._create_indexes()
        
    async def _create_indexes(self):
        """Create necessary indexes for efficient querying"""
        # Memory indexes
        await self.memories.create_index("type")
        await self.memories.create_index("project_id")
        await self.memories.create_index("agent_id")
        await self.memories.create_index("session_id")
        await self.memories.create_index("created_at")
        await self.memories.create_index("tags")
        await self.memories.create_index("content_hash")
        await self.memories.create_index("last_accessed")
        
        # Context indexes
        await self.contexts.create_index("type")
        await self.contexts.create_index("parent_id")
        await self.contexts.create_index("memory_ids")
        await self.contexts.create_index("tags")
        await self.contexts.create_index("last_accessed")
        await self.contexts.create_index("name")
        await self.contexts.create_index("description")
        
    async def add_memory(self, memory: MemoryEntry) -> None:
        """Add a memory entry to the document store
        
        Args:
            memory: Memory entry to add
        """
        try:
            # Convert memory to dict
            memory_dict = {
                "id": memory.id,
                "type": memory.type.value,
                "content": memory.content,
                "metadata": memory.metadata,
                "embedding": memory.embedding,
                "created_at": memory.created_at,
                "updated_at": memory.updated_at,
                "project_id": memory.project_id,
                "agent_id": memory.agent_id,
                "session_id": memory.session_id,
                "tags": memory.tags,
                "relevance_score": memory.relevance_score,
                "content_hash": memory.content_hash,
                "summary": memory.summary,
                "compressed_content": memory.compressed_content,
                "retention_priority": memory.retention_priority,
                "last_accessed": memory.last_accessed,
                "access_count": memory.access_count
            }
            
            await self.memories.insert_one(memory_dict)
            
        except Exception as e:
            logger.error(f"Failed to add memory to document store: {str(e)}")
            raise
            
    async def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by ID
        
        Args:
            memory_id: ID of memory to retrieve
            
        Returns:
            Memory entry if found, None otherwise
        """
        try:
            memory_dict = await self.memories.find_one({"id": memory_id})
            if not memory_dict:
                return None
                
            # Update access statistics
            await self._update_access_stats(memory_id)
                
            return self._dict_to_memory(memory_dict)
            
        except Exception as e:
            logger.error(f"Failed to retrieve memory from document store: {str(e)}")
            raise
            
    async def update_memory(self, memory: MemoryEntry) -> None:
        """Update a memory entry in the document store
        
        Args:
            memory: Updated memory entry
        """
        try:
            # Convert memory to dict
            memory_dict = {
                "id": memory.id,
                "type": memory.type.value,
                "content": memory.content,
                "metadata": memory.metadata,
                "embedding": memory.embedding,
                "updated_at": memory.updated_at,
                "project_id": memory.project_id,
                "agent_id": memory.agent_id,
                "session_id": memory.session_id,
                "tags": memory.tags,
                "relevance_score": memory.relevance_score,
                "content_hash": memory.content_hash,
                "summary": memory.summary,
                "compressed_content": memory.compressed_content,
                "retention_priority": memory.retention_priority,
                "last_accessed": memory.last_accessed,
                "access_count": memory.access_count
            }
            
            await self.memories.update_one(
                {"id": memory.id},
                {"$set": memory_dict}
            )
            
        except Exception as e:
            logger.error(f"Failed to update memory in document store: {str(e)}")
            raise
            
    async def delete_memory(self, memory_id: str) -> None:
        """Delete a memory entry from the document store
        
        Args:
            memory_id: ID of memory to delete
        """
        try:
            await self.memories.delete_one({"id": memory_id})
            
        except Exception as e:
            logger.error(f"Failed to delete memory from document store: {str(e)}")
            raise
            
    async def get_memories_by_type(
        self,
        memory_type: MemoryType,
        limit: int = 100,
        skip: int = 0
    ) -> List[MemoryEntry]:
        """Retrieve memories by type
        
        Args:
            memory_type: Type of memories to retrieve
            limit: Maximum number of results
            skip: Number of results to skip
            
        Returns:
            List of memory entries
        """
        try:
            cursor = self.memories.find(
                {"type": memory_type.value}
            ).sort("created_at", -1).skip(skip).limit(limit)
            
            memories = []
            async for memory_dict in cursor:
                memories.append(self._dict_to_memory(memory_dict))
                
            return memories
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories by type: {str(e)}")
            raise
            
    async def get_memories_by_project(
        self,
        project_id: str,
        limit: int = 100,
        skip: int = 0
    ) -> List[MemoryEntry]:
        """Retrieve memories by project ID
        
        Args:
            project_id: Project ID to filter by
            limit: Maximum number of results
            skip: Number of results to skip
            
        Returns:
            List of memory entries
        """
        try:
            cursor = self.memories.find(
                {"project_id": project_id}
            ).sort("created_at", -1).skip(skip).limit(limit)
            
            memories = []
            async for memory_dict in cursor:
                memories.append(self._dict_to_memory(memory_dict))
                
            return memories
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories by project: {str(e)}")
            raise
            
    async def get_memories_by_tags(
        self,
        tags: List[str],
        limit: int = 100,
        skip: int = 0
    ) -> List[MemoryEntry]:
        """Retrieve memories by tags
        
        Args:
            tags: List of tags to filter by
            limit: Maximum number of results
            skip: Number of results to skip
            
        Returns:
            List of memory entries
        """
        try:
            cursor = self.memories.find(
                {"tags": {"$all": tags}}
            ).sort("created_at", -1).skip(skip).limit(limit)
            
            memories = []
            async for memory_dict in cursor:
                memories.append(self._dict_to_memory(memory_dict))
                
            return memories
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories by tags: {str(e)}")
            raise
            
    async def get_memories_by_access_count(
        self,
        min_count: int = 0,
        limit: int = 100,
        skip: int = 0
    ) -> List[MemoryEntry]:
        """Retrieve memories by access count
        
        Args:
            min_count: Minimum access count
            limit: Maximum number of results
            skip: Number of results to skip
            
        Returns:
            List of memory entries
        """
        try:
            cursor = self.memories.find(
                {"access_count": {"$gte": min_count}}
            ).sort("access_count", -1).skip(skip).limit(limit)
            
            memories = []
            async for memory_dict in cursor:
                memories.append(self._dict_to_memory(memory_dict))
                
            return memories
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories by access count: {str(e)}")
            raise
            
    async def _update_access_stats(self, memory_id: str) -> None:
        """Update access statistics for a memory
        
        Args:
            memory_id: ID of memory to update
        """
        try:
            current_time = datetime.now().isoformat()
            await self.memories.update_one(
                {"id": memory_id},
                {
                    "$inc": {"access_count": 1},
                    "$set": {"last_accessed": current_time}
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to update access stats: {str(e)}")
            
    async def store_context(self, context_dict: Dict[str, Any]) -> None:
        """Store a context in the document store
        
        Args:
            context_dict: Context dictionary to store
        """
        try:
            # Convert sets to lists for MongoDB storage
            context_dict["memory_ids"] = list(context_dict.get("memory_ids", []))
            context_dict["child_ids"] = list(context_dict.get("child_ids", []))
            
            # Store context
            await self.contexts.update_one(
                {"id": context_dict["id"]},
                {"$set": context_dict},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Failed to store context: {str(e)}")
            raise
            
    async def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a context by ID
        
        Args:
            context_id: ID of context to retrieve
            
        Returns:
            Context dictionary if found, None otherwise
        """
        try:
            context_dict = await self.contexts.find_one({"id": context_id})
            if not context_dict:
                return None
                
            # Convert lists back to sets
            context_dict["memory_ids"] = set(context_dict.get("memory_ids", []))
            context_dict["child_ids"] = set(context_dict.get("child_ids", []))
            
            return context_dict
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {str(e)}")
            raise
            
    async def delete_context(self, context_id: str) -> None:
        """Delete a context from the document store
        
        Args:
            context_id: ID of context to delete
        """
        try:
            await self.contexts.delete_one({"id": context_id})
            
        except Exception as e:
            logger.error(f"Failed to delete context: {str(e)}")
            raise
            
    async def get_contexts_for_memory(
        self,
        memory_id: str
    ) -> List[ContextReference]:
        """Get all contexts for a memory
        
        Args:
            memory_id: ID of memory
            
        Returns:
            List of context references
        """
        try:
            cursor = self.contexts.find({"memory_ids": memory_id})
            contexts = []
            async for context_dict in cursor:
                # Convert lists back to sets
                context_dict["memory_ids"] = set(context_dict.get("memory_ids", []))
                context_dict["child_ids"] = set(context_dict.get("child_ids", []))
                contexts.append(ContextReference(**context_dict))
                
            return contexts
            
        except Exception as e:
            logger.error(f"Failed to get contexts for memory: {str(e)}")
            raise
            
    async def search_contexts(
        self,
        query: str,
        context_type: Optional[str] = None,
        limit: int = 10
    ) -> List[ContextReference]:
        """Search contexts by query
        
        Args:
            query: Search query
            context_type: Optional context type filter
            limit: Maximum number of results
            
        Returns:
            List of matching context references
        """
        try:
            # Build search filter
            filter_dict = {}
            if context_type:
                filter_dict["type"] = context_type
                
            # Search in name and description
            filter_dict["$or"] = [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
            
            # Execute search
            cursor = self.contexts.find(filter_dict).limit(limit)
            contexts = []
            async for context_dict in cursor:
                # Convert lists back to sets
                context_dict["memory_ids"] = set(context_dict.get("memory_ids", []))
                context_dict["child_ids"] = set(context_dict.get("child_ids", []))
                contexts.append(ContextReference(**context_dict))
                
            return contexts
            
        except Exception as e:
            logger.error(f"Failed to search contexts: {str(e)}")
            raise
            
    async def update_context_access_stats(
        self,
        context_id: str,
        current_time: str
    ) -> None:
        """Update access statistics for a context
        
        Args:
            context_id: ID of context to update
            current_time: Current timestamp
        """
        try:
            await self.contexts.update_one(
                {"id": context_id},
                {
                    "$inc": {"access_count": 1},
                    "$set": {"last_accessed": current_time}
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to update context access stats: {str(e)}")
            
    async def export_backup(self, backup_path: str) -> None:
        """Export document store to backup file
        
        Args:
            backup_path: Path to save backup
        """
        try:
            # Create backup directory
            os.makedirs(backup_path, exist_ok=True)
            
            # Export memories
            cursor = self.memories.find({})
            memories = []
            async for memory_dict in cursor:
                memories.append(memory_dict)
                
            # Export contexts
            cursor = self.contexts.find({})
            contexts = []
            async for context_dict in cursor:
                contexts.append(context_dict)
                
            # Save to JSON files
            with open(os.path.join(backup_path, "memories.json"), "w") as f:
                json.dump(memories, f, default=str)
                
            with open(os.path.join(backup_path, "contexts.json"), "w") as f:
                json.dump(contexts, f, default=str)
                
            # Export indexes
            memory_indexes = await self.memories.list_indexes().to_list(None)
            context_indexes = await self.contexts.list_indexes().to_list(None)
            
            with open(os.path.join(backup_path, "indexes.json"), "w") as f:
                json.dump({
                    "memories": memory_indexes,
                    "contexts": context_indexes
                }, f)
                
        except Exception as e:
            logger.error(f"Failed to export backup: {str(e)}")
            raise
            
    async def import_backup(self, backup_path: str) -> None:
        """Import document store from backup file
        
        Args:
            backup_path: Path to load backup from
        """
        try:
            # Clear existing data
            await self.memories.delete_many({})
            await self.contexts.delete_many({})
            
            # Load memories
            with open(os.path.join(backup_path, "memories.json"), "r") as f:
                memories = json.load(f)
                
            # Load contexts
            with open(os.path.join(backup_path, "contexts.json"), "r") as f:
                contexts = json.load(f)
                
            # Insert data
            if memories:
                await self.memories.insert_many(memories)
                
            if contexts:
                await self.contexts.insert_many(contexts)
                
            # Recreate indexes
            with open(os.path.join(backup_path, "indexes.json"), "r") as f:
                indexes = json.load(f)
                
            # Recreate memory indexes
            for index in indexes["memories"]:
                if index.get("name") != "_id_":  # Skip _id index
                    await self.memories.create_index(
                        index["key"].items(),
                        name=index["name"],
                        unique=index.get("unique", False)
                    )
                    
            # Recreate context indexes
            for index in indexes["contexts"]:
                if index.get("name") != "_id_":  # Skip _id index
                    await self.contexts.create_index(
                        index["key"].items(),
                        name=index["name"],
                        unique=index.get("unique", False)
                    )
                    
        except Exception as e:
            logger.error(f"Failed to import backup: {str(e)}")
            raise
            
    def _dict_to_memory(self, memory_dict: Dict[str, Any]) -> MemoryEntry:
        """Convert dictionary to MemoryEntry
        
        Args:
            memory_dict: Dictionary representation of memory
            
        Returns:
            MemoryEntry instance
        """
        return MemoryEntry(
            id=memory_dict["id"],
            type=MemoryType(memory_dict["type"]),
            content=memory_dict["content"],
            metadata=memory_dict["metadata"],
            embedding=memory_dict["embedding"],
            created_at=memory_dict["created_at"],
            updated_at=memory_dict["updated_at"],
            project_id=memory_dict.get("project_id"),
            agent_id=memory_dict.get("agent_id"),
            session_id=memory_dict.get("session_id"),
            tags=memory_dict.get("tags", []),
            relevance_score=memory_dict.get("relevance_score", 0.0),
            content_hash=memory_dict.get("content_hash"),
            summary=memory_dict.get("summary"),
            compressed_content=memory_dict.get("compressed_content"),
            retention_priority=memory_dict.get("retention_priority", 1.0),
            last_accessed=memory_dict.get("last_accessed"),
            access_count=memory_dict.get("access_count", 0)
        ) 