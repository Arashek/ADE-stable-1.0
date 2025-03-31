import logging
import json
from typing import Dict, Any, Optional, List
import requests
from .base import BaseProviderAdapter, ServiceUnavailableError, InvalidRequestError
from ..config import Capability, ProviderConfig

logger = logging.getLogger(__name__)

class OllamaAdapter(BaseProviderAdapter):
    """Ollama implementation of provider adapter for local LLMs"""
    
    def __init__(self, config: ProviderConfig):
        self.name = "ollama"
        self.base_url = config.server_url or "http://localhost:11434"
        self.available_models = {}
        super().__init__(config)
    
    def _initialize(self) -> None:
        """Initialize connection to Ollama server"""
        try:
            # Check server health
            response = requests.get(f"{self.base_url}/api/health")
            if response.status_code != 200:
                raise ServiceUnavailableError("Ollama server is not available")
            
            # Get list of available models
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                self.available_models = {
                    model["name"]: model["details"]
                    for model in response.json()["models"]
                }
            else:
                logger.warning("Failed to fetch available models from Ollama")
            
            logger.info("Successfully initialized Ollama adapter")
            
        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to Ollama server")
            raise ServiceUnavailableError("Ollama server is not accessible")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama adapter: {str(e)}")
            raise
    
    def get_capabilities(self) -> Dict[Capability, float]:
        """Return Ollama's capabilities with confidence scores"""
        return {
            Capability.TEXT_GENERATION: 0.8,  # Good at text generation
            Capability.CODE_GENERATION: 0.7,  # Decent at code generation
            Capability.PLAN_CREATION: 0.75,   # Good at planning
        }
    
    def list_available_models(self) -> List[str]:
        """List all available models from Ollama server"""
        return list(self.available_models.keys())
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """Generate text using the specified Ollama model"""
        if not model:
            model = self.config.default_model or "llama2"  # Default to llama2 if not specified
        
        if model not in self.available_models:
            raise InvalidRequestError(f"Model {model} not available")
        
        try:
            # Prepare request payload
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                **(parameters or {})
            }
            
            # Make request to Ollama API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            if response.status_code != 200:
                raise ServiceUnavailableError(f"Ollama API error: {response.text}")
            
            # Extract response
            result = response.json()
            return result["response"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error generating text with Ollama: {str(e)}")
            raise ServiceUnavailableError("Failed to generate text with Ollama")
        except Exception as e:
            logger.error(f"Unexpected error in Ollama generate: {str(e)}")
            raise 