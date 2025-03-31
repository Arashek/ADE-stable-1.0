from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import asyncio
from dataclasses import dataclass

from .base import (
    BaseLLMProvider,
    LLMConfig,
    LLMRequest,
    LLMResponse,
    LLMProvider,
    TaskType,
    LLMError,
    RateLimitError,
    QuotaExceededError
)

logger = logging.getLogger(__name__)

@dataclass
class ProviderStats:
    """Statistics for LLM provider"""
    success_rate: float
    average_latency: float
    total_cost: float
    last_error: Optional[str] = None
    last_success: Optional[datetime] = None

class LLMManager:
    """Manages multiple LLM providers with fallback mechanisms"""
    
    def __init__(self):
        self.providers: Dict[LLMProvider, BaseLLMProvider] = {}
        self.provider_stats: Dict[LLMProvider, ProviderStats] = {}
        self._provider_priority: List[LLMProvider] = []
        self._lock = asyncio.Lock()
        
    def register_provider(self, provider: BaseLLMProvider) -> None:
        """Register a new LLM provider"""
        self.providers[provider.config.provider] = provider
        self.provider_stats[provider.config.provider] = ProviderStats(
            success_rate=1.0,
            average_latency=0.0,
            total_cost=0.0
        )
        self._update_provider_priority()
        
    def _update_provider_priority(self) -> None:
        """Update provider priority based on performance"""
        self._provider_priority = sorted(
            self.providers.keys(),
            key=lambda p: (
                self.provider_stats[p].success_rate,
                -self.provider_stats[p].average_latency
            ),
            reverse=True
        )
        
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using best available provider with fallback"""
        async with self._lock:
            for provider_type in self._provider_priority:
                provider = self.providers[provider_type]
                
                if not provider.can_handle_task(request.task_type):
                    continue
                    
                try:
                    # Check rate limits
                    if not provider._check_rate_limits():
                        logger.warning(f"Rate limit exceeded for provider {provider_type}")
                        continue
                        
                    # Generate response
                    start_time = datetime.now()
                    response = await provider.generate(request)
                    end_time = datetime.now()
                    
                    # Update statistics
                    self._update_provider_stats(
                        provider_type,
                        True,
                        (end_time - start_time).total_seconds(),
                        response.cost
                    )
                    
                    return response
                    
                except RateLimitError:
                    logger.warning(f"Rate limit error for provider {provider_type}")
                    continue
                    
                except QuotaExceededError:
                    logger.warning(f"Quota exceeded for provider {provider_type}")
                    continue
                    
                except Exception as e:
                    logger.error(f"Error with provider {provider_type}: {str(e)}")
                    self._update_provider_stats(
                        provider_type,
                        False,
                        0,
                        0,
                        str(e)
                    )
                    continue
                    
            raise LLMError("No available providers could handle the request")
            
    def _update_provider_stats(
        self,
        provider_type: LLMProvider,
        success: bool,
        latency: float,
        cost: float,
        error: Optional[str] = None
    ) -> None:
        """Update provider statistics"""
        stats = self.provider_stats[provider_type]
        
        # Update success rate (weighted average)
        current_success_rate = 1.0 if success else 0.0
        stats.success_rate = (stats.success_rate * 0.9) + (current_success_rate * 0.1)
        
        # Update average latency (weighted average)
        stats.average_latency = (stats.average_latency * 0.9) + (latency * 0.1)
        
        # Update total cost
        stats.total_cost += cost
        
        # Update error and success timestamps
        if error:
            stats.last_error = error
        if success:
            stats.last_success = datetime.now()
            
        # Update provider priority
        self._update_provider_priority()
        
    def get_provider_stats(self) -> Dict[LLMProvider, ProviderStats]:
        """Get statistics for all providers"""
        return self.provider_stats.copy()
        
    def get_best_provider(self, task_type: TaskType) -> Optional[LLMProvider]:
        """Get best provider for specific task type"""
        for provider_type in self._provider_priority:
            provider = self.providers[provider_type]
            if provider.can_handle_task(task_type):
                return provider_type
        return None
        
    def get_provider_usage(self) -> Dict[LLMProvider, Dict[str, Any]]:
        """Get usage statistics for all providers"""
        return {
            provider_type: provider.get_usage_stats()
            for provider_type, provider in self.providers.items()
        }
        
    async def validate_all_providers(self) -> Dict[LLMProvider, bool]:
        """Validate credentials for all providers"""
        results = {}
        for provider_type, provider in self.providers.items():
            try:
                results[provider_type] = await provider.validate_credentials()
            except Exception as e:
                logger.error(f"Error validating provider {provider_type}: {str(e)}")
                results[provider_type] = False
        return results 