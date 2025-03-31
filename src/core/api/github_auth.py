from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from ..models.user import User
from ..auth import get_current_user
from ..integrations.github import github_client
from ..utils.events import EventType, event_emitter

router = APIRouter(prefix="/api/github/auth", tags=["github-auth"])

class TokenResponse(BaseModel):
    """Response model for token operations."""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    scope: Optional[str] = None

class TokenValidationResponse(BaseModel):
    """Response model for token validation."""
    valid: bool
    scopes: Optional[list] = None
    expires_at: Optional[str] = None

@router.get("/oauth/authorize")
async def authorize_github(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Initiate GitHub OAuth flow.
    
    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        
    Returns:
        OAuth authorization URL
    """
    try:
        # Generate state for CSRF protection
        state = github_client.generate_oauth_state(current_user.id)
        
        # Get authorization URL
        auth_url = github_client.get_oauth_authorization_url(
            state=state,
            redirect_uri=str(request.url_for("github_oauth_callback"))
        )
        
        return {"authorization_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initiating OAuth flow: {str(e)}"
        )

@router.get("/oauth/callback")
async def github_oauth_callback(
    code: str,
    state: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Handle GitHub OAuth callback.
    
    Args:
        code: OAuth authorization code
        state: OAuth state for CSRF protection
        request: FastAPI request object
        current_user: Current authenticated user
        
    Returns:
        Token information
    """
    try:
        # Validate state
        if not github_client.validate_oauth_state(state, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OAuth state"
            )
        
        # Exchange code for token
        token_info = await github_client.exchange_oauth_code(code)
        
        # Store token for user
        await github_client.store_user_token(current_user.id, token_info)
        
        # Emit event
        event_emitter.emit(EventType.GITHUB_TOKEN_CREATED, {
            "user_id": current_user.id,
            "scopes": token_info.get("scope", "").split()
        })
        
        return TokenResponse(**token_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error completing OAuth flow: {str(e)}"
        )

@router.post("/token", response_model=TokenResponse)
async def create_personal_token(
    scopes: list[str],
    current_user: User = Depends(get_current_user)
):
    """Create a GitHub personal access token.
    
    Args:
        scopes: List of requested scopes
        current_user: Current authenticated user
        
    Returns:
        Token information
    """
    try:
        token_info = await github_client.create_personal_token(
            current_user.id,
            scopes
        )
        
        # Emit event
        event_emitter.emit(EventType.GITHUB_TOKEN_CREATED, {
            "user_id": current_user.id,
            "scopes": scopes
        })
        
        return TokenResponse(**token_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating personal token: {str(e)}"
        )

@router.get("/token/validate", response_model=TokenValidationResponse)
async def validate_token(
    current_user: User = Depends(get_current_user)
):
    """Validate current GitHub token.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Token validation status
    """
    try:
        validation = await github_client.validate_token(current_user.id)
        return TokenValidationResponse(**validation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating token: {str(e)}"
        )

@router.delete("/token")
async def revoke_token(
    current_user: User = Depends(get_current_user)
):
    """Revoke current GitHub token.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success status
    """
    try:
        await github_client.revoke_token(current_user.id)
        
        # Emit event
        event_emitter.emit(EventType.GITHUB_TOKEN_REVOKED, {
            "user_id": current_user.id
        })
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error revoking token: {str(e)}"
        ) 