"""
Validation Middleware for ADE Platform APIs

This module provides middleware components for FastAPI that enhance request and
response validation, improve error handling, and add detailed logging for validation errors.
"""

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError
import logging
import json
import traceback
import time
from typing import Callable, Dict, Any, Optional, Union, Type
from datetime import datetime
import uuid

# Try to import error logging system
try:
    # Corrected import path
    from utils.error_logging import log_error, ErrorCategory, ErrorSeverity
    from models.api_models import ErrorCategory as ModelErrorCategory
    from models.api_models import ErrorSeverity as ModelErrorSeverity
    
    # Map model enums to error logging enums
    def map_category(category: ModelErrorCategory) -> str:
        return getattr(ErrorCategory, category.value, ErrorCategory.UNKNOWN)
    
    def map_severity(severity: ModelErrorSeverity) -> str:
        return getattr(ErrorSeverity, severity.value, ErrorSeverity.ERROR)
    
    error_logging_available = True
except ImportError:
    error_logging_available = False
    
    # Define fallback error categories and severities if import fails
    class ErrorCategory:
        VALIDATION = "VALIDATION"
        API = "API"
        UNKNOWN = "UNKNOWN"
    
    class ErrorSeverity:
        ERROR = "ERROR"
        WARNING = "WARNING"
    
    # Dummy mapping functions
    def map_category(category: Any) -> str:
        return getattr(ErrorCategory, "VALIDATION", ErrorCategory.UNKNOWN)
    
    def map_severity(severity: Any) -> str:
        return getattr(ErrorSeverity, "ERROR", ErrorSeverity.ERROR)

# Configure logging
logger = logging.getLogger(__name__)


class ValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for enhancing request and response validation.
    
    Features:
    - Detailed validation error handling
    - Request and response timing
    - Error logging integration
    - Standardized error response format
    """
    
    def __init__(
        self, 
        app,
        exclude_paths: Optional[list] = None,
        log_request_body: bool = False,
        log_response_body: bool = False
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip middleware for excluded paths
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                return await call_next(request)
        
        # Initialize request metadata
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Add request ID to request state for downstream access
        request.state.request_id = request_id
        
        # Prepare context for error logging
        context = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else "unknown",
            "headers": dict(request.headers) if hasattr(request, "headers") else {}
        }
        
        # Remove sensitive headers from logging
        sensitive_headers = ["authorization", "cookie", "x-api-key"]
        for header in sensitive_headers:
            if header in context["headers"]:
                context["headers"][header] = "[REDACTED]"
        
        # Log request body if enabled
        if self.log_request_body:
            try:
                # Clone the request body for logging
                body_bytes = await request.body()
                
                # Store the body so it can be read again by request handlers
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                
                request._receive = receive
                
                # Try to parse and log the body
                try:
                    body = json.loads(body_bytes)
                    # Redact sensitive fields
                    if isinstance(body, dict):
                        for key in ["password", "token", "secret", "key"]:
                            if key in body:
                                body[key] = "[REDACTED]"
                    context["request_body"] = body
                except json.JSONDecodeError:
                    context["request_body"] = "[BINARY OR INVALID JSON]"
            except Exception as e:
                logger.warning(f"Failed to capture request body: {str(e)}")
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Add timing headers
            response.headers["X-Response-Time"] = str(response_time)
            response.headers["X-Request-ID"] = request_id
            
            # Log response body if enabled and response is JSON
            if self.log_response_body and response.headers.get("content-type") == "application/json":
                try:
                    body = response.body
                    response_data = json.loads(body)
                    context["response_body"] = response_data
                    context["response_status"] = response.status_code
                except Exception as e:
                    logger.warning(f"Failed to capture response body: {str(e)}")
            
            return response
            
        except ValidationError as e:
            # Handle Pydantic validation errors
            return self._handle_validation_error(e, context, request_id, start_time)
            
        except Exception as e:
            # Handle other exceptions
            return self._handle_exception(e, context, request_id, start_time)
    
    def _handle_validation_error(
        self, 
        exc: ValidationError, 
        context: Dict[str, Any],
        request_id: str,
        start_time: float
    ) -> JSONResponse:
        """Handle Pydantic validation errors"""
        # Format validation errors
        errors = []
        for error in exc.errors():
            errors.append({
                "loc": error.get("loc", []),
                "msg": error.get("msg", ""),
                "type": error.get("type", "")
            })
        
        # Create error response
        error_detail = {
            "success": False,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "error": "Validation Error",
            "detail": errors
        }
        
        # Log the validation error
        error_msg = f"Validation error: {str(exc)}"
        context["validation_errors"] = errors
        
        if error_logging_available:
            try:
                error_id = log_error(
                    error=error_msg,
                    category=ErrorCategory.VALIDATION,
                    severity=ErrorSeverity.WARNING,
                    component="api",
                    source="validation_middleware",
                    context=context
                )
                error_detail["error_id"] = error_id
            except Exception as log_error:
                logger.error(f"Failed to log validation error: {str(log_error)}")
        
        # Log using standard logging
        logger.warning(f"Request validation failed: {error_msg}")
        
        # Add timing
        response_time = time.time() - start_time
        
        # Return formatted response
        response = JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_detail
        )
        response.headers["X-Response-Time"] = str(response_time)
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    def _handle_exception(
        self, 
        exc: Exception, 
        context: Dict[str, Any],
        request_id: str,
        start_time: float
    ) -> JSONResponse:
        """Handle generic exceptions"""
        # Get exception details
        error_msg = str(exc)
        error_type = exc.__class__.__name__
        stack_trace = traceback.format_exc()
        
        # Create error response
        error_detail = {
            "success": False,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "error": error_type,
            "detail": error_msg
        }
        
        # Update context
        context["error_type"] = error_type
        context["stack_trace"] = stack_trace
        
        # Log the error
        if error_logging_available:
            try:
                error_id = log_error(
                    error=exc,
                    category=ErrorCategory.API,
                    severity=ErrorSeverity.ERROR,
                    component="api",
                    source="validation_middleware",
                    context=context
                )
                error_detail["error_id"] = error_id
            except Exception as log_error:
                logger.error(f"Failed to log exception: {str(log_error)}")
        
        # Log using standard logging
        logger.error(f"Unhandled exception in request: {error_msg}", exc_info=True)
        
        # Add timing
        response_time = time.time() - start_time
        
        # Return formatted response
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_detail
        )
        response.headers["X-Response-Time"] = str(response_time)
        response.headers["X-Request-ID"] = request_id
        
        return response


class ResponseValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for validating API responses against expected Pydantic models.
    
    This middleware can be used to ensure that API responses conform to their
    specified response models, catching any inconsistencies before they reach clients.
    """
    
    def __init__(
        self, 
        app,
        debug_mode: bool = False,
        exclude_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.debug_mode = debug_mode
        self.exclude_paths = exclude_paths or []
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip middleware for excluded paths
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                return await call_next(request)
        
        # Process the request normally
        response = await call_next(request)
        
        # Only validate JSON responses in debug mode
        if self.debug_mode and response.headers.get("content-type") == "application/json":
            # Get the route and response model
            route = request.scope.get("route")
            if route and hasattr(route, "response_model"):
                response_model = route.response_model
                
                if response_model:
                    # Read response body
                    body = await response.body()
                    
                    try:
                        # Parse response data
                        response_data = json.loads(body)
                        
                        # Validate against response model
                        try:
                            response_model.parse_obj(response_data)
                        except ValidationError as e:
                            # Log the validation error but still return the original response
                            logger.error(
                                f"Response validation failed for {request.url.path}: {str(e)}"
                            )
                            
                            # In debug mode, we can modify the response to include validation errors
                            if self.debug_mode:
                                # Create a new response with validation error details
                                error_response = {
                                    "original_response": response_data,
                                    "validation_errors": e.errors(),
                                    "_debug_info": {
                                        "expected_model": response_model.__name__,
                                        "endpoint": request.url.path,
                                        "method": request.method
                                    }
                                }
                                
                                return JSONResponse(
                                    status_code=response.status_code,
                                    content=error_response,
                                    headers=dict(response.headers)
                                )
                    except json.JSONDecodeError:
                        # Not a valid JSON response
                        logger.warning(f"Could not validate non-JSON response for {request.url.path}")
        
        return response


# Function to add middleware to FastAPI app
def add_validation_middleware(app, debug_mode: bool = False):
    """
    Add validation middleware to a FastAPI application
    
    Args:
        app: The FastAPI application
        debug_mode: Whether to run in debug mode with extra validation
    """
    # Add request validation middleware
    app.add_middleware(
        ValidationMiddleware,
        exclude_paths=["/docs", "/redoc", "/openapi.json", "/static", "/health"],
        log_request_body=debug_mode,
        log_response_body=debug_mode
    )
    
    # Optionally add response validation in debug mode
    if debug_mode:
        app.add_middleware(
            ResponseValidationMiddleware,
            debug_mode=True,
            exclude_paths=["/docs", "/redoc", "/openapi.json", "/static", "/health"]
        )
