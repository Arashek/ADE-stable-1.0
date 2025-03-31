from datetime import datetime
import json
import uuid
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
from pathlib import Path
import sqlite3
from dataclasses import dataclass, asdict
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
import os
from ..security.privacy_engine import PrivacyEngine, PrivacyConfig
from ..security.encryption_engine import EncryptionEngine, EncryptionConfig
from ..security.backup_engine import BackupEngine, BackupConfig
import numpy as np
from sentence_transformers import SentenceTransformer
from fuzzywuzzy import fuzz
import re
import secrets
import hashlib
import gzip
import shutil
import tarfile

@dataclass
class ConversationMetadata:
    conversation_id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    is_archived: bool
    is_deleted: bool
    privacy_level: str
    encryption_enabled: bool
    backup_enabled: bool

@dataclass
class Message:
    message_id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime
    metadata: Dict
    is_encrypted: bool
    is_anonymized: bool

class UserConversationStore:
    def __init__(
        self,
        db_path: str,
        privacy_config: Optional[PrivacyConfig] = None,
        encryption_config: Optional[EncryptionConfig] = None,
        backup_config: Optional[BackupConfig] = None
    ):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize engines
        self.privacy_engine = PrivacyEngine(privacy_config)
        self.encryption_engine = EncryptionEngine(encryption_config)
        self.backup_engine = BackupEngine(backup_config)
        
        # Initialize search capabilities
        self._init_search_capabilities()
        
        # Initialize database
        self._init_database()
        
        # Initialize thread safety
        self._lock = threading.Lock()

    def _init_search_capabilities(self):
        """Initialize search capabilities."""
        # Initialize sentence transformer for semantic search
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize search index
        self._init_search_index()

    def _init_search_index(self):
        """Initialize the search index table."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create search index table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_index (
                    conversation_id TEXT NOT NULL,
                    message_id TEXT NOT NULL,
                    content_embedding BLOB NOT NULL,
                    content_text TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    PRIMARY KEY (conversation_id, message_id),
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
                    FOREIGN KEY (message_id) REFERENCES messages(message_id)
                )
            """)
            
            # Create index for faster search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_search_created_at
                ON search_index(created_at)
            """)
            
            conn.commit()

    def _update_search_index(self, message: Message):
        """Update the search index with a new message."""
        # Generate embedding for the message content
        embedding = self.sentence_transformer.encode(message.content)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO search_index (
                    conversation_id, message_id, content_embedding,
                    content_text, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                message.conversation_id,
                message.message_id,
                embedding.tobytes(),
                message.content,
                message.created_at.isoformat()
            ))
            conn.commit()

    def semantic_search(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Tuple[Message, float]]:
        """Perform semantic search across messages."""
        # Generate query embedding
        query_embedding = self.sentence_transformer.encode(query)
        
        # Search in database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT si.*, m.*
                FROM search_index si
                JOIN messages m ON si.message_id = m.message_id
                JOIN conversations c ON si.conversation_id = c.conversation_id
                WHERE c.user_id = ?
                ORDER BY si.created_at DESC
                LIMIT ?
            """, (user_id, limit * 2))  # Get more results for filtering
            
            results = []
            for row in cursor.fetchall():
                # Convert embedding bytes back to numpy array
                message_embedding = np.frombuffer(row[2], dtype=np.float32)
                
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, message_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(message_embedding)
                )
                
                if similarity >= threshold:
                    message = Message(
                        message_id=row[1],
                        conversation_id=row[0],
                        role=row[8],
                        content=row[3],
                        created_at=datetime.fromisoformat(row[4]),
                        metadata=json.loads(row[6]),
                        is_encrypted=bool(row[7]),
                        is_anonymized=bool(row[8])
                    )
                    results.append((message, float(similarity)))
            
            # Sort by similarity and limit results
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]

    def fuzzy_search(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
        threshold: int = 80
    ) -> List[Tuple[Message, int]]:
        """Perform fuzzy search across messages."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.*
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.conversation_id
                WHERE c.user_id = ?
                ORDER BY m.created_at DESC
                LIMIT ?
            """, (user_id, limit * 2))
            
            results = []
            for row in cursor.fetchall():
                message = Message(
                    message_id=row[0],
                    conversation_id=row[1],
                    role=row[2],
                    content=row[3],
                    created_at=datetime.fromisoformat(row[4]),
                    metadata=json.loads(row[5]),
                    is_encrypted=bool(row[6]),
                    is_anonymized=bool(row[7])
                )
                
                # Calculate fuzzy match ratio
                ratio = fuzz.ratio(query.lower(), message.content.lower())
                if ratio >= threshold:
                    results.append((message, ratio))
            
            # Sort by match ratio and limit results
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]

    def hybrid_search(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
        semantic_threshold: float = 0.7,
        fuzzy_threshold: int = 80,
        semantic_weight: float = 0.7
    ) -> List[Tuple[Message, float]]:
        """Perform hybrid search combining semantic and fuzzy matching."""
        # Get semantic search results
        semantic_results = self.semantic_search(
            query, user_id, limit, semantic_threshold
        )
        
        # Get fuzzy search results
        fuzzy_results = self.fuzzy_search(
            query, user_id, limit, fuzzy_threshold
        )
        
        # Combine results
        combined_results = {}
        
        # Add semantic results
        for message, score in semantic_results:
            combined_results[message.message_id] = (message, score * semantic_weight)
        
        # Add fuzzy results
        for message, score in fuzzy_results:
            if message.message_id in combined_results:
                # Update score if fuzzy match is better
                fuzzy_weight = 1 - semantic_weight
                current_score = combined_results[message.message_id][1]
                new_score = max(current_score, score * fuzzy_weight)
                combined_results[message.message_id] = (message, new_score)
            else:
                combined_results[message.message_id] = (
                    message,
                    score * (1 - semantic_weight)
                )
        
        # Sort by combined score and limit results
        results = list(combined_results.values())
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def _init_database(self):
        """Initialize the SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    tags TEXT NOT NULL,
                    is_archived BOOLEAN NOT NULL DEFAULT 0,
                    is_deleted BOOLEAN NOT NULL DEFAULT 0,
                    privacy_level TEXT NOT NULL,
                    encryption_enabled BOOLEAN NOT NULL DEFAULT 1,
                    backup_enabled BOOLEAN NOT NULL DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    metadata TEXT NOT NULL,
                    is_encrypted BOOLEAN NOT NULL DEFAULT 1,
                    is_anonymized BOOLEAN NOT NULL DEFAULT 1,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """)
            
            # Create backup schedules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backup_schedules (
                    schedule_id TEXT PRIMARY KEY,
                    schedule_type TEXT NOT NULL,
                    schedule_params TEXT NOT NULL,
                    backup_dir TEXT NOT NULL,
                    compression BOOLEAN NOT NULL DEFAULT 1,
                    deduplication BOOLEAN NOT NULL DEFAULT 1,
                    encryption_key TEXT,
                    cloud_storage TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            # Create cloud storage connections table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cloud_storage_connections (
                    connection_id TEXT PRIMARY KEY,
                    storage_type TEXT NOT NULL,
                    credentials TEXT NOT NULL,
                    options TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user_id
                ON conversations(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
                ON messages(conversation_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_created_at
                ON conversations(created_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_created_at
                ON messages(created_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_backup_schedules_type
                ON backup_schedules(schedule_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cloud_storage_type
                ON cloud_storage_connections(storage_type)
            """)
            
            conn.commit()

    def create_conversation(
        self,
        user_id: str,
        title: str,
        tags: List[str] = None,
        privacy_level: str = "medium",
        encryption_enabled: bool = True,
        backup_enabled: bool = True
    ) -> ConversationMetadata:
        """Create a new conversation."""
        with self._lock:
            conversation_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            metadata = ConversationMetadata(
                conversation_id=conversation_id,
                user_id=user_id,
                title=title,
                created_at=now,
                updated_at=now,
                tags=tags or [],
                is_archived=False,
                is_deleted=False,
                privacy_level=privacy_level,
                encryption_enabled=encryption_enabled,
                backup_enabled=backup_enabled
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversations (
                        conversation_id, user_id, title, created_at,
                        updated_at, tags, privacy_level,
                        encryption_enabled, backup_enabled
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metadata.conversation_id,
                    metadata.user_id,
                    metadata.title,
                    metadata.created_at.isoformat(),
                    metadata.updated_at.isoformat(),
                    json.dumps(metadata.tags),
                    metadata.privacy_level,
                    metadata.encryption_enabled,
                    metadata.backup_enabled
                ))
                conn.commit()
            
            return metadata

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Dict = None,
        encrypt: bool = True,
        anonymize: bool = True
    ) -> Message:
        """Add a message to a conversation."""
        with self._lock:
            # Get conversation metadata
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation not found: {conversation_id}")
            
            # Process content based on privacy settings
            if anonymize and conversation.privacy_level != "none":
                content = self.privacy_engine.anonymize_text(content)
            
            # Encrypt content if enabled
            if encrypt and conversation.encryption_enabled:
                encrypted_content, encryption_metadata = self.encryption_engine.encrypt_data(
                    content,
                    self._get_conversation_key(conversation_id)
                )
                content = encrypted_content.hex()
                if metadata is None:
                    metadata = {}
                metadata["encryption"] = encryption_metadata
            
            # Create message
            message_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            message = Message(
                message_id=message_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
                created_at=now,
                metadata=metadata or {},
                is_encrypted=encrypt and conversation.encryption_enabled,
                is_anonymized=anonymize and conversation.privacy_level != "none"
            )
            
            # Store message
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO messages (
                        message_id, conversation_id, role, content,
                        created_at, metadata, is_encrypted, is_anonymized
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.message_id,
                    message.conversation_id,
                    message.role,
                    message.content,
                    message.created_at.isoformat(),
                    json.dumps(message.metadata),
                    message.is_encrypted,
                    message.is_anonymized
                ))
                
                # Update conversation timestamp
                cursor.execute("""
                    UPDATE conversations
                    SET updated_at = ?
                    WHERE conversation_id = ?
                """, (now.isoformat(), conversation_id))
                
                conn.commit()
            
            # Trigger backup if enabled
            if conversation.backup_enabled:
                self._trigger_backup(conversation_id)
            
            # Update search index
            self._update_search_index(message)
            
            return message

    def get_conversation(
        self,
        conversation_id: str
    ) -> Optional[ConversationMetadata]:
        """Get conversation metadata."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM conversations
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return ConversationMetadata(
                conversation_id=row[0],
                user_id=row[1],
                title=row[2],
                created_at=datetime.fromisoformat(row[3]),
                updated_at=datetime.fromisoformat(row[4]),
                tags=json.loads(row[5]),
                is_archived=bool(row[6]),
                is_deleted=bool(row[7]),
                privacy_level=row[8],
                encryption_enabled=bool(row[9]),
                backup_enabled=bool(row[10])
            )

    def get_messages(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Message]:
        """Get messages from a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
                LIMIT ? OFFSET ?
            """, (conversation_id, limit, offset))
            
            messages = []
            for row in cursor.fetchall():
                # Decrypt content if needed
                content = row[3]
                if conversation.encryption_enabled and row[7]:
                    content = self.encryption_engine.decrypt_data(
                        bytes.fromhex(content),
                        self._get_conversation_key(conversation_id)
                    )
                
                messages.append(Message(
                    message_id=row[0],
                    conversation_id=row[1],
                    role=row[2],
                    content=content,
                    created_at=datetime.fromisoformat(row[4]),
                    metadata=json.loads(row[5]),
                    is_encrypted=bool(row[6]),
                    is_anonymized=bool(row[7])
                ))
            
            return messages

    def search_conversations(
        self,
        user_id: str,
        query: str,
        tags: List[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[ConversationMetadata]:
        """Search conversations."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build query
            sql = """
                SELECT * FROM conversations
                WHERE user_id = ?
                AND is_deleted = 0
            """
            params = [user_id]
            
            if query:
                sql += " AND title LIKE ?"
                params.append(f"%{query}%")
            
            if tags:
                sql += " AND tags LIKE ?"
                params.append(f"%{json.dumps(tags)}%")
            
            sql += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(sql, params)
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append(ConversationMetadata(
                    conversation_id=row[0],
                    user_id=row[1],
                    title=row[2],
                    created_at=datetime.fromisoformat(row[3]),
                    updated_at=datetime.fromisoformat(row[4]),
                    tags=json.loads(row[5]),
                    is_archived=bool(row[6]),
                    is_deleted=bool(row[7]),
                    privacy_level=row[8],
                    encryption_enabled=bool(row[9]),
                    backup_enabled=bool(row[10])
                ))
            
            return conversations

    def update_conversation(
        self,
        conversation_id: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        privacy_level: Optional[str] = None,
        encryption_enabled: Optional[bool] = None,
        backup_enabled: Optional[bool] = None,
        is_archived: Optional[bool] = None
    ) -> ConversationMetadata:
        """Update conversation metadata."""
        with self._lock:
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation not found: {conversation_id}")
            
            # Update fields
            if title is not None:
                conversation.title = title
            if tags is not None:
                conversation.tags = tags
            if privacy_level is not None:
                conversation.privacy_level = privacy_level
            if encryption_enabled is not None:
                conversation.encryption_enabled = encryption_enabled
            if backup_enabled is not None:
                conversation.backup_enabled = backup_enabled
            if is_archived is not None:
                conversation.is_archived = is_archived
            
            conversation.updated_at = datetime.utcnow()
            
            # Update database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE conversations
                    SET title = ?, tags = ?, privacy_level = ?,
                        encryption_enabled = ?, backup_enabled = ?,
                        is_archived = ?, updated_at = ?
                    WHERE conversation_id = ?
                """, (
                    conversation.title,
                    json.dumps(conversation.tags),
                    conversation.privacy_level,
                    conversation.encryption_enabled,
                    conversation.backup_enabled,
                    conversation.is_archived,
                    conversation.updated_at.isoformat(),
                    conversation.conversation_id
                ))
                conn.commit()
            
            return conversation

    def delete_conversation(
        self,
        conversation_id: str,
        permanent: bool = False
    ) -> bool:
        """Delete a conversation."""
        with self._lock:
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation not found: {conversation_id}")
            
            if permanent:
                # Permanently delete conversation and messages
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        DELETE FROM messages
                        WHERE conversation_id = ?
                    """, (conversation_id,))
                    cursor.execute("""
                        DELETE FROM conversations
                        WHERE conversation_id = ?
                    """, (conversation_id,))
                    conn.commit()
            else:
                # Soft delete conversation
                conversation.is_deleted = True
                conversation.updated_at = datetime.utcnow()
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE conversations
                        SET is_deleted = 1, updated_at = ?
                        WHERE conversation_id = ?
                    """, (
                        conversation.updated_at.isoformat(),
                        conversation_id
                    ))
                    conn.commit()
            
            return True

    def get_conversation_stats(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get conversation statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build query
            sql = """
                SELECT COUNT(*) as total_conversations,
                       COUNT(CASE WHEN is_archived = 1 THEN 1 END) as archived_conversations,
                       COUNT(CASE WHEN is_deleted = 1 THEN 1 END) as deleted_conversations,
                       COUNT(DISTINCT m.conversation_id) as conversations_with_messages,
                       COUNT(m.message_id) as total_messages
                FROM conversations c
                LEFT JOIN messages m ON c.conversation_id = m.conversation_id
                WHERE c.user_id = ?
            """
            params = [user_id]
            
            if start_date:
                sql += " AND c.created_at >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                sql += " AND c.created_at <= ?"
                params.append(end_date.isoformat())
            
            cursor.execute(sql, params)
            row = cursor.fetchone()
            
            return {
                "total_conversations": row[0],
                "archived_conversations": row[1],
                "deleted_conversations": row[2],
                "conversations_with_messages": row[3],
                "total_messages": row[4]
            }

    def _get_conversation_key(self, conversation_id: str) -> bytes:
        """Get encryption key for a conversation."""
        # Implementation would derive a key based on conversation_id and user_id
        # This is a placeholder - actual implementation would use proper key derivation
        return os.urandom(32)

    def _trigger_backup(self, conversation_id: str):
        """Trigger a backup for a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation or not conversation.backup_enabled:
            return
        
        # Get conversation data
        messages = self.get_messages(conversation_id)
        conversation_data = {
            "conversation": conversation.__dict__,
            "messages": [m.__dict__ for m in messages]
        }
        
        # Create backup
        self.backup_engine.create_backup(
            source_path=conversation_id,
            backup_type="incremental",
            metadata={
                "conversation_id": conversation_id,
                "user_id": conversation.user_id,
                "message_count": len(messages),
                "backup_timestamp": datetime.utcnow().isoformat()
            }
        )

    def validate_store_config(self) -> Tuple[bool, List[str]]:
        """Validate the store configuration."""
        issues = []
        
        # Validate database path
        if not os.path.exists(os.path.dirname(self.db_path)):
            try:
                os.makedirs(os.path.dirname(self.db_path))
            except Exception as e:
                issues.append(f"Failed to create database directory: {e}")
        
        # Validate privacy configuration
        privacy_valid, privacy_issues = self.privacy_engine.validate_privacy_config()
        if not privacy_valid:
            issues.extend(privacy_issues)
        
        # Validate encryption configuration
        encryption_valid, encryption_issues = self.encryption_engine.validate_encryption_config()
        if not encryption_valid:
            issues.extend(encryption_issues)
        
        # Validate backup configuration
        backup_valid, backup_issues = self.backup_engine.validate_backup_config()
        if not backup_valid:
            issues.extend(backup_issues)
        
        return len(issues) == 0, issues

    def export_conversation(
        self,
        conversation_id: str,
        format: str = "json",
        include_metadata: bool = True,
        include_embeddings: bool = False,
        encryption_key: Optional[bytes] = None
    ) -> Union[str, bytes]:
        """Export a conversation to a specified format."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")
        
        # Get all messages
        messages = self.get_messages(conversation_id)
        
        # Prepare export data
        export_data = {
            "version": "1.0",
            "exported_at": datetime.utcnow().isoformat(),
            "conversation": asdict(conversation),
            "messages": [asdict(m) for m in messages]
        }
        
        # Add search embeddings if requested
        if include_embeddings:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT content_embedding
                    FROM search_index
                    WHERE conversation_id = ?
                """, (conversation_id,))
                
                embeddings = []
                for row in cursor.fetchall():
                    embeddings.append(row[0])
                
                export_data["embeddings"] = embeddings
        
        # Convert to requested format
        if format == "json":
            export_str = json.dumps(export_data, indent=2)
            if encryption_key:
                return self.encryption_engine.encrypt_data(
                    export_str.encode(),
                    encryption_key
                )[0]
            return export_str
        
        elif format == "markdown":
            markdown = []
            
            # Add conversation metadata
            if include_metadata:
                markdown.append(f"# {conversation.title}")
                markdown.append(f"Created: {conversation.created_at}")
                markdown.append(f"Updated: {conversation.updated_at}")
                if conversation.tags:
                    markdown.append(f"Tags: {', '.join(conversation.tags)}")
                markdown.append("")
            
            # Add messages
            for message in messages:
                markdown.append(f"## {message.role.title()}")
                markdown.append(message.content)
                markdown.append("")
            
            export_str = "\n".join(markdown)
            if encryption_key:
                return self.encryption_engine.encrypt_data(
                    export_str.encode(),
                    encryption_key
                )[0]
            return export_str
        
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def import_conversation(
        self,
        import_data: Union[str, bytes],
        format: str = "json",
        encryption_key: Optional[bytes] = None,
        user_id: Optional[str] = None,
        privacy_level: Optional[str] = None,
        encryption_enabled: Optional[bool] = None,
        backup_enabled: Optional[bool] = None
    ) -> ConversationMetadata:
        """Import a conversation from a specified format."""
        # Decrypt if needed
        if encryption_key:
            import_data = self.encryption_engine.decrypt_data(
                import_data,
                encryption_key
            )
        
        # Parse import data
        if format == "json":
            if isinstance(import_data, bytes):
                import_data = import_data.decode()
            data = json.loads(import_data)
            
            # Validate version
            if data.get("version") != "1.0":
                raise ValueError("Unsupported import version")
            
            # Get conversation data
            conv_data = data["conversation"]
            
            # Override user_id if provided
            if user_id:
                conv_data["user_id"] = user_id
            
            # Override privacy settings if provided
            if privacy_level:
                conv_data["privacy_level"] = privacy_level
            if encryption_enabled is not None:
                conv_data["encryption_enabled"] = encryption_enabled
            if backup_enabled is not None:
                conv_data["backup_enabled"] = backup_enabled
            
            # Create conversation
            conversation = self.create_conversation(**conv_data)
            
            # Import messages
            for msg_data in data["messages"]:
                self.add_message(
                    conversation_id=conversation.conversation_id,
                    role=msg_data["role"],
                    content=msg_data["content"],
                    metadata=msg_data.get("metadata", {}),
                    encrypt=conversation.encryption_enabled,
                    anonymize=conversation.privacy_level != "none"
                )
            
            # Import embeddings if available
            if "embeddings" in data:
                self._import_embeddings(
                    conversation.conversation_id,
                    data["embeddings"]
                )
            
            return conversation
        
        elif format == "markdown":
            if isinstance(import_data, bytes):
                import_data = import_data.decode()
            
            # Parse markdown
            lines = import_data.split("\n")
            title = lines[0].lstrip("# ").strip()
            
            # Extract metadata
            metadata = {}
            i = 1
            while i < len(lines) and lines[i].startswith(("Created:", "Updated:", "Tags:")):
                line = lines[i].strip()
                if line.startswith("Created:"):
                    metadata["created_at"] = datetime.fromisoformat(
                        line.replace("Created:", "").strip()
                    )
                elif line.startswith("Updated:"):
                    metadata["updated_at"] = datetime.fromisoformat(
                        line.replace("Updated:", "").strip()
                    )
                elif line.startswith("Tags:"):
                    metadata["tags"] = [
                        tag.strip()
                        for tag in line.replace("Tags:", "").strip().split(",")
                    ]
                i += 1
            
            # Create conversation
            conv_data = {
                "user_id": user_id,
                "title": title,
                "tags": metadata.get("tags", []),
                "privacy_level": privacy_level or "medium",
                "encryption_enabled": encryption_enabled if encryption_enabled is not None else True,
                "backup_enabled": backup_enabled if backup_enabled is not None else True
            }
            
            conversation = self.create_conversation(**conv_data)
            
            # Import messages
            current_role = None
            current_content = []
            
            while i < len(lines):
                line = lines[i].strip()
                
                if line.startswith("## "):
                    # Save previous message if exists
                    if current_role and current_content:
                        self.add_message(
                            conversation_id=conversation.conversation_id,
                            role=current_role,
                            content="\n".join(current_content),
                            encrypt=conversation.encryption_enabled,
                            anonymize=conversation.privacy_level != "none"
                        )
                    
                    # Start new message
                    current_role = line.replace("## ", "").lower()
                    current_content = []
                
                elif line and not line.startswith("#"):
                    current_content.append(line)
                
                i += 1
            
            # Save last message
            if current_role and current_content:
                self.add_message(
                    conversation_id=conversation.conversation_id,
                    role=current_role,
                    content="\n".join(current_content),
                    encrypt=conversation.encryption_enabled,
                    anonymize=conversation.privacy_level != "none"
                )
            
            return conversation
        
        else:
            raise ValueError(f"Unsupported import format: {format}")

    def _import_embeddings(self, conversation_id: str, embeddings: List[bytes]):
        """Import search embeddings for a conversation."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get message IDs in order
            cursor.execute("""
                SELECT message_id
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
            """, (conversation_id,))
            
            message_ids = [row[0] for row in cursor.fetchall()]
            
            # Insert embeddings
            for msg_id, embedding in zip(message_ids, embeddings):
                cursor.execute("""
                    INSERT OR REPLACE INTO search_index (
                        conversation_id, message_id, content_embedding,
                        content_text, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    conversation_id,
                    msg_id,
                    embedding,
                    "",  # Content text is not needed for embeddings
                    datetime.utcnow().isoformat()
                ))
            
            conn.commit()

    def share_conversation(
        self,
        conversation_id: str,
        user_id: str,
        access_level: str = "read",
        expires_at: Optional[datetime] = None,
        encryption_key: Optional[bytes] = None
    ) -> str:
        """Share a conversation with another user."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")
        
        # Validate access level
        if access_level not in ["read", "write", "admin"]:
            raise ValueError(f"Invalid access level: {access_level}")
        
        # Generate share token
        share_token = secrets.token_urlsafe(32)
        
        # Store share information
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversation_shares (
                    conversation_id, user_id, share_token,
                    access_level, expires_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                conversation_id,
                user_id,
                share_token,
                access_level,
                expires_at.isoformat() if expires_at else None,
                datetime.utcnow().isoformat()
            ))
            conn.commit()
        
        # If encryption key is provided, encrypt the share token
        if encryption_key:
            share_token = self.encryption_engine.encrypt_data(
                share_token.encode(),
                encryption_key
            )[0].decode()
        
        return share_token

    def get_shared_conversations(
        self,
        user_id: str,
        access_level: Optional[str] = None
    ) -> List[ConversationMetadata]:
        """Get conversations shared with a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT c.*
                FROM conversations c
                JOIN conversation_shares s ON c.conversation_id = s.conversation_id
                WHERE s.user_id = ?
            """
            params = [user_id]
            
            if access_level:
                query += " AND s.access_level = ?"
                params.append(access_level)
            
            query += " AND (s.expires_at IS NULL OR s.expires_at > ?)"
            params.append(datetime.utcnow().isoformat())
            
            cursor.execute(query, params)
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append(ConversationMetadata(*row))
            
            return conversations

    def revoke_share(
        self,
        conversation_id: str,
        user_id: str
    ) -> bool:
        """Revoke a user's access to a shared conversation."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM conversation_shares
                WHERE conversation_id = ? AND user_id = ?
            """, (conversation_id, user_id))
            conn.commit()
            
            return cursor.rowcount > 0

    def update_share_access(
        self,
        conversation_id: str,
        user_id: str,
        access_level: str
    ) -> bool:
        """Update a user's access level for a shared conversation."""
        if access_level not in ["read", "write", "admin"]:
            raise ValueError(f"Invalid access level: {access_level}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE conversation_shares
                SET access_level = ?
                WHERE conversation_id = ? AND user_id = ?
            """, (access_level, conversation_id, user_id))
            conn.commit()
            
            return cursor.rowcount > 0

    def add_collaborator(
        self,
        conversation_id: str,
        user_id: str,
        role: str = "collaborator",
        permissions: Optional[List[str]] = None
    ) -> bool:
        """Add a collaborator to a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")
        
        # Validate role
        if role not in ["collaborator", "reviewer", "editor"]:
            raise ValueError(f"Invalid role: {role}")
        
        # Set default permissions based on role
        if permissions is None:
            permissions = {
                "collaborator": ["read", "write", "comment"],
                "reviewer": ["read", "comment"],
                "editor": ["read", "write", "comment", "edit"]
            }[role]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversation_collaborators (
                    conversation_id, user_id, role,
                    permissions, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                conversation_id,
                user_id,
                role,
                json.dumps(permissions),
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            
            return cursor.rowcount > 0

    def get_collaborators(
        self,
        conversation_id: str
    ) -> List[Dict[str, Any]]:
        """Get all collaborators for a conversation."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, role, permissions
                FROM conversation_collaborators
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            collaborators = []
            for row in cursor.fetchall():
                collaborators.append({
                    "user_id": row[0],
                    "role": row[1],
                    "permissions": json.loads(row[2])
                })
            
            return collaborators

    def remove_collaborator(
        self,
        conversation_id: str,
        user_id: str
    ) -> bool:
        """Remove a collaborator from a conversation."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM conversation_collaborators
                WHERE conversation_id = ? AND user_id = ?
            """, (conversation_id, user_id))
            conn.commit()
            
            return cursor.rowcount > 0

    def update_collaborator_permissions(
        self,
        conversation_id: str,
        user_id: str,
        permissions: List[str]
    ) -> bool:
        """Update a collaborator's permissions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE conversation_collaborators
                SET permissions = ?
                WHERE conversation_id = ? AND user_id = ?
            """, (
                json.dumps(permissions),
                conversation_id,
                user_id
            ))
            conn.commit()
            
            return cursor.rowcount > 0

    def add_comment(
        self,
        conversation_id: str,
        message_id: str,
        user_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a comment to a message."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO message_comments (
                    conversation_id, message_id, user_id,
                    content, metadata, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                conversation_id,
                message_id,
                user_id,
                content,
                json.dumps(metadata or {}),
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            
            return cursor.lastrowid

    def get_comments(
        self,
        conversation_id: str,
        message_id: str
    ) -> List[Dict[str, Any]]:
        """Get all comments for a message."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, content, metadata, created_at
                FROM message_comments
                WHERE conversation_id = ? AND message_id = ?
                ORDER BY created_at ASC
            """, (conversation_id, message_id))
            
            comments = []
            for row in cursor.fetchall():
                comments.append({
                    "user_id": row[0],
                    "content": row[1],
                    "metadata": json.loads(row[2]),
                    "created_at": datetime.fromisoformat(row[3])
                })
            
            return comments

    def delete_comment(
        self,
        conversation_id: str,
        message_id: str,
        comment_id: str
    ) -> bool:
        """Delete a comment."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM message_comments
                WHERE conversation_id = ? AND message_id = ? AND id = ?
            """, (conversation_id, message_id, comment_id))
            conn.commit()
            
            return cursor.rowcount > 0

    def create_backup(
        self,
        backup_dir: str,
        compression: bool = True,
        deduplication: bool = True,
        encryption_key: Optional[bytes] = None
    ) -> str:
        """Create a backup of the conversation store."""
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"conversation_store_{timestamp}.backup")
        
        # Create temporary directory for backup
        temp_dir = os.path.join(backup_dir, f"temp_{timestamp}")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Export database
            db_backup = os.path.join(temp_dir, "store.db")
            with sqlite3.connect(self.db_path) as source:
                backup = sqlite3.connect(db_backup)
                source.backup(backup)
                backup.close()
            
            # Export search index
            if hasattr(self, "search_index"):
                search_backup = os.path.join(temp_dir, "search_index.db")
                with sqlite3.connect(self.search_index_path) as source:
                    backup = sqlite3.connect(search_backup)
                    source.backup(backup)
                    backup.close()
            
            # Create backup manifest
            manifest = {
                "version": "1.0",
                "timestamp": timestamp,
                "compression": compression,
                "deduplication": deduplication,
                "encryption": encryption_key is not None,
                "files": []
            }
            
            # Process files for backup
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, temp_dir)
                    
                    # Calculate file hash for deduplication
                    file_hash = None
                    if deduplication:
                        with open(file_path, "rb") as f:
                            file_hash = hashlib.sha256(f.read()).hexdigest()
                    
                    # Compress file if requested
                    if compression:
                        compressed_path = f"{file_path}.gz"
                        with open(file_path, "rb") as f_in:
                            with gzip.open(compressed_path, "wb") as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        os.remove(file_path)
                        file_path = compressed_path
                    
                    # Encrypt file if key is provided
                    if encryption_key:
                        encrypted_path = f"{file_path}.enc"
                        with open(file_path, "rb") as f:
                            data = f.read()
                            encrypted_data = self.encryption_engine.encrypt_data(
                                data,
                                encryption_key
                            )[0]
                            with open(encrypted_path, "wb") as f:
                                f.write(encrypted_data)
                        os.remove(file_path)
                        file_path = encrypted_path
                    
                    manifest["files"].append({
                        "path": rel_path,
                        "hash": file_hash,
                        "compressed": compression,
                        "encrypted": encryption_key is not None
                    })
            
            # Create backup archive
            with tarfile.open(backup_file, "w:gz") as tar:
                # Add manifest
                manifest_path = os.path.join(temp_dir, "manifest.json")
                with open(manifest_path, "w") as f:
                    json.dump(manifest, f, indent=2)
                tar.add(manifest_path, arcname="manifest.json")
                
                # Add files
                for file_info in manifest["files"]:
                    file_path = os.path.join(temp_dir, file_info["path"])
                    tar.add(file_path, arcname=file_info["path"])
            
            return backup_file
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    def restore_backup(
        self,
        backup_file: str,
        encryption_key: Optional[bytes] = None
    ) -> bool:
        """Restore a backup of the conversation store."""
        # Create temporary directory for restoration
        temp_dir = os.path.join(os.path.dirname(backup_file), "temp_restore")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Extract backup archive
            with tarfile.open(backup_file, "r:gz") as tar:
                tar.extractall(temp_dir)
            
            # Read manifest
            manifest_path = os.path.join(temp_dir, "manifest.json")
            with open(manifest_path) as f:
                manifest = json.load(f)
            
            # Validate version
            if manifest["version"] != "1.0":
                raise ValueError("Unsupported backup version")
            
            # Process files
            for file_info in manifest["files"]:
                file_path = os.path.join(temp_dir, file_info["path"])
                
                # Decrypt file if needed
                if file_info["encrypted"]:
                    if not encryption_key:
                        raise ValueError("Encryption key required for this backup")
                    
                    decrypted_path = f"{file_path}.dec"
                    with open(file_path, "rb") as f:
                        data = f.read()
                        decrypted_data = self.encryption_engine.decrypt_data(
                            data,
                            encryption_key
                        )
                        with open(decrypted_path, "wb") as f:
                            f.write(decrypted_data)
                    os.remove(file_path)
                    file_path = decrypted_path
                
                # Decompress file if needed
                if file_info["compressed"]:
                    decompressed_path = f"{file_path}.decomp"
                    with gzip.open(file_path, "rb") as f_in:
                        with open(decompressed_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(file_path)
                    file_path = decompressed_path
                
                # Restore database files
                if file_info["path"] == "store.db":
                    with sqlite3.connect(file_path) as source:
                        backup = sqlite3.connect(self.db_path)
                        source.backup(backup)
                        backup.close()
                
                elif file_info["path"] == "search_index.db":
                    with sqlite3.connect(file_path) as source:
                        backup = sqlite3.connect(self.search_index_path)
                        source.backup(backup)
                        backup.close()
            
            return True
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    def list_backups(
        self,
        backup_dir: str
    ) -> List[Dict[str, Any]]:
        """List available backups."""
        backups = []
        
        for file in os.listdir(backup_dir):
            if file.endswith(".backup"):
                file_path = os.path.join(backup_dir, file)
                
                # Extract timestamp from filename
                timestamp = file.split("_")[-1].replace(".backup", "")
                
                # Get file size and modification time
                stat = os.stat(file_path)
                
                # Read manifest if possible
                manifest = None
                try:
                    with tarfile.open(file_path, "r:gz") as tar:
                        manifest_file = tar.extractfile("manifest.json")
                        if manifest_file:
                            manifest = json.loads(manifest_file.read().decode())
                except:
                    pass
                
                backups.append({
                    "file": file,
                    "path": file_path,
                    "timestamp": timestamp,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "manifest": manifest
                })
        
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)

    def cleanup_backups(
        self,
        backup_dir: str,
        max_backups: int = 10,
        min_age_days: int = 7
    ) -> List[str]:
        """Clean up old backups."""
        backups = self.list_backups(backup_dir)
        now = datetime.utcnow()
        deleted = []
        
        # Sort backups by timestamp
        backups.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Keep only the most recent max_backups
        for backup in backups[max_backups:]:
            backup_age = (now - backup["modified"]).days
            if backup_age >= min_age_days:
                try:
                    os.remove(backup["path"])
                    deleted.append(backup["file"])
                except:
                    pass
        
        return deleted

    def create_incremental_backup(
        self,
        backup_dir: str,
        last_backup_timestamp: Optional[str] = None,
        compression: bool = True,
        deduplication: bool = True,
        encryption_key: Optional[bytes] = None
    ) -> str:
        """Create an incremental backup of the conversation store."""
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"conversation_store_incremental_{timestamp}.backup")
        
        # Create temporary directory for backup
        temp_dir = os.path.join(backup_dir, f"temp_{timestamp}")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Get last backup timestamp if not provided
            if not last_backup_timestamp:
                backups = self.list_backups(backup_dir)
                if backups:
                    last_backup_timestamp = backups[0]["timestamp"]
                else:
                    # If no previous backup, create a full backup
                    return self.create_backup(
                        backup_dir,
                        compression,
                        deduplication,
                        encryption_key
                    )
            
            # Create backup manifest
            manifest = {
                "version": "1.0",
                "timestamp": timestamp,
                "last_backup": last_backup_timestamp,
                "type": "incremental",
                "compression": compression,
                "deduplication": deduplication,
                "encryption": encryption_key is not None,
                "files": []
            }
            
            # Get changed conversations since last backup
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT conversation_id, updated_at
                    FROM conversations
                    WHERE updated_at > ?
                """, (last_backup_timestamp,))
                
                changed_conversations = cursor.fetchall()
            
            # Process changed conversations
            for conv_id, updated_at in changed_conversations:
                # Export conversation data
                conv_backup = os.path.join(temp_dir, f"conversation_{conv_id}.db")
                with sqlite3.connect(self.db_path) as source:
                    backup = sqlite3.connect(conv_backup)
                    source.backup(backup)
                    backup.close()
                
                # Process backup file
                file_path = conv_backup
                rel_path = os.path.relpath(file_path, temp_dir)
                
                # Calculate file hash for deduplication
                file_hash = None
                if deduplication:
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                
                # Compress file if requested
                if compression:
                    compressed_path = f"{file_path}.gz"
                    with open(file_path, "rb") as f_in:
                        with gzip.open(compressed_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(file_path)
                    file_path = compressed_path
                
                # Encrypt file if key is provided
                if encryption_key:
                    encrypted_path = f"{file_path}.enc"
                    with open(file_path, "rb") as f:
                        data = f.read()
                        encrypted_data = self.encryption_engine.encrypt_data(
                            data,
                            encryption_key
                        )[0]
                        with open(encrypted_path, "wb") as f:
                            f.write(encrypted_data)
                    os.remove(file_path)
                    file_path = encrypted_path
                
                manifest["files"].append({
                    "path": rel_path,
                    "hash": file_hash,
                    "compressed": compression,
                    "encrypted": encryption_key is not None,
                    "conversation_id": conv_id,
                    "updated_at": updated_at
                })
            
            # Create backup archive
            with tarfile.open(backup_file, "w:gz") as tar:
                # Add manifest
                manifest_path = os.path.join(temp_dir, "manifest.json")
                with open(manifest_path, "w") as f:
                    json.dump(manifest, f, indent=2)
                tar.add(manifest_path, arcname="manifest.json")
                
                # Add files
                for file_info in manifest["files"]:
                    file_path = os.path.join(temp_dir, file_info["path"])
                    tar.add(file_path, arcname=file_info["path"])
            
            return backup_file
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    def verify_backup(
        self,
        backup_file: str,
        encryption_key: Optional[bytes] = None
    ) -> Tuple[bool, List[str]]:
        """Verify the integrity of a backup file."""
        issues = []
        
        # Create temporary directory for verification
        temp_dir = os.path.join(os.path.dirname(backup_file), "temp_verify")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Extract backup archive
            with tarfile.open(backup_file, "r:gz") as tar:
                tar.extractall(temp_dir)
            
            # Read manifest
            manifest_path = os.path.join(temp_dir, "manifest.json")
            with open(manifest_path) as f:
                manifest = json.load(f)
            
            # Validate version
            if manifest["version"] != "1.0":
                issues.append("Unsupported backup version")
                return False, issues
            
            # Process files
            for file_info in manifest["files"]:
                file_path = os.path.join(temp_dir, file_info["path"])
                
                # Verify file exists
                if not os.path.exists(file_path):
                    issues.append(f"Missing file: {file_info['path']}")
                    continue
                
                # Decrypt file if needed
                if file_info["encrypted"]:
                    if not encryption_key:
                        issues.append("Encryption key required for verification")
                        continue
                    
                    try:
                        decrypted_path = f"{file_path}.dec"
                        with open(file_path, "rb") as f:
                            data = f.read()
                            decrypted_data = self.encryption_engine.decrypt_data(
                                data,
                                encryption_key
                            )
                            with open(decrypted_path, "wb") as f:
                                f.write(decrypted_data)
                        os.remove(file_path)
                        file_path = decrypted_path
                    except Exception as e:
                        issues.append(f"Decryption failed for {file_info['path']}: {str(e)}")
                        continue
                
                # Decompress file if needed
                if file_info["compressed"]:
                    try:
                        decompressed_path = f"{file_path}.decomp"
                        with gzip.open(file_path, "rb") as f_in:
                            with open(decompressed_path, "wb") as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        os.remove(file_path)
                        file_path = decompressed_path
                    except Exception as e:
                        issues.append(f"Decompression failed for {file_info['path']}: {str(e)}")
                        continue
                
                # Verify file hash if available
                if file_info["hash"]:
                    with open(file_path, "rb") as f:
                        current_hash = hashlib.sha256(f.read()).hexdigest()
                        if current_hash != file_info["hash"]:
                            issues.append(f"Hash mismatch for {file_info['path']}")
                
                # Verify database integrity
                if file_info["path"].endswith(".db"):
                    try:
                        with sqlite3.connect(file_path) as conn:
                            cursor = conn.cursor()
                            cursor.execute("PRAGMA integrity_check")
                            result = cursor.fetchone()
                            if result[0] != "ok":
                                issues.append(f"Database integrity check failed for {file_info['path']}")
                    except Exception as e:
                        issues.append(f"Database verification failed for {file_info['path']}: {str(e)}")
            
            return len(issues) == 0, issues
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    def schedule_backup(
        self,
        schedule_type: str,
        schedule_params: Dict[str, Any],
        backup_dir: str,
        compression: bool = True,
        deduplication: bool = True,
        encryption_key: Optional[bytes] = None,
        cloud_storage: Optional[Dict[str, Any]] = None
    ) -> str:
        """Schedule automated backups."""
        schedule_id = str(uuid.uuid4())
        
        # Validate schedule type
        if schedule_type not in ["daily", "weekly", "monthly", "custom"]:
            raise ValueError(f"Invalid schedule type: {schedule_type}")
        
        # Create schedule record
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO backup_schedules (
                    schedule_id, schedule_type, schedule_params,
                    backup_dir, compression, deduplication,
                    encryption_key, cloud_storage, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                schedule_id,
                schedule_type,
                json.dumps(schedule_params),
                backup_dir,
                compression,
                deduplication,
                encryption_key.hex() if encryption_key else None,
                json.dumps(cloud_storage) if cloud_storage else None,
                datetime.utcnow().isoformat()
            ))
            conn.commit()
        
        return schedule_id

    def get_backup_schedules(self) -> List[Dict[str, Any]]:
        """Get all backup schedules."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM backup_schedules")
            
            schedules = []
            for row in cursor.fetchall():
                schedules.append({
                    "schedule_id": row[0],
                    "schedule_type": row[1],
                    "schedule_params": json.loads(row[2]),
                    "backup_dir": row[3],
                    "compression": bool(row[4]),
                    "deduplication": bool(row[5]),
                    "encryption_key": bytes.fromhex(row[6]) if row[6] else None,
                    "cloud_storage": json.loads(row[7]) if row[7] else None,
                    "created_at": datetime.fromisoformat(row[8])
                })
            
            return schedules

    def delete_backup_schedule(self, schedule_id: str) -> bool:
        """Delete a backup schedule."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM backup_schedules
                WHERE schedule_id = ?
            """, (schedule_id,))
            conn.commit()
            
            return cursor.rowcount > 0

    def connect_cloud_storage(
        self,
        storage_type: str,
        credentials: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Connect to cloud storage."""
        connection_id = str(uuid.uuid4())
        
        # Validate storage type
        if storage_type not in ["s3", "ftp", "sftp", "webdav", "custom"]:
            raise ValueError(f"Invalid storage type: {storage_type}")
        
        # Create connection record
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cloud_storage_connections (
                    connection_id, storage_type, credentials,
                    options, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                connection_id,
                storage_type,
                json.dumps(credentials),
                json.dumps(options or {}),
                datetime.utcnow().isoformat()
            ))
            conn.commit()
        
        return connection_id

    def upload_to_cloud(
        self,
        connection_id: str,
        local_path: str,
        remote_path: str,
        compression: bool = True,
        encryption_key: Optional[bytes] = None
    ) -> bool:
        """Upload a file to cloud storage."""
        # Get connection details
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT storage_type, credentials, options
                FROM cloud_storage_connections
                WHERE connection_id = ?
            """, (connection_id,))
            
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Connection not found: {connection_id}")
            
            storage_type = row[0]
            credentials = json.loads(row[1])
            options = json.loads(row[2])
        
        # Create temporary directory for processing
        temp_dir = os.path.join(os.path.dirname(local_path), "temp_upload")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Process file for upload
            file_path = local_path
            
            # Compress if requested
            if compression:
                compressed_path = os.path.join(temp_dir, f"{os.path.basename(local_path)}.gz")
                with open(local_path, "rb") as f_in:
                    with gzip.open(compressed_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                file_path = compressed_path
            
            # Encrypt if key is provided
            if encryption_key:
                encrypted_path = f"{file_path}.enc"
                with open(file_path, "rb") as f:
                    data = f.read()
                    encrypted_data = self.encryption_engine.encrypt_data(
                        data,
                        encryption_key
                    )[0]
                    with open(encrypted_path, "wb") as f:
                        f.write(encrypted_data)
                file_path = encrypted_path
            
            # Upload based on storage type
            if storage_type == "s3":
                import boto3
                s3 = boto3.client(
                    "s3",
                    aws_access_key_id=credentials["access_key"],
                    aws_secret_access_key=credentials["secret_key"],
                    region_name=credentials.get("region", "us-east-1")
                )
                s3.upload_file(file_path, credentials["bucket"], remote_path)
            
            elif storage_type == "ftp":
                from ftplib import FTP
                ftp = FTP(credentials["host"])
                ftp.login(credentials["username"], credentials["password"])
                with open(file_path, "rb") as f:
                    ftp.storbinary(f"STOR {remote_path}", f)
                ftp.quit()
            
            elif storage_type == "sftp":
                import paramiko
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    credentials["host"],
                    username=credentials["username"],
                    password=credentials.get("password"),
                    key_filename=credentials.get("key_file")
                )
                sftp = ssh.open_sftp()
                sftp.put(file_path, remote_path)
                sftp.close()
                ssh.close()
            
            elif storage_type == "webdav":
                from webdav3.client import Client
                client = Client({
                    "webdav_hostname": credentials["host"],
                    "webdav_login": credentials["username"],
                    "webdav_password": credentials["password"]
                })
                client.upload_sync(remote_path, file_path)
            
            elif storage_type == "custom":
                # Use custom upload function if provided
                if "upload_function" in options:
                    options["upload_function"](file_path, remote_path, credentials)
                else:
                    raise ValueError("Custom upload function not provided")
            
            return True
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    def safe_code_modification(
        self,
        connection_id: str,
        local_path: str,
        remote_path: str,
        modification_function: Callable[[str], None],
        backup_dir: Optional[str] = None,
        compression: bool = True,
        encryption_key: Optional[bytes] = None
    ) -> bool:
        """Safely modify code with backup and rollback capability."""
        # Create backup of current code
        if backup_dir:
            backup_file = self.create_backup(
                backup_dir,
                compression=compression,
                encryption_key=encryption_key
            )
        else:
            backup_file = None
        
        try:
            # Download current code
            temp_dir = os.path.join(os.path.dirname(local_path), "temp_modify")
            os.makedirs(temp_dir, exist_ok=True)
            
            try:
                # Download from remote
                self.download_from_cloud(
                    connection_id,
                    remote_path,
                    local_path
                )
                
                # Create local copy
                local_copy = os.path.join(temp_dir, "code_copy")
                shutil.copy2(local_path, local_copy)
                
                # Apply modifications
                modification_function(local_copy)
                
                # Verify modifications
                if self.verify_code_modifications(local_copy):
                    # Upload modified code
                    self.upload_to_cloud(
                        connection_id,
                        local_copy,
                        remote_path,
                        compression=False
                    )
                    return True
                else:
                    raise ValueError("Code modification verification failed")
                
            finally:
                # Clean up temporary directory
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            # Rollback on failure
            if backup_file:
                self.restore_backup(backup_file)
            raise e

    def verify_code_modifications(self, modified_path: str) -> bool:
        """Verify code modifications."""
        # Add your code verification logic here
        # This could include:
        # - Syntax checking
        # - Unit test execution
        # - Code style validation
        # - Security scanning
        # - Performance testing
        return True

    def download_from_cloud(
        self,
        connection_id: str,
        remote_path: str,
        local_path: str
    ) -> bool:
        """Download a file from cloud storage."""
        # Get connection details
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT storage_type, credentials, options
                FROM cloud_storage_connections
                WHERE connection_id = ?
            """, (connection_id,))
            
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Connection not found: {connection_id}")
            
            storage_type = row[0]
            credentials = json.loads(row[1])
            options = json.loads(row[2])
        
        # Download based on storage type
        if storage_type == "s3":
            import boto3
            s3 = boto3.client(
                "s3",
                aws_access_key_id=credentials["access_key"],
                aws_secret_access_key=credentials["secret_key"],
                region_name=credentials.get("region", "us-east-1")
            )
            s3.download_file(credentials["bucket"], remote_path, local_path)
        
        elif storage_type == "ftp":
            from ftplib import FTP
            ftp = FTP(credentials["host"])
            ftp.login(credentials["username"], credentials["password"])
            with open(local_path, "wb") as f:
                ftp.retrbinary(f"RETR {remote_path}", f.write)
            ftp.quit()
        
        elif storage_type == "sftp":
            import paramiko
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                credentials["host"],
                username=credentials["username"],
                password=credentials.get("password"),
                key_filename=credentials.get("key_file")
            )
            sftp = ssh.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            ssh.close()
        
        elif storage_type == "webdav":
            from webdav3.client import Client
            client = Client({
                "webdav_hostname": credentials["host"],
                "webdav_login": credentials["username"],
                "webdav_password": credentials["password"]
            })
            client.download_sync(remote_path, local_path)
        
        elif storage_type == "custom":
            # Use custom download function if provided
            if "download_function" in options:
                options["download_function"](remote_path, local_path, credentials)
            else:
                raise ValueError("Custom download function not provided")
        
        return True 