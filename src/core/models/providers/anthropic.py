"""Anthropic provider implementation."""
from typing import Dict, Optional, Any, List
import logging
from datetime import datetime
import json
import aiohttp

from src.core.models.providers.base import ModelProvider
from src.core.models.types import ModelCapability, ProviderResponse

logger = logging.getLogger(__name__)

class AnthropicProvider(ModelProvider):
    """Anthropic provider implementation."""
    
    def __init__(self, api_key: str, provider_id: Optional[str] = None):
        """Initialize the Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            provider_id: Optional provider ID
        """
        super().__init__(api_key, provider_id)
        self.capabilities_scores = {
            ModelCapability.TEXT_GENERATION: 0.95,
            ModelCapability.CODE_GENERATION: 0.9,
            ModelCapability.IMAGE_UNDERSTANDING: 0.85
        }
        self.base_url = "https://api.anthropic.com/v1"
        self.default_model = "claude-3-opus-20240229"
        self.is_initialized = True
    
    def has_capability(self, capability: ModelCapability) -> bool:
        """Check if the provider supports a specific capability.
        
        Args:
            capability: The capability to check
            
        Returns:
            True if the provider supports the capability
        """
        return capability in self.capabilities_scores
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        images: Optional[List[bytes]] = None
    ) -> ProviderResponse:
        """Generate a response from Anthropic.
        
        Args:
            prompt: The prompt to send to Anthropic
            model: Optional model to use
            parameters: Optional parameters for the request
            images: Optional list of images for multimodal models
            
        Returns:
            The provider's response
            
        Raises:
            Exception: If the request fails
        """
        start_time = datetime.now()
        
        try:
            # Prepare request data
            data = {
                "model": model or self.default_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": parameters.get("max_tokens", 1000) if parameters else 1000,
                "temperature": parameters.get("temperature", 0.7) if parameters else 0.7,
                "top_p": parameters.get("top_p", 1.0) if parameters else 1.0
            }
            
            # Add images if provided
            if images:
                data["messages"][0]["content"] = [
                    {"type": "text", "text": prompt},
                    *[{"type": "image", "source": {"type": "base64", "data": image}} for image in images]
                ]
            
            # Make request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2024-02-29",
                        "Content-Type": "application/json"
                    },
                    json=data
                ) as response:
                    response_data = await response.json()
                    
                    if response.status != 200:
                        raise Exception(f"Anthropic API error: {response_data.get('error', {}).get('message', 'Unknown error')}")
                    
                    # Extract response
                    content = response_data["content"][0]["text"]
                    
                    # Update performance metrics
                    self.performance.success_count += 1
                    self.performance.last_success = datetime.now()
                    self.performance.consecutive_failures = 0
                    self.performance.total_requests += 1
                    self.performance.total_latency += (datetime.now() - start_time).total_seconds()
                    
                    # Calculate cost
                    input_tokens = response_data["usage"]["input_tokens"]
                    output_tokens = response_data["usage"]["output_tokens"]
                    cost = self._calculate_cost(model or self.default_model, input_tokens, output_tokens)
                    self.performance.total_cost += cost
                    
                    return ProviderResponse(
                        content=content,
                        raw_response=response_data,
                        model=model or self.default_model,
                        latency=(datetime.now() - start_time).total_seconds(),
                        cost=cost
                    )
                    
        except Exception as e:
            # Update performance metrics
            self.performance.failure_count += 1
            self.performance.last_failure = datetime.now()
            self.performance.consecutive_failures += 1
            self.performance.total_requests += 1
            self.performance.total_latency += (datetime.now() - start_time).total_seconds()
            
            logger.error(f"Anthropic provider error: {str(e)}")
            raise
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate the cost of a request.
        
        Args:
            model: The model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            The cost in USD
        """
        # Cost per 1K tokens (as of March 2024)
        costs = {
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "claude-3-haiku-20240307": {"input": 0.0005, "output": 0.0025}
        }
        
        model_costs = costs.get(model, costs["claude-3-sonnet-20240229"])
        return (
            (input_tokens * model_costs["input"] / 1000) +
            (output_tokens * model_costs["output"] / 1000)
        ) 