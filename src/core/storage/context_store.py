from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import sqlite3
import aiosqlite
from pathlib import Path
import shutil

from ..api.context_management import (
    ContextReference,
    ContextType,
    ContextSource,
    ContextInfluence
)

class ContextStore:
    def __init__(self, db_path: str = "context_store.db"):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure the database and tables exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_references (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    source_path TEXT,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    is_active BOOLEAN NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_influence (
                    reference_id TEXT PRIMARY KEY,
                    influence_score REAL NOT NULL,
                    usage_count INTEGER NOT NULL,
                    last_used TEXT NOT NULL,
                    relevance_factors TEXT NOT NULL,
                    FOREIGN KEY (reference_id) REFERENCES context_references(id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reference_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    influence_score REAL NOT NULL,
                    relevance_factors TEXT NOT NULL,
                    FOREIGN KEY (reference_id) REFERENCES context_references(id)
                )
            """)

    async def save_context_reference(self, context: ContextReference) -> bool:
        """Save a context reference to the database."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO context_references
                (id, type, title, content, source, source_path, metadata,
                 created_at, updated_at, priority, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                context.id,
                context.type.value,
                context.title,
                context.content,
                context.source.value,
                context.source_path,
                json.dumps(context.metadata),
                context.created_at.isoformat(),
                context.updated_at.isoformat(),
                context.priority,
                context.is_active
            ))
            await db.commit()
            return True

    async def get_context_reference(self, reference_id: str) -> Optional[ContextReference]:
        """Retrieve a context reference by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT * FROM context_references WHERE id = ?
            """, (reference_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return ContextReference(
                        id=row[0],
                        type=ContextType(row[1]),
                        title=row[2],
                        content=row[3],
                        source=ContextSource(row[4]),
                        source_path=row[5],
                        metadata=json.loads(row[6]),
                        created_at=datetime.fromisoformat(row[7]),
                        updated_at=datetime.fromisoformat(row[8]),
                        priority=row[9],
                        is_active=bool(row[10])
                    )
                return None

    async def get_context_references(
        self,
        active_only: bool = False
    ) -> List[ContextReference]:
        """Get all context references, optionally filtered by active status."""
        async with aiosqlite.connect(self.db_path) as db:
            query = "SELECT * FROM context_references"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY priority DESC, updated_at DESC"
            
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                return [
                    ContextReference(
                        id=row[0],
                        type=ContextType(row[1]),
                        title=row[2],
                        content=row[3],
                        source=ContextSource(row[4]),
                        source_path=row[5],
                        metadata=json.loads(row[6]),
                        created_at=datetime.fromisoformat(row[7]),
                        updated_at=datetime.fromisoformat(row[8]),
                        priority=row[9],
                        is_active=bool(row[10])
                    )
                    for row in rows
                ]

    async def delete_context_reference(self, reference_id: str) -> bool:
        """Delete a context reference and its associated data."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM context_influence WHERE reference_id = ?", (reference_id,))
            await db.execute("DELETE FROM context_history WHERE reference_id = ?", (reference_id,))
            await db.execute("DELETE FROM context_references WHERE id = ?", (reference_id,))
            await db.commit()
            return True

    async def save_context_influence(self, influence: ContextInfluence) -> bool:
        """Save context influence data."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO context_influence
                (reference_id, influence_score, usage_count, last_used, relevance_factors)
                VALUES (?, ?, ?, ?, ?)
            """, (
                influence.reference_id,
                influence.influence_score,
                influence.usage_count,
                influence.last_used.isoformat(),
                json.dumps(influence.relevance_factors)
            ))
            await db.commit()
            return True

    async def get_context_influence(
        self,
        reference_id: str
    ) -> Optional[ContextInfluence]:
        """Get influence data for a context reference."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT * FROM context_influence WHERE reference_id = ?
            """, (reference_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return ContextInfluence(
                        reference_id=row[0],
                        influence_score=row[1],
                        usage_count=row[2],
                        last_used=datetime.fromisoformat(row[3]),
                        relevance_factors=json.loads(row[4])
                    )
                return None

    async def get_context_history(
        self,
        reference_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get usage history for a context reference."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT * FROM context_history
                WHERE reference_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (reference_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "id": row[0],
                        "reference_id": row[1],
                        "timestamp": datetime.fromisoformat(row[2]),
                        "influence_score": row[3],
                        "relevance_factors": json.loads(row[4])
                    }
                    for row in rows
                ]

    async def search_context_references(
        self,
        query: str,
        type: Optional[ContextType] = None,
        source: Optional[ContextSource] = None
    ) -> List[ContextReference]:
        """Search for context references."""
        async with aiosqlite.connect(self.db_path) as db:
            conditions = ["title LIKE ? OR content LIKE ?"]
            params = [f"%{query}%", f"%{query}%"]
            
            if type:
                conditions.append("type = ?")
                params.append(type.value)
            
            if source:
                conditions.append("source = ?")
                params.append(source.value)
            
            query = f"""
                SELECT * FROM context_references
                WHERE {' AND '.join(conditions)}
                ORDER BY priority DESC, updated_at DESC
            """
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [
                    ContextReference(
                        id=row[0],
                        type=ContextType(row[1]),
                        title=row[2],
                        content=row[3],
                        source=ContextSource(row[4]),
                        source_path=row[5],
                        metadata=json.loads(row[6]),
                        created_at=datetime.fromisoformat(row[7]),
                        updated_at=datetime.fromisoformat(row[8]),
                        priority=row[9],
                        is_active=bool(row[10])
                    )
                    for row in rows
                ]

    async def get_context_suggestions(
        self,
        current_context: str,
        limit: int = 5
    ) -> List[ContextReference]:
        """Get suggested context references based on current context."""
        # This would typically use more sophisticated matching
        # For now, we'll return recently used active contexts
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT cr.* FROM context_references cr
                JOIN context_influence ci ON cr.id = ci.reference_id
                WHERE cr.is_active = 1
                ORDER BY ci.last_used DESC
                LIMIT ?
            """, (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [
                    ContextReference(
                        id=row[0],
                        type=ContextType(row[1]),
                        title=row[2],
                        content=row[3],
                        source=ContextSource(row[4]),
                        source_path=row[5],
                        metadata=json.loads(row[6]),
                        created_at=datetime.fromisoformat(row[7]),
                        updated_at=datetime.fromisoformat(row[8]),
                        priority=row[9],
                        is_active=bool(row[10])
                    )
                    for row in rows
                ]

    async def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Error backing up database: {e}")
            return False

    async def restore_database(self, backup_path: str) -> bool:
        """Restore the database from a backup."""
        try:
            shutil.copy2(backup_path, self.db_path)
            return True
        except Exception as e:
            print(f"Error restoring database: {e}")
            return False 