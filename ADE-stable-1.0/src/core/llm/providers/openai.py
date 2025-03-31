from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import openai
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

from ..base import (
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

class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        openai.api_key = config.api_key
        self._client = openai.AsyncOpenAI()
        
    async def validate_credentials(self) -> bool:
        """Validate OpenAI API credentials"""
        try:
            await self._client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI credential validation failed: {str(e)}")
            return False
            
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI API"""
        if not self._check_rate_limits():
            raise RateLimitError("Rate limit exceeded")
            
        try:
            # Prepare request parameters
            params = {
                "model": self.config.model_name,
                "messages": [{"role": "user", "content": request.prompt}],
                "max_tokens": request.max_tokens or self.config.max_tokens,
                "temperature": request.temperature or self.config.temperature,
                "top_p": self.config.top_p,
                "frequency_penalty": self.config.frequency_penalty,
                "presence_penalty": self.config.presence_penalty,
                "stop": request.stop or self.config.stop
            }
            
            # Make API request
            start_time = datetime.now()
            response = await self._client.chat.completions.create(**params)
            end_time = datetime.now()
            
            # Calculate costs
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = prompt_tokens + completion_tokens
            
            # Calculate cost based on model
            cost = self._calculate_cost(
                model=self.config.model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens
            )
            
            # Update usage statistics
            self._update_usage(total_tokens, cost)
            
            # Create standardized response
            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.config.model_name,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                },
                finish_reason=response.choices[0].finish_reason,
                cost=cost,
                latency=(end_time - start_time).total_seconds(),
                timestamp=datetime.now(),
                metadata={
                    "model": self.config.model_name,
                    "provider": "openai"
                }
            )
            
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit error: {str(e)}")
            raise RateLimitError(str(e))
            
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI API connection error: {str(e)}")
            raise LLMError(f"API connection error: {str(e)}")
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise LLMError(f"API error: {str(e)}")
            
    def _calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Calculate cost based on model and token usage"""
        # GPT-4 pricing (as of 2024)
        if model.startswith("gpt-4"):
            prompt_cost = prompt_tokens * 0.03 / 1000
            completion_cost = completion_tokens * 0.06 / 1000
        # GPT-3.5 pricing
        elif model.startswith("gpt-3.5"):
            prompt_cost = prompt_tokens * 0.001 / 1000
            completion_cost = completion_tokens * 0.002 / 1000
        # Default pricing
        else:
            prompt_cost = prompt_tokens * 0.001 / 1000
            completion_cost = completion_tokens * 0.002 / 1000
            
        return prompt_cost + completion_cost
        
    def can_handle_task(self, task_type: TaskType) -> bool:
        """Check if provider can handle specific task type"""
        # OpenAI models can handle all task types
        return True 