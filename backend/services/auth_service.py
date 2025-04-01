"""
Authentication Service for ADE Platform

This module provides authentication and authorization services.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        """Initialize the authentication service"""
        logger.info("Initializing AuthService")
        self.enabled = True
    
    async def get_current_user(self, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the current user based on token.
        
        Args:
            token: Authentication token
            
        Returns:
            Dictionary containing user information
        """
        # For local development, return a default user
        return {
            "id": "local-dev-user",
            "username": "local-dev",
            "email": "dev@example.com",
            "is_active": True,
            "is_superuser": True
        }
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User information if authentication is successful, None otherwise
        """
        # For local development, return a default user for any credentials
        return {
            "id": "local-dev-user",
            "username": username,
            "email": f"{username}@example.com",
            "is_active": True,
            "is_superuser": True
        }
    
    async def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create an access token.
        
        Args:
            data: Data to encode in the token
            
        Returns:
            Access token
        """
        # For local development, return a dummy token
        return "local-dev-token"

# Create singleton instance
auth_service = AuthService()
