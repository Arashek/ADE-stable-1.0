from typing import Dict, Any, List, Optional, Union, Tuple
import logging
from datetime import datetime
import json
from dataclasses import dataclass, asdict
from enum import Enum
import os
import hashlib

from ..core.provider_registry import ProviderRegistry
from ..core.orchestrator import Orchestrator
from ..agents.base import BaseAgent
from .vector_store import VectorStore
from .document_store import DocumentStore
from .knowledge_graph import KnowledgeGraph
from .context_manager import ContextManager, ContextType
from .multimodal_processor import MultiModalProcessor, InputType, ProcessedInput

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Types of memories"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    CODE = "code"
    STRUCTURED_DATA = "structured_data"
    EXPERIENCE = "experience"
    KNOWLEDGE = "knowledge"
    SKILL = "skill"
    PREFERENCE = "preference"
    GOAL = "goal"
    TASK = "task"
    ERROR = "error"
    SOLUTION = "solution"
    INSIGHT = "insight"
    DECISION = "decision"
    ACTION = "action"
    OUTCOME = "outcome"
    FEEDBACK = "feedback"
    METADATA = "metadata"

@dataclass
class MemoryEntry:
    """Represents a memory entry"""
    id: str
    type: MemoryType
    content: str
    metadata: Dict[str, Any]
    embedding: List[float]
    created_at: str = datetime.now().isoformat()
    updated_at: str = datetime.now().isoformat()
    project_id: Optional[str] = None
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: List[str] = None
    relevance_score: float = 0.0
    content_hash: Optional[str] = None
    summary: Optional[str] = None
    compressed_content: Optional[str] = None
    retention_priority: float = 1.0
    last_accessed: str = datetime.now().isoformat()
    access_count: int = 0

class MemoryManager:
    """Manages memory operations"""
    
    def __init__(
        self,
        mongo_uri: str,
        vector_store_path: str,
        knowledge_graph_path: str,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """Initialize memory manager
        
        Args:
            mongo_uri: MongoDB connection URI
            vector_store_path: Path to vector store
            knowledge_graph_path: Path to knowledge graph
            model_name: Name of the model to use for embeddings
        """
        # Initialize stores
        self.document_store = DocumentStore(mongo_uri)
        self.vector_store = VectorStore(vector_store_path)
        self.knowledge_graph = KnowledgeGraph(knowledge_graph_path)
        self.context_manager = ContextManager(self.document_store)
        
        # Initialize multimodal processor
        self.multimodal_processor = MultiModalProcessor(model_name)
        
        # Cache
        self.memory_cache: Dict[str, MemoryEntry] = {}
        self.context_cache: Dict[str, Set[str]] = {}
        
        # Configuration
        self.max_cache_size = 1000
        self.cache_ttl = 3600  # 1 hour
        self.retention_periods = {
            MemoryType.TEXT: 30,  # days
            MemoryType.IMAGE: 90,
            MemoryType.AUDIO: 60,
            MemoryType.VIDEO: 90,
            MemoryType.DOCUMENT: 365,
            MemoryType.CODE: 180,
            MemoryType.STRUCTURED_DATA: 30,
            MemoryType.EXPERIENCE: 365,
            MemoryType.KNOWLEDGE: 730,  # 2 years
            MemoryType.SKILL: 730,
            MemoryType.PREFERENCE: 365,
            MemoryType.GOAL: 180,
            MemoryType.TASK: 90,
            MemoryType.ERROR: 365,
            MemoryType.SOLUTION: 365,
            MemoryType.INSIGHT: 365,
            MemoryType.DECISION: 365,
            MemoryType.ACTION: 90,
            MemoryType.OUTCOME: 90,
            MemoryType.FEEDBACK: 90,
            MemoryType.METADATA: 30
        }
        
    async def store_memory(
        self,
        content: Union[str, bytes, Dict[str, Any]],
        memory_type: MemoryType,
        metadata: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        context_ids: Optional[List[str]] = None
    ) -> MemoryEntry:
        """Store a memory
        
        Args:
            content: Memory content
            memory_type: Type of memory
            metadata: Additional metadata
            project_id: Project ID
            agent_id: Agent ID
            session_id: Session ID
            tags: List of tags
            context_ids: List of context IDs
            
        Returns:
            Created memory entry
        """
        try:
            # Process input based on type
            input_type = self._get_input_type(memory_type)
            processed_input = await self.multimodal_processor.process_input(
                content,
                input_type,
                metadata
            )
            
            # Generate memory ID
            memory_id = self._generate_memory_id()
            
            # Create memory entry
            memory = MemoryEntry(
                id=memory_id,
                type=memory_type,
                content=processed_input.content,
                metadata=processed_input.metadata,
                embedding=processed_input.embedding,
                project_id=project_id,
                agent_id=agent_id,
                session_id=session_id,
                tags=tags or [],
                content_hash=processed_input.content_hash,
                summary=processed_input.summary,
                compressed_content=processed_input.compressed_content,
                retention_priority=self._calculate_retention_priority(memory_type)
            )
            
            # Store in document store
            await self.document_store.add_memory(memory)
            
            # Store in vector store
            await self.vector_store.add_memory(memory)
            
            # Update knowledge graph
            await self.knowledge_graph.add_memory(memory)
            
            # Add to contexts if specified
            if context_ids:
                for context_id in context_ids:
                    await self.context_manager.add_memory_to_context(
                        context_id,
                        memory_id
                    )
            
            # Update cache
            self._update_cache(memory)
            
            return memory
            
        except Exception as e:
            logger.error(f"Failed to store memory: {str(e)}")
            raise
            
    async def retrieve_memories(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
        context_id: Optional[str] = None
    ) -> List[MemoryEntry]:
        """Retrieve memories by query
        
        Args:
            query: Search query
            memory_type: Optional memory type filter
            limit: Maximum number of results
            context_id: Optional context ID
            
        Returns:
            List of memory entries
        """
        try:
            # Get memories from vector store
            memories = await self.vector_store.search_memories(
                query,
                memory_type,
                limit
            )
            
            # Filter by context if specified
            if context_id:
                context_memories = await self.context_manager.get_contexts_for_memory(
                    context_id
                )
                memory_ids = {memory.id for memory in context_memories}
                memories = [
                    memory for memory in memories
                    if memory.id in memory_ids
                ]
            
            # Update access statistics
            for memory in memories:
                await self._update_access_stats(memory.id)
                
            return memories
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {str(e)}")
            raise
            
    async def update_memory(
        self,
        memory_id: str,
        updates: Dict[str, Any]
    ) -> MemoryEntry:
        """Update a memory
        
        Args:
            memory_id: ID of memory to update
            updates: Fields to update
            
        Returns:
            Updated memory entry
        """
        try:
            # Retrieve existing memory
            memory = await self.get_memory(memory_id)
            if not memory:
                raise ValueError(f"Memory not found: {memory_id}")
            
            # Update fields
            for key, value in updates.items():
                if hasattr(memory, key):
                    setattr(memory, key, value)
            
            memory.updated_at = datetime.now().isoformat()
            
            # Store updated memory
            await self.document_store.update_memory(memory)
            await self.vector_store.update_memory(memory)
            await self.knowledge_graph.update_memory(memory)
            
            # Update cache
            self._update_cache(memory)
            
            return memory
            
        except Exception as e:
            logger.error(f"Failed to update memory: {str(e)}")
            raise
            
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory
        
        Args:
            memory_id: ID of memory to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            # Remove from stores
            await self.document_store.delete_memory(memory_id)
            await self.vector_store.delete_memory(memory_id)
            await self.knowledge_graph.delete_memory(memory_id)
            
            # Remove from contexts
            contexts = await self.context_manager.get_contexts_for_memory(memory_id)
            for context in contexts:
                await self.context_manager.remove_memory_from_context(
                    context.id,
                    memory_id
                )
            
            # Remove from cache
            if memory_id in self.memory_cache:
                del self.memory_cache[memory_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete memory: {str(e)}")
            return False
            
    async def get_related_memories(
        self,
        memory_id: str,
        relationship_type: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Get memories related to a memory
        
        Args:
            memory_id: ID of memory
            relationship_type: Optional relationship type filter
            limit: Maximum number of results
            
        Returns:
            List of related memory entries
        """
        try:
            # Get related memories from knowledge graph
            related_memories = await self.knowledge_graph.get_related_memories(
                memory_id,
                relationship_type,
                limit
            )
            
            # Update access statistics
            for memory in related_memories:
                await self._update_access_stats(memory.id)
                
            return related_memories
            
        except Exception as e:
            logger.error(f"Failed to get related memories: {str(e)}")
            raise
            
    async def get_memory_path(
        self,
        source_id: str,
        target_id: str,
        max_length: int = 5
    ) -> List[Dict[str, Any]]:
        """Find path between two memories
        
        Args:
            source_id: ID of source memory
            target_id: ID of target memory
            max_length: Maximum path length
            
        Returns:
            List of edges in path
        """
        try:
            return await self.knowledge_graph.get_memory_path(
                source_id,
                target_id,
                max_length
            )
            
        except Exception as e:
            logger.error(f"Failed to get memory path: {str(e)}")
            raise
            
    async def get_memory_cluster(
        self,
        memory_id: str,
        min_similarity: float = 0.5,
        max_size: int = 10
    ) -> List[MemoryEntry]:
        """Get cluster of related memories
        
        Args:
            memory_id: ID of memory
            min_similarity: Minimum similarity threshold
            max_size: Maximum cluster size
            
        Returns:
            List of memory entries in cluster
        """
        try:
            # Get cluster from knowledge graph
            cluster = await self.knowledge_graph.get_memory_cluster(
                memory_id,
                min_similarity,
                max_size
            )
            
            # Update access statistics
            for memory in cluster:
                await self._update_access_stats(memory.id)
                
            return cluster
            
        except Exception as e:
            logger.error(f"Failed to get memory cluster: {str(e)}")
            raise
            
    async def cleanup_memories(self) -> None:
        """Clean up old memories based on retention policies"""
        try:
            current_time = datetime.now()
            
            # Get all memories
            memories = await self.document_store.get_memories_by_type(
                MemoryType.TEXT,
                limit=1000
            )
            
            for memory in memories:
                # Calculate age in days
                created_at = datetime.fromisoformat(memory.created_at)
                age_days = (current_time - created_at).days
                
                # Check retention period
                retention_days = self.retention_periods.get(memory.type, 30)
                if age_days > retention_days:
                    # Delete memory
                    await self.delete_memory(memory.id)
                    
        except Exception as e:
            logger.error(f"Failed to cleanup memories: {str(e)}")
            
    async def backup_memories(self, backup_path: str) -> None:
        """Backup memory state
        
        Args:
            backup_path: Path to save backup
        """
        try:
            # Create backup directory
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup document store
            await self.document_store.export_backup(backup_path)
            
            # Backup vector store
            await self.vector_store.save(backup_path)
            
            # Backup knowledge graph
            await self.knowledge_graph.save(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to backup memories: {str(e)}")
            raise
            
    async def restore_memories(self, backup_path: str) -> None:
        """Restore memory state from backup
        
        Args:
            backup_path: Path to load backup from
        """
        try:
            # Restore document store
            await self.document_store.import_backup(backup_path)
            
            # Restore vector store
            await self.vector_store.load(backup_path)
            
            # Restore knowledge graph
            await self.knowledge_graph.load(backup_path)
            
            # Clear cache
            self.memory_cache.clear()
            self.context_cache.clear()
            
        except Exception as e:
            logger.error(f"Failed to restore memories: {str(e)}")
            raise
            
    def _get_input_type(self, memory_type: MemoryType) -> InputType:
        """Get input type for memory type
        
        Args:
            memory_type: Memory type
            
        Returns:
            Corresponding input type
        """
        type_mapping = {
            MemoryType.TEXT: InputType.TEXT,
            MemoryType.IMAGE: InputType.IMAGE,
            MemoryType.AUDIO: InputType.AUDIO,
            MemoryType.VIDEO: InputType.VIDEO,
            MemoryType.DOCUMENT: InputType.DOCUMENT,
            MemoryType.CODE: InputType.CODE,
            MemoryType.STRUCTURED_DATA: InputType.STRUCTURED_DATA
        }
        return type_mapping.get(memory_type, InputType.TEXT)
        
    def _generate_memory_id(self) -> str:
        """Generate a unique memory ID"""
        return f"mem_{datetime.now().timestamp()}_{os.urandom(4).hex()}"
        
    def _calculate_retention_priority(self, memory_type: MemoryType) -> float:
        """Calculate retention priority for memory type
        
        Args:
            memory_type: Memory type
            
        Returns:
            Retention priority
        """
        priority_mapping = {
            MemoryType.KNOWLEDGE: 1.0,
            MemoryType.SKILL: 1.0,
            MemoryType.ERROR: 0.9,
            MemoryType.SOLUTION: 0.9,
            MemoryType.INSIGHT: 0.8,
            MemoryType.DECISION: 0.8,
            MemoryType.EXPERIENCE: 0.7,
            MemoryType.PREFERENCE: 0.7,
            MemoryType.GOAL: 0.6,
            MemoryType.TASK: 0.6,
            MemoryType.ACTION: 0.5,
            MemoryType.OUTCOME: 0.5,
            MemoryType.FEEDBACK: 0.4,
            MemoryType.METADATA: 0.3
        }
        return priority_mapping.get(memory_type, 0.5)
        
    def _update_cache(self, memory: MemoryEntry) -> None:
        """Update memory cache
        
        Args:
            memory: Memory entry to cache
        """
        # Remove oldest entry if cache is full
        if len(self.memory_cache) >= self.max_cache_size:
            oldest_id = min(
                self.memory_cache.items(),
                key=lambda x: datetime.fromisoformat(x[1].last_accessed)
            )[0]
            del self.memory_cache[oldest_id]
            
        # Add to cache
        self.memory_cache[memory.id] = memory
        
    async def _update_access_stats(self, memory_id: str) -> None:
        """Update access statistics for a memory
        
        Args:
            memory_id: ID of memory to update
        """
        try:
            current_time = datetime.now().isoformat()
            
            # Update document store
            await self.document_store._update_access_stats(memory_id)
            
            # Update cache if present
            if memory_id in self.memory_cache:
                memory = self.memory_cache[memory_id]
                memory.last_accessed = current_time
                memory.access_count += 1
                
        except Exception as e:
            logger.error(f"Failed to update access stats: {str(e)}") 