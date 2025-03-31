from typing import Dict, Any, Optional, Callable
import logging
from fastapi import Request, Response, HTTPException
from pydantic import BaseModel, ValidationError
from datetime import datetime

logger = logging.getLogger(__name__)

class ValidationErrorResponse(BaseModel):
    """Standard error response for validation failures"""
    error: str
    details: Dict[str, Any]
    timestamp: datetime

class ValidationMiddleware:
    """Middleware for API request/response validation"""
    
    def __init__(
        self,
        request_schemas: Dict[str, BaseModel],
        response_schemas: Dict[str, BaseModel],
        error_handler: Optional[Callable] = None
    ):
        self.request_schemas = request_schemas
        self.response_schemas = response_schemas
        self.error_handler = error_handler or self._default_error_handler
    
    async def __call__(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process request and validate against schemas"""
        try:
            # Get endpoint path
            path = request.url.path
            
            # Validate request if schema exists
            if path in self.request_schemas:
                await self._validate_request(request, path)
            
            # Process request
            response = await call_next(request)
            
            # Validate response if schema exists
            if path in self.response_schemas:
                await self._validate_response(response, path)
            
            return response
            
        except ValidationError as e:
            return await self.error_handler(request, e)
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return await self.error_handler(request, e)
    
    async def _validate_request(self, request: Request, path: str) -> None:
        """Validate request body against schema"""
        schema = self.request_schemas[path]
        
        # Get request body
        body = await request.json()
        
        # Validate against schema
        try:
            schema(**body)
        except ValidationError as e:
            logger.warning(f"Request validation failed for {path}: {str(e)}")
            raise
    
    async def _validate_response(self, response: Response, path: str) -> None:
        """Validate response body against schema"""
        schema = self.response_schemas[path]
        
        # Get response body
        body = await response.json()
        
        # Validate against schema
        try:
            schema(**body)
        except ValidationError as e:
            logger.warning(f"Response validation failed for {path}: {str(e)}")
            raise
    
    async def _default_error_handler(
        self,
        request: Request,
        error: Exception
    ) -> Response:
        """Default error handler for validation failures"""
        error_response = ValidationErrorResponse(
            error=str(error),
            details={"path": request.url.path},
            timestamp=datetime.now()
        )
        
        return Response(
            content=error_response.json(),
            status_code=400,
            media_type="application/json"
        ) 