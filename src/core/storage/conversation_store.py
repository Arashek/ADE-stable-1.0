from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
import sqlite3
import asyncio
from pathlib import Path
from ..api.agent_communication import Message, MessageType

@dataclass
class Conversation:
    id: str
    title: str
    created_at: datetime
    last_updated: datetime
    participants: List[str]
    tags: List[str]
    is_archived: bool = False
    is_bookmarked: bool = False

class ConversationStore:
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                last_updated TIMESTAMP NOT NULL,
                participants TEXT NOT NULL,
                tags TEXT NOT NULL,
                is_archived BOOLEAN DEFAULT 0,
                is_bookmarked BOOLEAN DEFAULT 0
            )
        """)

        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                content TEXT NOT NULL,
                type TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                thread_id TEXT,
                reactions TEXT,
                votes TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        """)

        # Create bookmarks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                note TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id),
                FOREIGN KEY (message_id) REFERENCES messages (id)
            )
        """)

        conn.commit()
        conn.close()

    async def create_conversation(self, conversation: Conversation) -> None:
        """Create a new conversation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO conversations (
                id, title, created_at, last_updated,
                participants, tags, is_archived, is_bookmarked
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            conversation.id,
            conversation.title,
            conversation.created_at.isoformat(),
            conversation.last_updated.isoformat(),
            json.dumps(conversation.participants),
            json.dumps(conversation.tags),
            conversation.is_archived,
            conversation.is_bookmarked
        ))

        conn.commit()
        conn.close()

    async def add_message(self, conversation_id: str, message: Message) -> None:
        """Add a message to a conversation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages (
                id, conversation_id, agent_id, content,
                type, timestamp, thread_id, reactions, votes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            message.id,
            conversation_id,
            message.agent_id,
            json.dumps(message.content),
            message.type.value,
            message.timestamp.isoformat(),
            message.thread_id,
            json.dumps(message.reactions) if message.reactions else None,
            json.dumps(message.votes) if message.votes else None
        ))

        # Update conversation last_updated
        cursor.execute("""
            UPDATE conversations
            SET last_updated = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), conversation_id))

        conn.commit()
        conn.close()

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM conversations WHERE id = ?
        """, (conversation_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return Conversation(
                id=row[0],
                title=row[1],
                created_at=datetime.fromisoformat(row[2]),
                last_updated=datetime.fromisoformat(row[3]),
                participants=json.loads(row[4]),
                tags=json.loads(row[5]),
                is_archived=bool(row[6]),
                is_bookmarked=bool(row[7])
            )
        return None

    async def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Message]:
        """Retrieve messages from a conversation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """, (conversation_id, limit, offset))

        messages = []
        for row in cursor.fetchall():
            messages.append(Message(
                id=row[0],
                agent_id=row[2],
                content=json.loads(row[3]),
                type=MessageType(row[4]),
                timestamp=datetime.fromisoformat(row[5]),
                thread_id=row[6],
                reactions=json.loads(row[7]) if row[7] else None,
                votes=json.loads(row[8]) if row[8] else None
            ))

        conn.close()
        return messages

    async def search_conversations(
        self,
        query: str,
        tags: Optional[List[str]] = None
    ) -> List[Conversation]:
        """Search conversations by title and tags."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        conditions = ["title LIKE ?"]
        params = [f"%{query}%"]

        if tags:
            conditions.append("tags LIKE ?")
            params.append(f"%{json.dumps(tags)}%")

        query = f"""
            SELECT * FROM conversations
            WHERE {' AND '.join(conditions)}
            ORDER BY last_updated DESC
        """

        cursor.execute(query, params)
        conversations = []

        for row in cursor.fetchall():
            conversations.append(Conversation(
                id=row[0],
                title=row[1],
                created_at=datetime.fromisoformat(row[2]),
                last_updated=datetime.fromisoformat(row[3]),
                participants=json.loads(row[4]),
                tags=json.loads(row[5]),
                is_archived=bool(row[6]),
                is_bookmarked=bool(row[7])
            ))

        conn.close()
        return conversations

    async def add_bookmark(
        self,
        conversation_id: str,
        message_id: str,
        note: Optional[str] = None
    ) -> None:
        """Add a bookmark to a message."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bookmarks (
                id, conversation_id, message_id, created_at, note
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            f"bookmark_{datetime.now().timestamp()}",
            conversation_id,
            message_id,
            datetime.now().isoformat(),
            note
        ))

        conn.commit()
        conn.close()

    async def get_bookmarks(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Retrieve bookmarks for a conversation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT b.*, m.content, m.timestamp
            FROM bookmarks b
            JOIN messages m ON b.message_id = m.id
            WHERE b.conversation_id = ?
            ORDER BY b.created_at DESC
        """, (conversation_id,))

        bookmarks = []
        for row in cursor.fetchall():
            bookmarks.append({
                "id": row[0],
                "message_id": row[2],
                "created_at": datetime.fromisoformat(row[3]),
                "note": row[4],
                "message_content": json.loads(row[5]),
                "message_timestamp": datetime.fromisoformat(row[6])
            })

        conn.close()
        return bookmarks

    async def archive_conversation(self, conversation_id: str) -> None:
        """Archive a conversation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE conversations
            SET is_archived = 1
            WHERE id = ?
        """, (conversation_id,))

        conn.commit()
        conn.close()

    async def export_conversation(self, conversation_id: str) -> str:
        """Export a conversation as JSON."""
        conversation = await self.get_conversation(conversation_id)
        messages = await self.get_conversation_messages(conversation_id)
        bookmarks = await self.get_bookmarks(conversation_id)

        export_data = {
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "last_updated": conversation.last_updated.isoformat(),
                "participants": conversation.participants,
                "tags": conversation.tags,
                "is_archived": conversation.is_archived,
                "is_bookmarked": conversation.is_bookmarked
            },
            "messages": [
                {
                    "id": msg.id,
                    "agent_id": msg.agent_id,
                    "content": msg.content,
                    "type": msg.type.value,
                    "timestamp": msg.timestamp.isoformat(),
                    "thread_id": msg.thread_id,
                    "reactions": msg.reactions,
                    "votes": msg.votes
                }
                for msg in messages
            ],
            "bookmarks": bookmarks
        }

        return json.dumps(export_data, default=str)

    async def cleanup_old_conversations(self, days: int = 30) -> None:
        """Remove old archived conversations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute("""
            DELETE FROM conversations
            WHERE is_archived = 1
            AND last_updated < ?
        """, (cutoff_date,))

        conn.commit()
        conn.close() 