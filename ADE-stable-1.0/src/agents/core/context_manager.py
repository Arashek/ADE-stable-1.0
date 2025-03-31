from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
import json
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ConversationState:
    """State of a conversation with an AI model"""
    session_id: str
    messages: List[Dict[str, str]]
    metadata: Dict[str, Any]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class ContextManager:
    """Manages conversation state and context for AI interactions"""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.conversations: Dict[str, ConversationState] = {}
        self.context_cache: Dict[str, Dict[str, Any]] = {}
        
    def create_session(self, session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new conversation session
        
        Args:
            session_id: Optional custom session ID
            metadata: Optional metadata for the session
            
        Returns:
            Session ID
        """
        if not session_id:
            session_id = self._generate_session_id()
            
        metadata = metadata or {}
        self.conversations[session_id] = ConversationState(
            session_id=session_id,
            messages=[],
            metadata=metadata
        )
        
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """Add a message to the conversation
        
        Args:
            session_id: ID of the conversation session
            role: Role of the message sender (e.g., 'user', 'assistant')
            content: Message content
            
        Returns:
            True if message was added successfully
        """
        if session_id not in self.conversations:
            logger.error(f"Session {session_id} not found")
            return False
            
        conversation = self.conversations[session_id]
        conversation.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        conversation.updated_at = datetime.now()
        
        # Trim conversation if needed
        self._trim_conversation(session_id)
        
        return True
    
    def get_conversation(self, session_id: str) -> Optional[List[Dict[str, str]]]:
        """Get the full conversation history
        
        Args:
            session_id: ID of the conversation session
            
        Returns:
            List of messages if session exists, None otherwise
        """
        if session_id not in self.conversations:
            return None
            
        return self.conversations[session_id].messages
    
    def get_recent_messages(self, session_id: str, count: int = 5) -> Optional[List[Dict[str, str]]]:
        """Get the most recent messages from the conversation
        
        Args:
            session_id: ID of the conversation session
            count: Number of messages to retrieve
            
        Returns:
            List of recent messages if session exists, None otherwise
        """
        conversation = self.get_conversation(session_id)
        if not conversation:
            return None
            
        return conversation[-count:]
    
    def add_context(self, session_id: str, context_key: str, context_value: Any) -> bool:
        """Add context to the conversation
        
        Args:
            session_id: ID of the conversation session
            context_key: Key for the context
            context_value: Value to store
            
        Returns:
            True if context was added successfully
        """
        if session_id not in self.conversations:
            logger.error(f"Session {session_id} not found")
            return False
            
        conversation = self.conversations[session_id]
        conversation.metadata[context_key] = context_value
        conversation.updated_at = datetime.now()
        
        return True
    
    def get_context(self, session_id: str, context_key: str) -> Optional[Any]:
        """Get context from the conversation
        
        Args:
            session_id: ID of the conversation session
            context_key: Key for the context
            
        Returns:
            Context value if found, None otherwise
        """
        if session_id not in self.conversations:
            return None
            
        return self.conversations[session_id].metadata.get(context_key)
    
    def cache_context(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Cache context for later use
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional time-to-live in seconds
        """
        self.context_cache[key] = {
            "value": value,
            "expires_at": datetime.now().timestamp() + ttl if ttl else None
        }
    
    def get_cached_context(self, key: str) -> Optional[Any]:
        """Get cached context
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        if key not in self.context_cache:
            return None
            
        cache_entry = self.context_cache[key]
        if cache_entry["expires_at"] and datetime.now().timestamp() > cache_entry["expires_at"]:
            del self.context_cache[key]
            return None
            
        return cache_entry["value"]
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a conversation session
        
        Args:
            session_id: ID of the conversation session
            
        Returns:
            True if session was cleared successfully
        """
        if session_id not in self.conversations:
            return False
            
        del self.conversations[session_id]
        return True
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        timestamp = datetime.now().isoformat()
        random_bytes = hashlib.sha256(timestamp.encode()).digest()
        return hashlib.hexdigest(random_bytes)[:16]
    
    def _trim_conversation(self, session_id: str) -> None:
        """Trim conversation to fit within token limit"""
        if session_id not in self.conversations:
            return
            
        conversation = self.conversations[session_id]
        total_tokens = sum(len(msg["content"].split()) for msg in conversation.messages)
        
        while total_tokens > self.max_tokens and conversation.messages:
            # Remove oldest message
            removed = conversation.messages.pop(0)
            total_tokens -= len(removed["content"].split())
    
    def export_session(self, session_id: str) -> Optional[str]:
        """Export a conversation session to JSON
        
        Args:
            session_id: ID of the conversation session
            
        Returns:
            JSON string if session exists, None otherwise
        """
        if session_id not in self.conversations:
            return None
            
        conversation = self.conversations[session_id]
        export_data = {
            "session_id": conversation.session_id,
            "messages": conversation.messages,
            "metadata": conversation.metadata,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat()
        }
        
        return json.dumps(export_data, indent=2)
    
    def import_session(self, json_data: str) -> Optional[str]:
        """Import a conversation session from JSON
        
        Args:
            json_data: JSON string containing session data
            
        Returns:
            Session ID if import successful, None otherwise
        """
        try:
            data = json.loads(json_data)
            session_id = data["session_id"]
            
            self.conversations[session_id] = ConversationState(
                session_id=session_id,
                messages=data["messages"],
                metadata=data["metadata"],
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"])
            )
            
            return session_id
        except Exception as e:
            logger.error(f"Failed to import session: {str(e)}")
            return None 