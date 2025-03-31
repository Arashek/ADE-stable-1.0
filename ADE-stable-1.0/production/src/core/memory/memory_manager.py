import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import sqlite3
from pathlib import Path
import threading
import asyncio
from uuid import uuid4

from ..agent_communication import Message, MessageCategory, MessagePriority

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    WORKING = "working"  # Short-term, high-priority information
    EPISODIC = "episodic"  # Recent interactions and decisions
    SEMANTIC = "semantic"  # General knowledge and patterns
    PROCEDURAL = "procedural"  # Task execution knowledge

class MemoryAccess(Enum):
    PRIVATE = "private"  # Only accessible to the owner
    SHARED = "shared"  # Accessible to specific agents
    PUBLIC = "public"  # Accessible to all agents

@dataclass
class MemoryEntry:
    """Represents a single memory entry."""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: MemoryType
    content: Dict[str, Any]
    importance: float  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_level: MemoryAccess = MemoryAccess.PRIVATE
    owner_id: str
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    related_memories: List[str] = field(default_factory=list)  # IDs of related memories

class MemoryManager:
    """Manages hierarchical memory system for agents."""
    
    def __init__(self, db_path: str = "memory.db"):
        """Initialize the memory manager."""
        self.db_path = db_path
        self.lock = threading.Lock()
        self.working_memory: Dict[str, MemoryEntry] = {}
        self.working_memory_limit = 100  # Maximum number of working memory entries
        
        # Initialize database
        self._init_db()
        
        # Start memory consolidation thread
        self.consolidation_thread = threading.Thread(
            target=self._consolidate_memories,
            daemon=True
        )
        self.consolidation_thread.start()

    def _init_db(self) -> None:
        """Initialize the SQLite database for memory storage."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables for different memory types
            for memory_type in MemoryType:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {memory_type.value}_memory (
                        id TEXT PRIMARY KEY,
                        content TEXT,
                        importance REAL,
                        created_at TIMESTAMP,
                        last_accessed TIMESTAMP,
                        access_level TEXT,
                        owner_id TEXT,
                        tags TEXT,
                        context TEXT,
                        version INTEGER
                    )
                """)
            
            # Create table for memory relationships
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_relationships (
                    memory_id TEXT,
                    related_id TEXT,
                    relationship_type TEXT,
                    created_at TIMESTAMP,
                    PRIMARY KEY (memory_id, related_id)
                )
            """)
            
            # Create indices for efficient retrieval
            for memory_type in MemoryType:
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{memory_type.value}_owner 
                    ON {memory_type.value}_memory(owner_id)
                """)
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{memory_type.value}_tags 
                    ON {memory_type.value}_memory(tags)
                """)
            
            conn.commit()

    def add_memory(self, entry: MemoryEntry) -> bool:
        """Add a new memory entry."""
        try:
            with self.lock:
                if entry.type == MemoryType.WORKING:
                    # Handle working memory
                    if len(self.working_memory) >= self.working_memory_limit:
                        # Remove least important entry
                        self._prune_working_memory()
                    self.working_memory[entry.id] = entry
                else:
                    # Store in database
                    self._store_memory(entry)
                
                # Broadcast memory update if shared or public
                if entry.access_level in [MemoryAccess.SHARED, MemoryAccess.PUBLIC]:
                    self._broadcast_memory_update(entry)
                
                return True
                
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return False

    def retrieve_memories(self, 
                         memory_type: Optional[MemoryType] = None,
                         tags: Optional[List[str]] = None,
                         context: Optional[Dict[str, Any]] = None,
                         agent_id: Optional[str] = None,
                         limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memories based on criteria."""
        try:
            memories = []
            
            # Check working memory first
            if memory_type is None or memory_type == MemoryType.WORKING:
                for entry in self.working_memory.values():
                    if self._matches_criteria(entry, tags, context, agent_id):
                        memories.append(entry)
                        entry.last_accessed = datetime.now()
            
            # Retrieve from database for other memory types
            if memory_type is None or memory_type != MemoryType.WORKING:
                db_memories = self._retrieve_from_db(
                    memory_type, tags, context, agent_id, limit
                )
                memories.extend(db_memories)
            
            # Sort by importance and recency
            memories.sort(key=lambda x: (x.importance, x.last_accessed), reverse=True)
            return memories[:limit]
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []

    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory entry."""
        try:
            with self.lock:
                # Check working memory first
                if memory_id in self.working_memory:
                    entry = self.working_memory[memory_id]
                    for key, value in updates.items():
                        setattr(entry, key, value)
                    entry.version += 1
                    return True
                
                # Update in database
                return self._update_in_db(memory_id, updates)
                
        except Exception as e:
            logger.error(f"Error updating memory: {e}")
            return False

    def _consolidate_memories(self) -> None:
        """Periodically consolidate memories from working to long-term storage."""
        while True:
            try:
                with self.lock:
                    # Find important working memories
                    important_memories = [
                        entry for entry in self.working_memory.values()
                        if entry.importance > 0.7  # High importance threshold
                    ]
                    
                    # Move to appropriate long-term storage
                    for entry in important_memories:
                        if entry.type == MemoryType.WORKING:
                            # Determine appropriate long-term storage type
                            if "interaction" in entry.tags:
                                entry.type = MemoryType.EPISODIC
                            elif "pattern" in entry.tags:
                                entry.type = MemoryType.SEMANTIC
                            elif "procedure" in entry.tags:
                                entry.type = MemoryType.PROCEDURAL
                            
                            # Store in database
                            self._store_memory(entry)
                            del self.working_memory[entry.id]
                
                # Sleep for consolidation interval
                threading.Event().wait(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in memory consolidation: {e}")
                threading.Event().wait(60)  # Wait before retrying

    def _prune_working_memory(self) -> None:
        """Remove least important memories from working memory."""
        # Sort by importance and last accessed time
        sorted_memories = sorted(
            self.working_memory.items(),
            key=lambda x: (x[1].importance, x[1].last_accessed)
        )
        
        # Remove least important entries
        while len(self.working_memory) >= self.working_memory_limit:
            _, entry = sorted_memories.pop(0)
            del self.working_memory[entry.id]
            
            # Store important memories in database before removal
            if entry.importance > 0.5:
                self._store_memory(entry)

    def _store_memory(self, entry: MemoryEntry) -> None:
        """Store a memory entry in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store main memory entry
            cursor.execute(f"""
                INSERT OR REPLACE INTO {entry.type.value}_memory
                (id, content, importance, created_at, last_accessed, 
                 access_level, owner_id, tags, context, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.id,
                json.dumps(entry.content),
                entry.importance,
                entry.created_at.isoformat(),
                entry.last_accessed.isoformat(),
                entry.access_level.value,
                entry.owner_id,
                json.dumps(entry.tags),
                json.dumps(entry.context),
                entry.version
            ))
            
            # Store memory relationships
            for related_id in entry.related_memories:
                cursor.execute("""
                    INSERT OR REPLACE INTO memory_relationships
                    (memory_id, related_id, relationship_type, created_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    entry.id,
                    related_id,
                    "related",
                    datetime.now().isoformat()
                ))
            
            conn.commit()

    def _retrieve_from_db(self, 
                         memory_type: Optional[MemoryType],
                         tags: Optional[List[str]],
                         context: Optional[Dict[str, Any]],
                         agent_id: Optional[str],
                         limit: int) -> List[MemoryEntry]:
        """Retrieve memories from the database."""
        memories = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build query based on criteria
            query_parts = []
            params = []
            
            if memory_type:
                query_parts.append("type = ?")
                params.append(memory_type.value)
            
            if tags:
                query_parts.append("tags LIKE ?")
                params.append(f"%{json.dumps(tags)}%")
            
            if agent_id:
                query_parts.append("(owner_id = ? OR access_level = 'public')")
                params.append(agent_id)
            
            # Execute query for each memory type
            for mem_type in MemoryType:
                if memory_type and mem_type != memory_type:
                    continue
                
                query = f"""
                    SELECT * FROM {mem_type.value}_memory
                    WHERE {' AND '.join(query_parts) if query_parts else '1=1'}
                    ORDER BY importance DESC, last_accessed DESC
                    LIMIT ?
                """
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                for row in cursor.fetchall():
                    memories.append(MemoryEntry(
                        id=row[0],
                        type=mem_type,
                        content=json.loads(row[1]),
                        importance=row[2],
                        created_at=datetime.fromisoformat(row[3]),
                        last_accessed=datetime.fromisoformat(row[4]),
                        access_level=MemoryAccess(row[5]),
                        owner_id=row[6],
                        tags=json.loads(row[7]),
                        context=json.loads(row[8]),
                        version=row[9]
                    ))
        
        return memories

    def _matches_criteria(self, 
                         entry: MemoryEntry,
                         tags: Optional[List[str]],
                         context: Optional[Dict[str, Any]],
                         agent_id: Optional[str]) -> bool:
        """Check if a memory entry matches the retrieval criteria."""
        if tags and not all(tag in entry.tags for tag in tags):
            return False
        
        if context:
            for key, value in context.items():
                if key not in entry.context or entry.context[key] != value:
                    return False
        
        if agent_id and entry.access_level == MemoryAccess.PRIVATE and entry.owner_id != agent_id:
            return False
        
        return True

    def _broadcast_memory_update(self, entry: MemoryEntry) -> None:
        """Broadcast memory updates to relevant agents."""
        # This method should be implemented to integrate with the communication system
        # It will be called when shared or public memories are updated
        pass

    def _update_in_db(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update a memory entry in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Find the memory type
                for mem_type in MemoryType:
                    cursor.execute(f"""
                        SELECT id FROM {mem_type.value}_memory WHERE id = ?
                    """, (memory_id,))
                    if cursor.fetchone():
                        # Build update query
                        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
                        query = f"""
                            UPDATE {mem_type.value}_memory
                            SET {set_clause}, version = version + 1
                            WHERE id = ?
                        """
                        
                        # Execute update
                        cursor.execute(query, list(updates.values()) + [memory_id])
                        conn.commit()
                        return True
                
                return False
                
        except Exception as e:
            logger.error(f"Error updating memory in database: {e}")
            return False 