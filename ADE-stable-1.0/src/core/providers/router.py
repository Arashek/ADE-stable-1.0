import logging
from typing import Dict, List, Any, Optional, TYPE_CHECKING
from .config import Capability
from .response import ProviderResponse, TextResponse, ImageResponse, PlanResponse

if TYPE_CHECKING:
    from .registry import ProviderRegistry
    from .adapters.base import BaseProviderAdapter

logger = logging.getLogger(__name__)

class ModelRouter:
    """Routes requests to appropriate providers based on capabilities"""
    
    def __init__(self, registry: 'ProviderRegistry'):
        self.registry = registry
    
    def route_text_generation(self, prompt: str, **kwargs) -> TextResponse:
        """Route a text generation request to the best provider"""
        providers = self.registry.get_providers_for_capability(Capability.TEXT_GENERATION)
        
        if not providers:
            logger.error("No providers available for text generation")
            return TextResponse(
                success=False,
                error="No providers available for text generation",
                text="",
                provider="none"
            )
        
        # Try providers in order until one succeeds
        errors = []
        for provider_name, confidence in providers:
            adapter = self.registry.get_adapter(provider_name)
            if not adapter:
                continue
                
            try:
                logger.info(f"Attempting text generation with provider: {provider_name}")
                result = adapter.generate_text(prompt, **kwargs)
                
                if isinstance(result, TextResponse):
                    if result.success:
                        logger.info(f"Successfully generated text with provider: {provider_name}")
                        return result
                    else:
                        errors.append(f"{provider_name}: {result.error}")
                else:
                    errors.append(f"{provider_name}: Invalid response type")
                    
            except Exception as e:
                logger.error(f"Error with provider {provider_name}: {str(e)}")
                errors.append(f"{provider_name}: {str(e)}")
        
        # If we get here, all providers failed
        error_msg = "All providers failed: " + "; ".join(errors)
        logger.error(error_msg)
        return TextResponse(
            success=False,
            error=error_msg,
            text="",
            provider="none"
        )
    
    def route_code_generation(self, spec: str, **kwargs) -> TextResponse:
        """Route a code generation request to the best provider"""
        providers = self.registry.get_providers_for_capability(Capability.CODE_GENERATION)
        
        if not providers:
            logger.error("No providers available for code generation")
            return TextResponse(
                success=False,
                error="No providers available for code generation",
                text="",
                provider="none"
            )
        
        # Try providers in order until one succeeds
        errors = []
        for provider_name, confidence in providers:
            adapter = self.registry.get_adapter(provider_name)
            if not adapter:
                continue
                
            try:
                logger.info(f"Attempting code generation with provider: {provider_name}")
                result = adapter.generate_code(spec, **kwargs)
                
                if isinstance(result, TextResponse):
                    if result.success:
                        logger.info(f"Successfully generated code with provider: {provider_name}")
                        return result
                    else:
                        errors.append(f"{provider_name}: {result.error}")
                else:
                    errors.append(f"{provider_name}: Invalid response type")
                    
            except Exception as e:
                logger.error(f"Error with provider {provider_name}: {str(e)}")
                errors.append(f"{provider_name}: {str(e)}")
        
        # If we get here, all providers failed
        error_msg = "All providers failed: " + "; ".join(errors)
        logger.error(error_msg)
        return TextResponse(
            success=False,
            error=error_msg,
            text="",
            provider="none"
        )
    
    def route_image_analysis(self, image_data: bytes, prompt: str, **kwargs) -> TextResponse:
        """Route an image analysis request to the best provider"""
        providers = self.registry.get_providers_for_capability(Capability.IMAGE_ANALYSIS)
        
        if not providers:
            logger.error("No providers available for image analysis")
            return TextResponse(
                success=False,
                error="No providers available for image analysis",
                text="",
                provider="none"
            )
        
        # Try providers in order until one succeeds
        errors = []
        for provider_name, confidence in providers:
            adapter = self.registry.get_adapter(provider_name)
            if not adapter:
                continue
                
            try:
                logger.info(f"Attempting image analysis with provider: {provider_name}")
                result = adapter.analyze_image(image_data, prompt, **kwargs)
                
                if isinstance(result, TextResponse):
                    if result.success:
                        logger.info(f"Successfully analyzed image with provider: {provider_name}")
                        return result
                    else:
                        errors.append(f"{provider_name}: {result.error}")
                else:
                    errors.append(f"{provider_name}: Invalid response type")
                    
            except Exception as e:
                logger.error(f"Error with provider {provider_name}: {str(e)}")
                errors.append(f"{provider_name}: {str(e)}")
        
        # If we get here, all providers failed
        error_msg = "All providers failed: " + "; ".join(errors)
        logger.error(error_msg)
        return TextResponse(
            success=False,
            error=error_msg,
            text="",
            provider="none"
        )
    
    def route_plan_creation(self, goal: str, **kwargs) -> PlanResponse:
        """Route a plan creation request to the best provider"""
        providers = self.registry.get_providers_for_capability(Capability.PLAN_CREATION)
        
        if not providers:
            logger.error("No providers available for plan creation")
            return PlanResponse(
                success=False,
                error="No providers available for plan creation",
                plan={},
                provider="none"
            )
        
        # Try providers in order until one succeeds
        errors = []
        for provider_name, confidence in providers:
            adapter = self.registry.get_adapter(provider_name)
            if not adapter:
                continue
                
            try:
                logger.info(f"Attempting plan creation with provider: {provider_name}")
                result = adapter.create_plan(goal, **kwargs)
                
                if isinstance(result, PlanResponse):
                    if result.success:
                        logger.info(f"Successfully created plan with provider: {provider_name}")
                        return result
                    else:
                        errors.append(f"{provider_name}: {result.error}")
                else:
                    errors.append(f"{provider_name}: Invalid response type")
                    
            except Exception as e:
                logger.error(f"Error with provider {provider_name}: {str(e)}")
                errors.append(f"{provider_name}: {str(e)}")
        
        # If we get here, all providers failed
        error_msg = "All providers failed: " + "; ".join(errors)
        logger.error(error_msg)
        return PlanResponse(
            success=False,
            error=error_msg,
            plan={},
            provider="none"
        )


