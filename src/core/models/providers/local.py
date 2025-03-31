"""Local LLM provider implementation."""
from typing import Dict, List, Optional, Any
import logging
import os
import json
from datetime import datetime
import subprocess
import tempfile

from src.core.models.providers.base import ModelProvider
from src.core.models.types import ModelCapability, ProviderResponse

# Configure logging
logger = logging.getLogger("ade-local-provider")

class LocalProvider(ModelProvider):
    """Local LLM provider implementation"""
    
    def __init__(
        self, 
        api_key: str,  # Not used but required by interface
        provider_id: Optional[str] = None,
        model_map: Optional[Dict[str, str]] = None,
        default_parameters: Optional[Dict[str, Any]] = None,
        model_path: Optional[str] = None
    ):
        super().__init__(api_key, provider_id)
        self.model_path = model_path or os.getenv("LOCAL_MODEL_PATH", "models/llama-2-7b-chat")
        self.model_map = model_map or {
            ModelCapability.CODE_GENERATION: self.model_path,
            ModelCapability.CODE_UNDERSTANDING: self.model_path,
            ModelCapability.CODE_EXPLANATION: self.model_path,
            ModelCapability.PLANNING: self.model_path,
            ModelCapability.REASONING: self.model_path,
            ModelCapability.DEBUGGING: self.model_path,
            ModelCapability.DOCUMENTATION: self.model_path,
            ModelCapability.SUMMARIZATION: self.model_path,
            ModelCapability.CHAT: self.model_path
        }
        self.default_parameters = default_parameters or {
            "temperature": 0.2,
            "max_tokens": 2000
        }
        self.executable = os.getenv("LOCAL_LLM_EXECUTABLE", "llama-cpp-python")
    
    @property
    def provider_type(self) -> str:
        return "local"
    
    def initialize(self) -> bool:
        """Initialize the Local LLM"""
        try:
            # Check if model file exists
            if not os.path.exists(self.model_path):
                logger.error(f"Model file not found: {self.model_path}")
                return False
                
            # Test if executable is available
            result = subprocess.run([self.executable, "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to run local LLM executable: {result.stderr}")
                return False
            
            self.is_initialized = True
            logger.info(f"Local LLM provider {self.provider_id} initialized successfully with model {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Local LLM provider: {str(e)}")
            self.is_initialized = False
            return False
    
    def list_available_models(self) -> List[str]:
        """List all available local models"""
        # Scan models directory for available models
        models_dir = os.path.dirname(self.model_path)
        if not os.path.exists(models_dir):
            return [self.model_path]
        
        # List directories in models_dir
        models = []
        for item in os.listdir(models_dir):
            full_path = os.path.join(models_dir, item)
            if os.path.isdir(full_path):
                models.append(full_path)
        
        return models or [self.model_path]
    
    def get_capabilities(self) -> List[ModelCapability]:
        """Return the capabilities this provider supports"""
        return [
            ModelCapability.CODE_GENERATION,
            ModelCapability.CODE_UNDERSTANDING,
            ModelCapability.CODE_EXPLANATION,
            ModelCapability.PLANNING,
            ModelCapability.REASONING,
            ModelCapability.DEBUGGING,
            ModelCapability.DOCUMENTATION,
            ModelCapability.SUMMARIZATION,
            ModelCapability.CHAT
        ]
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        images: Optional[List[bytes]] = None
    ) -> ProviderResponse:
        """Generate text from a prompt using Local LLM"""
        if not self.is_initialized:
            raise Exception("Local LLM provider not initialized")
        
        # Use default model if not specified
        if not model:
            model = self.model_path
        
        # Merge default parameters with provided parameters
        params = {**self.default_parameters}
        if parameters:
            params.update(parameters)
        
        try:
            # Write prompt to temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as prompt_file:
                prompt_file.write(prompt)
                prompt_path = prompt_file.name
            
            # Prepare command
            cmd = [
                self.executable,
                "--model", model,
                "--prompt", prompt_path,
                "--temp", str(params.get("temperature", 0.2)),
                "--tokens", str(params.get("max_tokens", 2000))
            ]
            
            # Run local LLM
            start_time = datetime.now()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            response_time = (datetime.now() - start_time).total_seconds() * 1000  # in ms
            
            # Clean up temp file
            os.unlink(prompt_path)
            
            if result.returncode != 0:
                logger.error(f"Local LLM error: {result.stderr}")
                
                # Record failure
                self.performance.record_failure(response_time)
                
                raise Exception(f"Local LLM error: {result.stderr}")
            
            # Record success
            content = result.stdout.strip()
            self.performance.record_success(response_time, len(content.split()))
            
            return ProviderResponse(
                content=content,
                raw_response=result,
                metadata={
                    "model": model,
                    "response_time_ms": response_time
                }
            )
            
        except Exception as e:
            logger.error(f"Local LLM generation error: {str(e)}")
            self.performance.record_failure()
            raise 