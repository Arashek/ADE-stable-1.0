from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import logging
from datetime import datetime

from src.core.config import settings
from src.core.models.user import User
from src.core.services.user_service import UserService

logger = logging.getLogger(__name__)
security = HTTPBearer()

class AuthMiddleware:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def __call__(self, request: Request, call_next):
        try:
            # Skip authentication for public endpoints
            if request.url.path in ["/api/auth/login", "/api/auth/register"]:
                return await call_next(request)

            # Get JWT token from Authorization header
            credentials: HTTPAuthorizationCredentials = await security(request)
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No authorization token provided"
                )

            token = credentials.credentials
            try:
                # Verify and decode JWT token
                payload = jwt.decode(
                    token,
                    settings.JWT_SECRET_KEY,
                    algorithms=[settings.JWT_ALGORITHM]
                )
                
                # Extract user information
                user_id: str = payload.get("sub")
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token payload"
                    )

                # Get user from database
                user = await self.user_service.get_user(user_id)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found"
                    )

                # Check if token is expired
                exp = payload.get("exp")
                if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has expired"
                    )

                # Add user to request state for use in route handlers
                request.state.user = user

                # Log successful authentication
                logger.info(
                    f"User {user_id} authenticated successfully for {request.method} {request.url.path}"
                )

                return await call_next(request)

            except JWTError as e:
                logger.error(f"JWT validation failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )

        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail}
            )
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error during authentication"}
            )

def require_permissions(*required_permissions: str):
    async def permission_checker(request: Request):
        user: User = request.state.user
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )

        # Check if user has all required permissions
        user_permissions = set(user.permissions)
        required_permissions_set = set(required_permissions)
        
        if not required_permissions_set.issubset(user_permissions):
            missing_permissions = required_permissions_set - user_permissions
            logger.warning(
                f"User {user.id} missing required permissions: {missing_permissions}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(missing_permissions)}"
            )

        return True

    return permission_checker 