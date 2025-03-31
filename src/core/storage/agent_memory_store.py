from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import sqlite3
import aiosqlite
from pathlib import Path
import shutil

from ..api.agent_memory import (
    AgentMemory,
    MemoryEvent,
    MemoryAccessLevel,
    EventType
)

class AgentMemoryStore:
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure the database and tables exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_memory (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    access_level TEXT NOT NULL,
                    memory_data TEXT NOT NULL,
                    last_sync TEXT NOT NULL,
                    sync_frequency INTEGER NOT NULL,
                    is_active BOOLEAN NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_events (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    details TEXT NOT NULL,
                    affected_files TEXT NOT NULL,
                    priority INTEGER NOT NULL
                )
            """)

    async def save_agent_memory(self, memory: AgentMemory) -> bool:
        """Save agent memory to the database."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO agent_memory
                (id, agent_id, access_level, memory_data, last_sync,
                 sync_frequency, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id,
                memory.agent_id,
                memory.access_level.value,
                json.dumps(memory.memory_data),
                memory.last_sync.isoformat(),
                memory.sync_frequency,
                memory.is_active
            ))
            await db.commit()
            return True

    async def get_agent_memory(self, agent_id: str) -> Optional[AgentMemory]:
        """Retrieve agent memory by agent ID."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT * FROM agent_memory WHERE agent_id = ?
            """, (agent_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return AgentMemory(
                        id=row[0],
                        agent_id=row[1],
                        access_level=MemoryAccessLevel(row[2]),
                        memory_data=json.loads(row[3]),
                        last_sync=datetime.fromisoformat(row[4]),
                        sync_frequency=row[5],
                        is_active=bool(row[6])
                    )
                return None

    async def save_memory_event(self, event: MemoryEvent) -> bool:
        """Save a memory event to the database."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO memory_events
                (id, type, timestamp, agent_id, details, affected_files, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event.id,
                event.type.value,
                event.timestamp.isoformat(),
                event.agent_id,
                json.dumps(event.details),
                json.dumps(event.affected_files),
                event.priority
            ))
            await db.commit()
            return True

    async def get_agent_events(
        self,
        agent_id: str,
        limit: int = 50,
        event_type: Optional[EventType] = None
    ) -> List[MemoryEvent]:
        """Get events for a specific agent."""
        async with aiosqlite.connect(self.db_path) as db:
            query = "SELECT * FROM memory_events WHERE agent_id = ?"
            params = [agent_id]
            
            if event_type:
                query += " AND type = ?"
                params.append(event_type.value)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [
                    MemoryEvent(
                        id=row[0],
                        type=EventType(row[1]),
                        timestamp=datetime.fromisoformat(row[2]),
                        agent_id=row[3],
                        details=json.loads(row[4]),
                        affected_files=json.loads(row[5]),
                        priority=row[6]
                    )
                    for row in rows
                ]

    async def get_relevant_events(
        self,
        agent_id: str,
        file_path: str,
        time_range: Optional[Dict[str, datetime]] = None
    ) -> List[MemoryEvent]:
        """Get events relevant to a specific file."""
        async with aiosqlite.connect(self.db_path) as db:
            query = """
                SELECT * FROM memory_events
                WHERE agent_id = ?
                AND json_array_length(affected_files) > 0
                AND json_array_contains(affected_files, ?)
            """
            params = [agent_id, file_path]
            
            if time_range:
                query += " AND timestamp BETWEEN ? AND ?"
                params.extend([
                    time_range["start"].isoformat(),
                    time_range["end"].isoformat()
                ])
            
            query += " ORDER BY timestamp DESC"
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [
                    MemoryEvent(
                        id=row[0],
                        type=EventType(row[1]),
                        timestamp=datetime.fromisoformat(row[2]),
                        agent_id=row[3],
                        details=json.loads(row[4]),
                        affected_files=json.loads(row[5]),
                        priority=row[6]
                    )
                    for row in rows
                ]

    async def get_active_agents(self) -> List[str]:
        """Get list of agents with active memory."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT agent_id FROM agent_memory
                WHERE is_active = 1
            """) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def cleanup_old_events(
        self,
        max_age_days: int = 30
    ) -> int:
        """Clean up old memory events."""
        cutoff_date = datetime.now().replace(
            day=datetime.now().day - max_age_days
        )
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                DELETE FROM memory_events
                WHERE timestamp < ?
            """, (cutoff_date.isoformat(),))
            await db.commit()
            
            return db.total_changes

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