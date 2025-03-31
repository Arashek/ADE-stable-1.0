from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    AZURE = "azure"
    CUSTOM = "custom"

class TaskType(Enum):
    """Types of tasks that can be performed by LLMs"""
    CODE_ANALYSIS = "code_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"
    TOOL_SELECTION = "tool_selection"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    GENERAL = "general"

@dataclass
class LLMConfig:
    """Configuration for LLM provider"""
    provider: LLMProvider
    api_key: Optional[str] = None
    model_name: str = ""
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 1
    cost_per_token: float = 0.0
    max_requests_per_minute: int = 60
    max_tokens_per_minute: int = 100000

@dataclass
class LLMResponse:
    """Standardized response from LLM"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    cost: float
    latency: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LLMRequest:
    """Standardized request to LLM"""
    prompt: str
    task_type: TaskType
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stop: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class LLMError(Exception):
    """Base exception for LLM-related errors"""
    pass

class RateLimitError(LLMError):
    """Exception raised when rate limit is exceeded"""
    pass

class QuotaExceededError(LLMError):
    """Exception raised when quota is exceeded"""
    pass

class LLMProviderError(LLMError):
    """Exception raised when provider-specific error occurs"""
    pass

class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._request_count = 0
        self._token_count = 0
        self._last_request_time = datetime.now()
        self._cost_tracker = 0.0
        
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate provider credentials"""
        pass
    
    def _check_rate_limits(self) -> bool:
        """Check if rate limits are exceeded"""
        current_time = datetime.now()
        time_diff = (current_time - self._last_request_time).total_seconds()
        
        # Reset counters if a minute has passed
        if time_diff >= 60:
            self._request_count = 0
            self._token_count = 0
            self._last_request_time = current_time
            
        # Check request rate
        if self._request_count >= self.config.max_requests_per_minute:
            return False
            
        # Check token rate
        if self._token_count >= self.config.max_tokens_per_minute:
            return False
            
        return True
    
    def _update_usage(self, tokens: int, cost: float):
        """Update usage statistics"""
        self._request_count += 1
        self._token_count += tokens
        self._cost_tracker += cost
        self._last_request_time = datetime.now()
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return {
            "request_count": self._request_count,
            "token_count": self._token_count,
            "cost": self._cost_tracker,
            "last_request": self._last_request_time
        }
    
    def can_handle_task(self, task_type: TaskType) -> bool:
        """Check if provider can handle specific task type"""
        return True  # Override in specific providers
    
    def get_cost_estimate(self, tokens: int) -> float:
        """Estimate cost for token count"""
        return tokens * self.config.cost_per_token 