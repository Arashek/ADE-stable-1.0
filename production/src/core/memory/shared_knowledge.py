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
from .memory_manager import MemoryEntry, MemoryType, MemoryAccess

logger = logging.getLogger(__name__)

class KnowledgeDomain(Enum):
    TASK = "task"
    PROCEDURE = "procedure"
    PATTERN = "pattern"
    RULE = "rule"
    FACT = "fact"
    RELATIONSHIP = "relationship"

@dataclass
class KnowledgeEntry:
    """Represents a shared knowledge entry."""
    id: str = field(default_factory=lambda: str(uuid4()))
    domain: KnowledgeDomain
    content: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    created_by: str
    contributors: List[str] = field(default_factory=list)
    version: int = 1
    confidence: float = 0.5  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)

class SharedKnowledgeRepository:
    """Manages shared knowledge between agents."""
    
    def __init__(self, db_path: str = "shared_knowledge.db"):
        """Initialize the shared knowledge repository."""
        self.db_path = db_path
        self.lock = threading.Lock()
        self.conflict_resolution_lock = threading.Lock()
        
        # Initialize database
        self._init_db()
        
        # Start conflict resolution thread
        self.conflict_resolution_thread = threading.Thread(
            target=self._resolve_conflicts,
            daemon=True
        )
        self.conflict_resolution_thread.start()

    def _init_db(self) -> None:
        """Initialize the SQLite database for shared knowledge."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create main knowledge table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id TEXT PRIMARY KEY,
                    domain TEXT,
                    content TEXT,
                    created_at TIMESTAMP,
                    last_updated TIMESTAMP,
                    created_by TEXT,
                    contributors TEXT,
                    version INTEGER,
                    confidence REAL,
                    tags TEXT,
                    metadata TEXT,
                    conflicts TEXT
                )
            """)
            
            # Create indices for efficient retrieval
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_domain ON knowledge(domain)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags ON knowledge(tags)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_by ON knowledge(created_by)")
            
            conn.commit()

    def add_knowledge(self, entry: KnowledgeEntry) -> Optional[str]:
        """Add new knowledge to the repository."""
        try:
            with self.lock:
                # Check for conflicts
                conflicts = self._check_conflicts(entry)
                if conflicts:
                    entry.conflicts = conflicts
                
                # Store in database
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO knowledge (
                            id, domain, content, created_at, last_updated,
                            created_by, contributors, version, confidence,
                            tags, metadata, conflicts
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        entry.id,
                        entry.domain.value,
                        json.dumps(entry.content),
                        entry.created_at.isoformat(),
                        entry.last_updated.isoformat(),
                        entry.created_by,
                        json.dumps(entry.contributors),
                        entry.version,
                        entry.confidence,
                        json.dumps(entry.tags),
                        json.dumps(entry.metadata),
                        json.dumps(entry.conflicts)
                    ))
                    conn.commit()
                
                return entry.id
                
        except Exception as e:
            logger.error(f"Error adding knowledge: {e}")
            return None

    def update_knowledge(self, knowledge_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing knowledge."""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get current knowledge
                    cursor.execute("SELECT * FROM knowledge WHERE id = ?", (knowledge_id,))
                    row = cursor.fetchone()
                    if not row:
                        return False
                    
                    # Create updated entry
                    current = self._row_to_entry(row)
                    updated = KnowledgeEntry(**{**current.__dict__, **updates})
                    updated.version += 1
                    updated.last_updated = datetime.now()
                    
                    # Check for conflicts
                    conflicts = self._check_conflicts(updated)
                    if conflicts:
                        updated.conflicts = conflicts
                    
                    # Update database
                    cursor.execute("""
                        UPDATE knowledge SET
                            content = ?,
                            last_updated = ?,
                            contributors = ?,
                            version = ?,
                            confidence = ?,
                            tags = ?,
                            metadata = ?,
                            conflicts = ?
                        WHERE id = ?
                    """, (
                        json.dumps(updated.content),
                        updated.last_updated.isoformat(),
                        json.dumps(updated.contributors),
                        updated.version,
                        updated.confidence,
                        json.dumps(updated.tags),
                        json.dumps(updated.metadata),
                        json.dumps(updated.conflicts),
                        knowledge_id
                    ))
                    conn.commit()
                
                return True
                
        except Exception as e:
            logger.error(f"Error updating knowledge: {e}")
            return False

    def retrieve_knowledge(self, 
                          domain: Optional[KnowledgeDomain] = None,
                          tags: Optional[List[str]] = None,
                          created_by: Optional[str] = None,
                          confidence_threshold: float = 0.0,
                          limit: int = 10) -> List[KnowledgeEntry]:
        """Retrieve knowledge based on criteria."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query
                query_parts = []
                params = []
                
                if domain:
                    query_parts.append("domain = ?")
                    params.append(domain.value)
                
                if tags:
                    query_parts.append("tags LIKE ?")
                    params.append(f"%{json.dumps(tags)}%")
                
                if created_by:
                    query_parts.append("created_by = ?")
                    params.append(created_by)
                
                if confidence_threshold > 0:
                    query_parts.append("confidence >= ?")
                    params.append(confidence_threshold)
                
                query = f"""
                    SELECT * FROM knowledge
                    WHERE {' AND '.join(query_parts) if query_parts else '1=1'}
                    ORDER BY confidence DESC, last_updated DESC
                    LIMIT ?
                """
                params.append(limit)
                
                cursor.execute(query, params)
                return [self._row_to_entry(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error retrieving knowledge: {e}")
            return []

    def _check_conflicts(self, entry: KnowledgeEntry) -> List[Dict[str, Any]]:
        """Check for conflicts with existing knowledge."""
        conflicts = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Find potential conflicts based on domain and tags
                cursor.execute("""
                    SELECT * FROM knowledge
                    WHERE domain = ? AND tags LIKE ?
                """, (
                    entry.domain.value,
                    f"%{json.dumps(entry.tags)}%"
                ))
                
                for row in cursor.fetchall():
                    existing = self._row_to_entry(row)
                    
                    # Check for content conflicts
                    if self._has_content_conflict(entry, existing):
                        conflicts.append({
                            "id": existing.id,
                            "type": "content_conflict",
                            "details": {
                                "existing": existing.content,
                                "new": entry.content,
                                "confidence_diff": entry.confidence - existing.confidence
                            }
                        })
                    
                    # Check for version conflicts
                    if existing.version > entry.version:
                        conflicts.append({
                            "id": existing.id,
                            "type": "version_conflict",
                            "details": {
                                "existing_version": existing.version,
                                "new_version": entry.version
                            }
                        })
        
        except Exception as e:
            logger.error(f"Error checking conflicts: {e}")
        
        return conflicts

    def _has_content_conflict(self, entry1: KnowledgeEntry, entry2: KnowledgeEntry) -> bool:
        """Check if two knowledge entries have conflicting content."""
        # Implement domain-specific conflict detection
        if entry1.domain != entry2.domain:
            return False
        
        if entry1.domain == KnowledgeDomain.FACT:
            # For facts, check if they contradict each other
            return self._check_fact_conflict(entry1, entry2)
        elif entry1.domain == KnowledgeDomain.RULE:
            # For rules, check if they have conflicting conditions or actions
            return self._check_rule_conflict(entry1, entry2)
        elif entry1.domain == KnowledgeDomain.PROCEDURE:
            # For procedures, check if they have conflicting steps
            return self._check_procedure_conflict(entry1, entry2)
        
        return False

    def _check_fact_conflict(self, entry1: KnowledgeEntry, entry2: KnowledgeEntry) -> bool:
        """Check for conflicts between fact entries."""
        # Implement fact-specific conflict detection
        # This is a simplified example
        return (
            entry1.content.get("subject") == entry2.content.get("subject") and
            entry1.content.get("predicate") == entry2.content.get("predicate") and
            entry1.content.get("object") != entry2.content.get("object")
        )

    def _check_rule_conflict(self, entry1: KnowledgeEntry, entry2: KnowledgeEntry) -> bool:
        """Check for conflicts between rule entries."""
        # Implement rule-specific conflict detection
        # This is a simplified example
        return (
            entry1.content.get("conditions") == entry2.content.get("conditions") and
            entry1.content.get("actions") != entry2.content.get("actions")
        )

    def _check_procedure_conflict(self, entry1: KnowledgeEntry, entry2: KnowledgeEntry) -> bool:
        """Check for conflicts between procedure entries."""
        # Implement procedure-specific conflict detection
        # This is a simplified example
        return (
            entry1.content.get("name") == entry2.content.get("name") and
            entry1.content.get("steps") != entry2.content.get("steps")
        )

    def _resolve_conflicts(self) -> None:
        """Periodically resolve conflicts in the knowledge base."""
        while True:
            try:
                with self.conflict_resolution_lock:
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        
                        # Find entries with conflicts
                        cursor.execute("""
                            SELECT * FROM knowledge
                            WHERE conflicts != '[]'
                        """)
                        
                        for row in cursor.fetchall():
                            entry = self._row_to_entry(row)
                            
                            # Resolve conflicts
                            resolved = self._resolve_entry_conflicts(entry)
                            if resolved:
                                # Update entry
                                cursor.execute("""
                                    UPDATE knowledge SET
                                        conflicts = ?,
                                        last_updated = ?
                                    WHERE id = ?
                                """, (
                                    json.dumps([]),
                                    datetime.now().isoformat(),
                                    entry.id
                                ))
                        
                        conn.commit()
                
                # Sleep for resolution interval
                threading.Event().wait(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in conflict resolution: {e}")
                threading.Event().wait(60)  # Wait before retrying

    def _resolve_entry_conflicts(self, entry: KnowledgeEntry) -> bool:
        """Resolve conflicts for a specific entry."""
        try:
            for conflict in entry.conflicts:
                if conflict["type"] == "content_conflict":
                    # Resolve content conflicts based on confidence
                    if conflict["details"]["confidence_diff"] > 0:
                        # New content has higher confidence
                        return True
                    else:
                        # Existing content has higher confidence
                        return False
                
                elif conflict["type"] == "version_conflict":
                    # Resolve version conflicts by keeping the newer version
                    return entry.version > conflict["details"]["existing_version"]
            
            return True
            
        except Exception as e:
            logger.error(f"Error resolving entry conflicts: {e}")
            return False

    def _row_to_entry(self, row: tuple) -> KnowledgeEntry:
        """Convert a database row to a KnowledgeEntry."""
        return KnowledgeEntry(
            id=row[0],
            domain=KnowledgeDomain(row[1]),
            content=json.loads(row[2]),
            created_at=datetime.fromisoformat(row[3]),
            last_updated=datetime.fromisoformat(row[4]),
            created_by=row[5],
            contributors=json.loads(row[6]),
            version=row[7],
            confidence=row[8],
            tags=json.loads(row[9]),
            metadata=json.loads(row[10]),
            conflicts=json.loads(row[11])
        ) 