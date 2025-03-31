import logging
import json
from typing import Dict, Any, Optional, List
import requests
from .base import BaseProviderAdapter, AuthenticationError, RateLimitError, ServiceUnavailableError
from ..config import Capability, ProviderConfig

logger = logging.getLogger(__name__)

class GroqAdapter(BaseProviderAdapter):
    """Groq implementation of provider adapter for high-performance LLMs"""
    
    def __init__(self, config: ProviderConfig):
        self.name = "groq"
        self.base_url = "https://api.groq.com/openai/v1"
        self.available_models = {
            "llama2-70b-4096": "Llama 2 70B",
            "mixtral-8x7b-32768": "Mixtral 8x7B"
        }
        super().__init__(config)
    
    def _initialize(self) -> None:
        """Initialize the Groq client"""
        try:
            # Get API key from credentials
            api_key = self.config.credentials.api_key
            if not api_key:
                raise AuthenticationError("Groq API key not provided")
            
            # Set up headers
            self.headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Verify API key by making a test request
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers
            )
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid Groq API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code != 200:
                raise ServiceUnavailableError(f"Groq API error: {response.text}")
            
            logger.info("Successfully initialized Groq adapter")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to initialize Groq adapter: {str(e)}")
            raise
    
    def get_capabilities(self) -> Dict[Capability, float]:
        """Return Groq's capabilities with confidence scores"""
        return {
            Capability.TEXT_GENERATION: 0.95,  # Excellent at text generation
            Capability.CODE_GENERATION: 0.9,   # Very good at code generation
            Capability.PLAN_CREATION: 0.92,    # Excellent at planning
        }
    
    def list_available_models(self) -> List[str]:
        """List all available Groq models"""
        return list(self.available_models.keys())
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """Generate text using the specified Groq model"""
        if not model:
            model = self.config.default_model or "llama2-70b-4096"
        
        if model not in self.available_models:
            raise InvalidRequestError(f"Model {model} not available")
        
        try:
            # Prepare request payload
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": parameters.get("temperature", 0.7),
                "max_tokens": parameters.get("max_tokens", 1000),
                "stream": False
            }
            
            # Make request to Groq API
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid Groq API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code != 200:
                raise ServiceUnavailableError(f"Groq API error: {response.text}")
            
            # Extract response
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error generating text with Groq: {str(e)}")
            raise ServiceUnavailableError("Failed to generate text with Groq")
        except Exception as e:
            logger.error(f"Unexpected error in Groq generate: {str(e)}")
            raise 