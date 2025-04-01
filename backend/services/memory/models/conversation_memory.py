"""
Conversation Memory Models

This module defines the data models for storing and retrieving conversation history,
enabling the platform to maintain context across user interactions.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Message(BaseModel):
    """Model for a single message in a conversation"""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender: str  # 'user', 'system', or agent_id
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class Conversation(BaseModel):
    """Model for a conversation between a user and the system"""
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    user_id: UUID
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List[Message] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class ConversationSummary(BaseModel):
    """Model for a summary of a conversation"""
    id: UUID
    project_id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message_timestamp: datetime
    tags: List[str]
    
class VectorEmbedding(BaseModel):
    """Model for a vector embedding of a message or conversation"""
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    content_id: UUID  # ID of the message or conversation
    content_type: str  # 'message' or 'conversation'
    embedding: List[float]
    text: str  # The text that was embedded
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class SemanticSearchResult(BaseModel):
    """Model for a semantic search result"""
    content_id: UUID
    content_type: str
    text: str
    similarity_score: float
    metadata: Dict[str, Any]
