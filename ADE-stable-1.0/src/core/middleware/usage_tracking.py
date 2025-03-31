from typing import Callable, Optional
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.core.services.usage_tracking import UsageTrackingService
from src.storage.document.models.usage import UsageType
from src.core.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)

class UsageTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking API usage"""
    
    def __init__(
        self,
        app: ASGIApp,
        usage_service: UsageTrackingService,
        provider_registry: ProviderRegistry
    ):
        super().__init__(app)
        self.usage_service = usage_service
        self.provider_registry = provider_registry
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process the request and track usage"""
        # Skip tracking for non-API routes
        if not request.url.path.startswith("/api/"):
            return await call_next(request)
        
        # Get user from request state
        user = getattr(request.state, "user", None)
        if not user:
            return await call_next(request)
        
        # Get provider and model from request
        provider = request.query_params.get("provider")
        model = request.query_params.get("model")
        
        if not provider or not model:
            return await call_next(request)
        
        # Get usage type from request path
        usage_type = self._get_usage_type(request.url.path)
        if not usage_type:
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        
        try:
            # Check quota limits
            if not await self.usage_service.check_quota_limits(
                user.id,
                usage_type,
                tokens=1  # Minimum token count for check
            ):
                return Response(
                    status_code=429,
                    content="Quota limit exceeded"
                )
            
            # Process request
            response = await call_next(request)
            
            # Calculate tokens and cost
            tokens_used = self._calculate_tokens(response)
            cost = self._calculate_cost(provider, model, tokens_used)
            
            # Record usage
            await self.usage_service.record_usage(
                user_id=user.id,
                provider=provider,
                model=model,
                usage_type=usage_type,
                tokens_used=tokens_used,
                cost=cost,
                status="success",
                project_id=request.query_params.get("project_id"),
                metadata={
                    "path": request.url.path,
                    "method": request.method,
                    "response_time": time.time() - start_time,
                    "status_code": response.status_code
                }
            )
            
            return response
            
        except Exception as e:
            # Record failed usage
            await self.usage_service.record_usage(
                user_id=user.id,
                provider=provider,
                model=model,
                usage_type=usage_type,
                tokens_used=0,
                cost=0,
                status="failure",
                project_id=request.query_params.get("project_id"),
                error_message=str(e),
                metadata={
                    "path": request.url.path,
                    "method": request.method,
                    "response_time": time.time() - start_time
                }
            )
            raise
    
    def _get_usage_type(self, path: str) -> Optional[UsageType]:
        """Determine usage type from request path"""
        path = path.lower()
        
        if "/text/" in path:
            return UsageType.TEXT_GENERATION
        elif "/code/" in path:
            return UsageType.CODE_GENERATION
        elif "/embedding/" in path:
            return UsageType.EMBEDDING
        elif "/vision/" in path:
            return UsageType.VISION
        elif "/audio/" in path:
            return UsageType.AUDIO
        
        return None
    
    def _calculate_tokens(self, response: Response) -> int:
        """Calculate tokens used from response"""
        try:
            # Get token count from response headers
            token_count = response.headers.get("X-Token-Count")
            if token_count:
                return int(token_count)
            
            # If not in headers, estimate from content length
            content_length = len(response.body)
            return max(1, content_length // 4)  # Rough estimate: 1 token per 4 characters
            
        except Exception as e:
            logger.error(f"Error calculating tokens: {str(e)}")
            return 1  # Minimum token count
    
    def _calculate_cost(
        self,
        provider: str,
        model: str,
        tokens: int
    ) -> float:
        """Calculate cost based on provider and model"""
        try:
            # Get provider adapter
            adapter = self.provider_registry.get_provider(provider)
            if not adapter:
                return 0.0
            
            # Get model pricing
            pricing = adapter.get_model_pricing(model)
            if not pricing:
                return 0.0
            
            # Calculate cost
            input_cost = (tokens * pricing.input_price) / 1000  # Price per 1K tokens
            output_cost = (tokens * pricing.output_price) / 1000
            
            return input_cost + output_cost
            
        except Exception as e:
            logger.error(f"Error calculating cost: {str(e)}")
            return 0.0 