from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
import os

from .memory_manager import MemoryEntry, MemoryType

logger = logging.getLogger(__name__)

class ContextType(Enum):
    """Types of contexts"""
    PROJECT = "project"
    SESSION = "session"
    AGENT = "agent"
    TASK = "task"
    DOMAIN = "domain"
    CUSTOM = "custom"

@dataclass
class ContextReference:
    """Represents a context reference"""
    id: str
    type: ContextType
    name: str
    description: str
    metadata: Dict[str, Any]
    created_at: str = datetime.now().isoformat()
    updated_at: str = datetime.now().isoformat()
    parent_id: Optional[str] = None
    memory_ids: Set[str] = None
    child_ids: Set[str] = None
    tags: List[str] = None
    relevance_score: float = 0.0
    last_accessed: str = datetime.now().isoformat()
    access_count: int = 0

class ContextManager:
    """Manages context references and their relationships"""
    
    def __init__(self, document_store):
        """Initialize context manager
        
        Args:
            document_store: DocumentStore instance for persistence
        """
        self.document_store = document_store
        self.contexts: Dict[str, ContextReference] = {}
        self.context_cache: Dict[str, Set[str]] = {}  # memory_id -> context_ids
        
    async def create_context(
        self,
        context_type: ContextType,
        name: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> ContextReference:
        """Create a new context reference
        
        Args:
            context_type: Type of context
            name: Name of the context
            description: Description of the context
            metadata: Additional metadata
            parent_id: ID of parent context
            tags: List of tags
            
        Returns:
            Created context reference
        """
        try:
            # Generate context ID
            context_id = self._generate_context_id()
            
            # Create context reference
            context = ContextReference(
                id=context_id,
                type=context_type,
                name=name,
                description=description,
                metadata=metadata or {},
                parent_id=parent_id,
                memory_ids=set(),
                child_ids=set(),
                tags=tags or []
            )
            
            # Store context
            await self._store_context(context)
            
            # Update parent if exists
            if parent_id:
                await self._update_parent_context(parent_id, context_id)
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to create context: {str(e)}")
            raise
    
    async def get_context(self, context_id: str) -> Optional[ContextReference]:
        """Retrieve a context reference by ID
        
        Args:
            context_id: ID of context to retrieve
            
        Returns:
            Context reference if found, None otherwise
        """
        try:
            # Check cache first
            if context_id in self.contexts:
                context = self.contexts[context_id]
                await self._update_access_stats(context_id)
                return context
            
            # Retrieve from document store
            context_dict = await self.document_store.get_context(context_id)
            if not context_dict:
                return None
            
            # Convert to ContextReference
            context = self._dict_to_context(context_dict)
            
            # Update cache
            self.contexts[context_id] = context
            
            # Update access stats
            await self._update_access_stats(context_id)
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {str(e)}")
            raise
    
    async def update_context(
        self,
        context_id: str,
        updates: Dict[str, Any]
    ) -> ContextReference:
        """Update a context reference
        
        Args:
            context_id: ID of context to update
            updates: Fields to update
            
        Returns:
            Updated context reference
        """
        try:
            # Retrieve existing context
            context = await self.get_context(context_id)
            if not context:
                raise ValueError(f"Context not found: {context_id}")
            
            # Update fields
            for key, value in updates.items():
                if hasattr(context, key):
                    setattr(context, key, value)
            
            context.updated_at = datetime.now().isoformat()
            
            # Store updated context
            await self._store_context(context)
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to update context: {str(e)}")
            raise
    
    async def delete_context(self, context_id: str) -> bool:
        """Delete a context reference
        
        Args:
            context_id: ID of context to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            # Retrieve context
            context = await self.get_context(context_id)
            if not context:
                return False
            
            # Remove from parent if exists
            if context.parent_id:
                await self._remove_from_parent(context.parent_id, context_id)
            
            # Remove from document store
            await self.document_store.delete_context(context_id)
            
            # Remove from cache
            if context_id in self.contexts:
                del self.contexts[context_id]
            
            # Remove from context cache
            for memory_ids in self.context_cache.values():
                memory_ids.discard(context_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete context: {str(e)}")
            return False
    
    async def add_memory_to_context(
        self,
        context_id: str,
        memory_id: str
    ) -> bool:
        """Add a memory to a context
        
        Args:
            context_id: ID of context
            memory_id: ID of memory to add
            
        Returns:
            True if added, False otherwise
        """
        try:
            # Retrieve context
            context = await self.get_context(context_id)
            if not context:
                return False
            
            # Add memory ID
            context.memory_ids.add(memory_id)
            
            # Update context
            await self._store_context(context)
            
            # Update context cache
            if memory_id not in self.context_cache:
                self.context_cache[memory_id] = set()
            self.context_cache[memory_id].add(context_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add memory to context: {str(e)}")
            return False
    
    async def remove_memory_from_context(
        self,
        context_id: str,
        memory_id: str
    ) -> bool:
        """Remove a memory from a context
        
        Args:
            context_id: ID of context
            memory_id: ID of memory to remove
            
        Returns:
            True if removed, False otherwise
        """
        try:
            # Retrieve context
            context = await self.get_context(context_id)
            if not context:
                return False
            
            # Remove memory ID
            context.memory_ids.discard(memory_id)
            
            # Update context
            await self._store_context(context)
            
            # Update context cache
            if memory_id in self.context_cache:
                self.context_cache[memory_id].discard(context_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove memory from context: {str(e)}")
            return False
    
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
            # Check cache first
            if memory_id in self.context_cache:
                context_ids = self.context_cache[memory_id]
                contexts = []
                for context_id in context_ids:
                    context = await self.get_context(context_id)
                    if context:
                        contexts.append(context)
                return contexts
            
            # Retrieve from document store
            contexts = await self.document_store.get_contexts_for_memory(memory_id)
            
            # Update cache
            self.context_cache[memory_id] = {context.id for context in contexts}
            
            return contexts
            
        except Exception as e:
            logger.error(f"Failed to get contexts for memory: {str(e)}")
            raise
    
    async def get_child_contexts(
        self,
        context_id: str
    ) -> List[ContextReference]:
        """Get all child contexts of a context
        
        Args:
            context_id: ID of parent context
            
        Returns:
            List of child context references
        """
        try:
            # Retrieve context
            context = await self.get_context(context_id)
            if not context:
                return []
            
            # Get child contexts
            child_contexts = []
            for child_id in context.child_ids:
                child_context = await self.get_context(child_id)
                if child_context:
                    child_contexts.append(child_context)
            
            return child_contexts
            
        except Exception as e:
            logger.error(f"Failed to get child contexts: {str(e)}")
            raise
    
    async def get_parent_context(
        self,
        context_id: str
    ) -> Optional[ContextReference]:
        """Get parent context of a context
        
        Args:
            context_id: ID of child context
            
        Returns:
            Parent context reference if found, None otherwise
        """
        try:
            # Retrieve context
            context = await self.get_context(context_id)
            if not context or not context.parent_id:
                return None
            
            # Get parent context
            return await self.get_context(context.parent_id)
            
        except Exception as e:
            logger.error(f"Failed to get parent context: {str(e)}")
            raise
    
    async def search_contexts(
        self,
        query: str,
        context_type: Optional[ContextType] = None,
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
            # Search in document store
            contexts = await self.document_store.search_contexts(
                query,
                context_type.value if context_type else None,
                limit
            )
            
            return contexts
            
        except Exception as e:
            logger.error(f"Failed to search contexts: {str(e)}")
            raise
    
    async def _store_context(self, context: ContextReference) -> None:
        """Store a context reference in the document store
        
        Args:
            context: Context reference to store
        """
        try:
            # Convert to dict
            context_dict = {
                "id": context.id,
                "type": context.type.value,
                "name": context.name,
                "description": context.description,
                "metadata": context.metadata,
                "created_at": context.created_at,
                "updated_at": context.updated_at,
                "parent_id": context.parent_id,
                "memory_ids": list(context.memory_ids),
                "child_ids": list(context.child_ids),
                "tags": context.tags,
                "relevance_score": context.relevance_score,
                "last_accessed": context.last_accessed,
                "access_count": context.access_count
            }
            
            # Store in document store
            await self.document_store.store_context(context_dict)
            
            # Update cache
            self.contexts[context.id] = context
            
        except Exception as e:
            logger.error(f"Failed to store context: {str(e)}")
            raise
    
    async def _update_parent_context(
        self,
        parent_id: str,
        child_id: str
    ) -> None:
        """Update parent context with child ID
        
        Args:
            parent_id: ID of parent context
            child_id: ID of child context
        """
        try:
            # Retrieve parent context
            parent = await self.get_context(parent_id)
            if not parent:
                raise ValueError(f"Parent context not found: {parent_id}")
            
            # Add child ID
            parent.child_ids.add(child_id)
            
            # Update parent context
            await self._store_context(parent)
            
        except Exception as e:
            logger.error(f"Failed to update parent context: {str(e)}")
            raise
    
    async def _remove_from_parent(
        self,
        parent_id: str,
        child_id: str
    ) -> None:
        """Remove child ID from parent context
        
        Args:
            parent_id: ID of parent context
            child_id: ID of child context
        """
        try:
            # Retrieve parent context
            parent = await self.get_context(parent_id)
            if not parent:
                return
            
            # Remove child ID
            parent.child_ids.discard(child_id)
            
            # Update parent context
            await self._store_context(parent)
            
        except Exception as e:
            logger.error(f"Failed to remove from parent: {str(e)}")
    
    async def _update_access_stats(self, context_id: str) -> None:
        """Update access statistics for a context
        
        Args:
            context_id: ID of context to update
        """
        try:
            current_time = datetime.now().isoformat()
            await self.document_store.update_context_access_stats(
                context_id,
                current_time
            )
            
        except Exception as e:
            logger.error(f"Failed to update access stats: {str(e)}")
    
    def _generate_context_id(self) -> str:
        """Generate a unique context ID"""
        return f"ctx_{datetime.now().timestamp()}_{os.urandom(4).hex()}"
    
    def _dict_to_context(self, context_dict: Dict[str, Any]) -> ContextReference:
        """Convert dictionary to ContextReference
        
        Args:
            context_dict: Dictionary representation of context
            
        Returns:
            ContextReference instance
        """
        return ContextReference(
            id=context_dict["id"],
            type=ContextType(context_dict["type"]),
            name=context_dict["name"],
            description=context_dict["description"],
            metadata=context_dict["metadata"],
            created_at=context_dict["created_at"],
            updated_at=context_dict["updated_at"],
            parent_id=context_dict.get("parent_id"),
            memory_ids=set(context_dict.get("memory_ids", [])),
            child_ids=set(context_dict.get("child_ids", [])),
            tags=context_dict.get("tags", []),
            relevance_score=context_dict.get("relevance_score", 0.0),
            last_accessed=context_dict.get("last_accessed"),
            access_count=context_dict.get("access_count", 0)
        ) 