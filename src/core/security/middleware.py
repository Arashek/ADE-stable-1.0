from typing import List, Optional, Set
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .auth import auth_manager, User

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for handling JWT authentication and public routes"""
    
    def __init__(
        self,
        app,
        public_paths: Optional[Set[str]] = None,
        exclude_paths: Optional[Set[str]] = None
    ):
        """
        Initialize the authentication middleware
        
        Args:
            app: The FastAPI application
            public_paths: Set of paths that don't require authentication
            exclude_paths: Set of paths to completely exclude from middleware processing
        """
        super().__init__(app)
        self.security = HTTPBearer()
        self.public_paths = public_paths or {
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics"
        }
        self.exclude_paths = exclude_paths or set()
        
    async def dispatch(
        self,
        request: Request,
        call_next
    ) -> Response:
        """
        Process the request and handle authentication
        
        Args:
            request: The incoming request
            call_next: The next middleware/handler in the chain
            
        Returns:
            Response: The response from the next handler
            
        Raises:
            HTTPException: If authentication fails
        """
        # Skip authentication for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
            
        # Allow public paths without authentication
        if request.url.path in self.public_paths:
            return await call_next(request)
            
        try:
            # Extract and validate the token
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(
                    status_code=401,
                    detail="No authorization header"
                )
                
            # Extract the token from the Authorization header
            try:
                scheme, token = auth_header.split()
                if scheme.lower() != "bearer":
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid authentication scheme"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authorization header format"
                )
            
            # Verify the token and get the user
            try:
                user = auth_manager.get_current_user(token)
            except HTTPException as e:
                raise HTTPException(
                    status_code=e.status_code,
                    detail=e.detail
                )
            
            # Add the authenticated user to the request state
            request.state.user = user
            
            # Process the request
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            # Re-raise HTTP exceptions
            raise e
        except Exception as e:
            # Handle unexpected errors
            raise HTTPException(
                status_code=500,
                detail="Internal server error during authentication"
            )
            
    def add_public_path(self, path: str) -> None:
        """Add a path to the public paths set"""
        self.public_paths.add(path)
        
    def add_exclude_path(self, path: str) -> None:
        """Add a path to the excluded paths set"""
        self.exclude_paths.add(path)
        
    def remove_public_path(self, path: str) -> None:
        """Remove a path from the public paths set"""
        self.public_paths.discard(path)
        
    def remove_exclude_path(self, path: str) -> None:
        """Remove a path from the excluded paths set"""
        self.exclude_paths.discard(path)
        
    def get_public_paths(self) -> Set[str]:
        """Get the current set of public paths"""
        return self.public_paths.copy()
        
    def get_exclude_paths(self) -> Set[str]:
        """Get the current set of excluded paths"""
        return self.exclude_paths.copy() 