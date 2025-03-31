from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
import logging
from ..config import ProviderConfig, Capability
from ..response import TextResponse, ImageResponse, PlanResponse

logger = logging.getLogger(__name__)

class AdapterError(Exception):
    """Base class for adapter errors"""
    pass

class AuthenticationError(AdapterError):
    """Error authenticating with provider"""
    pass

class RateLimitError(AdapterError):
    """Rate limit exceeded"""
    pass

class InvalidRequestError(AdapterError):
    """Invalid request to provider"""
    pass

class ServiceUnavailableError(AdapterError):
    """Provider service unavailable"""
    pass

class BaseProviderAdapter(ABC):
    """Base class for provider adapters"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self._validate_config()
        self.name = "base"  # Override in subclasses
        self.initialized = False
        try:
            self._initialize()
            self.initialized = True
            logger.info(f"Initialized {self.name} adapter")
        except Exception as e:
            logger.error(f"Failed to initialize {self.name} adapter: {str(e)}")
            raise
    
    def _validate_config(self) -> None:
        """Validate provider configuration"""
        if not self.config.enabled:
            raise ValueError("Provider is not enabled")
            
        if not self.config.model_path:
            raise ValueError("Model path is required")
            
        if not self.config.capabilities:
            raise ValueError("Provider must have at least one capability")
    
    @abstractmethod
    async def generate_code_completion(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.95,
        stop_sequences: Optional[List[str]] = None
    ) -> str:
        """Generate code completion for the given prompt"""
        pass
    
    @abstractmethod
    async def generate_plan(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 0.95
    ) -> str:
        """Generate a plan for the given task"""
        pass
    
    def get_capability_score(self, capability: Capability) -> float:
        """Get the provider's score for a specific capability"""
        return self.config.capabilities.get(capability, 0.0)
    
    def supports_capability(self, capability: Capability) -> bool:
        """Check if the provider supports a specific capability"""
        return capability in self.config.capabilities
    
    def get_capabilities(self) -> Dict[Capability, float]:
        """Get all capabilities and their scores"""
        return self.config.capabilities.copy()
    
    def get_tier(self) -> str:
        """Get the provider's tier"""
        return self.config.tier.name
    
    def is_enabled(self) -> bool:
        """Check if the provider is enabled"""
        return self.config.enabled
    
    @abstractmethod
    def _initialize(self) -> None:
        """Initialize the provider with credentials"""
        pass
    
    def generate_text(self, prompt: str, **kwargs) -> TextResponse:
        """Generate text response"""
        try:
            result = self._generate_text_impl(prompt, **kwargs)
            return TextResponse(
                success=True,
                text=result,
                provider=self.name
            )
        except Exception as e:
            logger.error(f"{self.name} text generation error: {str(e)}")
            error_message = self._handle_provider_error(e)
            return TextResponse(
                success=False,
                text="",
                provider=self.name,
                error=error_message
            )
    
    @abstractmethod
    def _generate_text_impl(self, prompt: str, **kwargs) -> str:
        """Implementation of text generation"""
        pass
    
    def generate_code(self, spec: str, **kwargs) -> TextResponse:
        """Generate code based on specification"""
        try:
            result = self._generate_code_impl(spec, **kwargs)
            return TextResponse(
                success=True,
                text=result,
                provider=self.name
            )
        except Exception as e:
            logger.error(f"{self.name} code generation error: {str(e)}")
            error_message = self._handle_provider_error(e)
            return TextResponse(
                success=False,
                text="",
                provider=self.name,
                error=error_message
            )
    
    @abstractmethod
    def _generate_code_impl(self, spec: str, **kwargs) -> str:
        """Implementation of code generation"""
        pass
    
    def analyze_image(self, image_data: bytes, prompt: str, **kwargs) -> TextResponse:
        """Analyze image with text prompt"""
        try:
            result = self._analyze_image_impl(image_data, prompt, **kwargs)
            return TextResponse(
                success=True,
                text=result,
                provider=self.name
            )
        except Exception as e:
            logger.error(f"{self.name} image analysis error: {str(e)}")
            error_message = self._handle_provider_error(e)
            return TextResponse(
                success=False,
                text="",
                provider=self.name,
                error=error_message
            )
    
    @abstractmethod
    def _analyze_image_impl(self, image_data: bytes, prompt: str, **kwargs) -> str:
        """Implementation of image analysis"""
        pass
    
    def create_plan(self, goal: str, **kwargs) -> PlanResponse:
        """Create a structured plan for achieving a goal"""
        try:
            result = self._create_plan_impl(goal, **kwargs)
            return PlanResponse(
                success=True,
                plan=result,
                provider=self.name
            )
        except Exception as e:
            logger.error(f"{self.name} plan creation error: {str(e)}")
            error_message = self._handle_provider_error(e)
            return PlanResponse(
                success=False,
                plan={},
                provider=self.name,
                error=error_message
            )
    
    @abstractmethod
    def _create_plan_impl(self, goal: str, **kwargs) -> Dict[str, Any]:
        """Implementation of plan creation"""
        pass
    
    def _handle_provider_error(self, error: Exception) -> str:
        """Map provider-specific errors to standard exceptions and return error message"""
        error_str = str(error).lower()
        
        if "authentication" in error_str or "api key" in error_str or "auth" in error_str:
            error_type = "Authentication error"
        elif "rate limit" in error_str or "too many requests" in error_str:
            error_type = "Rate limit exceeded"
        elif "bad request" in error_str or "invalid" in error_str:
            error_type = "Invalid request"
        elif "server error" in error_str or "internal" in error_str or "unavailable" in error_str:
            error_type = "Service unavailable"
        else:
            error_type = "Provider error"
            
        return f"{error_type}: {str(error)}"


