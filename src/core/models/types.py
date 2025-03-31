"""Common types used across the models module."""
from enum import Enum
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ModelCapability(str, Enum):
    """Available model capabilities."""
    TEXT_GENERATION = "text_generation"
    PLANNING = "planning"
    CODE_GENERATION = "code_generation"
    CODE_UNDERSTANDING = "code_understanding"
    CODE_EXPLANATION = "code_explanation"
    REASONING = "reasoning"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"
    SUMMARIZATION = "summarization"
    CHAT = "chat"
    EMBEDDING = "embedding"
    VISION = "vision"
    AUDIO = "audio"

class ProviderType(str, Enum):
    """Supported provider types."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    DEEPSEEK = "deepseek"
    LOCAL = "local"
    CUSTOM = "custom"

class ProviderResponse(BaseModel):
    """Response from a provider"""
    content: str
    model_used: str
    tokens_input: int = 0
    tokens_output: int = 0
    cost: float = 0.0
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    raw_response: Any = None 