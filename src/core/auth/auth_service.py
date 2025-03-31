from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import jwt
import bcrypt
from dataclasses import dataclass
from enum import Enum
import logging
from abc import ABC, abstractmethod
import aiohttp
import asyncio
from urllib.parse import urlencode
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    TECHNICAL_STAFF = "technical_staff"
    CUSTOMER = "customer"

@dataclass
class User:
    id: str
    email: str
    role: UserRole
    organization_id: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    metadata: Dict[str, Any]
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None

@dataclass
class TokenPayload:
    sub: str  # user_id
    role: UserRole
    org_id: str
    exp: datetime
    iat: datetime
    permissions: List[str]
    oauth_provider: Optional[str] = None

class AuthenticationProvider(ABC):
    @abstractmethod
    def authenticate(self, credentials: Dict[str, str]) -> Optional[User]:
        pass

class JWTProvider(AuthenticationProvider):
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        
    def authenticate(self, credentials: Dict[str, str]) -> Optional[User]:
        try:
            token = credentials.get("token")
            if not token:
                return None
                
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            return User(
                id=payload["sub"],
                email=payload.get("email"),
                role=UserRole(payload["role"]),
                organization_id=payload["org_id"],
                is_active=True,
                created_at=datetime.fromtimestamp(payload["iat"]),
                last_login=datetime.fromtimestamp(payload["exp"]),
                metadata=payload.get("metadata", {}),
                oauth_provider=payload.get("oauth_provider"),
                oauth_id=payload.get("oauth_id")
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {str(e)}")
            return None

class OAuthProvider(AuthenticationProvider):
    def __init__(self, client_id: str, client_secret: str, provider: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.provider = provider
        self._token_endpoints = {
            "google": "https://accounts.google.com/o/oauth2/token",
            "github": "https://github.com/login/oauth/access_token",
            "microsoft": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "slack": "https://slack.com/api/oauth.v2.access",
            "linkedin": "https://www.linkedin.com/oauth/v2/accessToken",
            "facebook": "https://graph.facebook.com/v12.0/oauth/access_token",
            "twitter": "https://api.twitter.com/2/oauth2/token",
            "discord": "https://discord.com/api/oauth2/token",
            "gitlab": "https://gitlab.com/oauth/token",
            "bitbucket": "https://bitbucket.org/site/oauth2/access_token",
            "dropbox": "https://api.dropboxapi.com/oauth2/token",
            "box": "https://api.box.com/oauth2/token",
            "salesforce": "https://login.salesforce.com/services/oauth2/token",
            "zoom": "https://zoom.us/oauth/token",
            "okta": "https://{domain}/oauth2/v1/token"
        }
        self._user_info_endpoints = {
            "google": "https://www.googleapis.com/oauth2/v3/userinfo",
            "github": "https://api.github.com/user",
            "microsoft": "https://graph.microsoft.com/v1.0/me",
            "slack": "https://slack.com/api/users.identity",
            "linkedin": "https://api.linkedin.com/v2/me",
            "facebook": "https://graph.facebook.com/v12.0/me",
            "twitter": "https://api.twitter.com/2/users/me",
            "discord": "https://discord.com/api/users/@me",
            "gitlab": "https://gitlab.com/api/v4/user",
            "bitbucket": "https://api.bitbucket.org/2.0/user",
            "dropbox": "https://api.dropboxapi.com/2/users/get_current_account",
            "box": "https://api.box.com/2.0/users/me",
            "salesforce": "https://login.salesforce.com/services/oauth2/userinfo",
            "zoom": "https://api.zoom.us/v2/users/me",
            "okta": "https://{domain}/oauth2/v1/userinfo"
        }
        self._scope_mapping = {
            "google": ["openid", "email", "profile"],
            "github": ["user:email"],
            "microsoft": ["User.Read"],
            "slack": ["identity.basic", "identity.email"],
            "linkedin": ["r_emailaddress", "r_liteprofile"],
            "facebook": ["email", "public_profile"],
            "twitter": ["tweet.read", "users.read"],
            "discord": ["identify", "email"],
            "gitlab": ["read_user", "read_api"],
            "bitbucket": ["account", "email"],
            "dropbox": ["account_info.read"],
            "box": ["root_readonly"],
            "salesforce": ["openid", "profile", "email"],
            "zoom": ["user:read:admin"],
            "okta": ["openid", "profile", "email"]
        }
        self._pkce_support = {
            "google": True,
            "github": True,
            "microsoft": True,
            "slack": True,
            "linkedin": True,
            "facebook": True,
            "twitter": True,
            "discord": True,
            "gitlab": True,
            "bitbucket": True,
            "dropbox": True,
            "box": True,
            "salesforce": True,
            "zoom": True,
            "okta": True
        }
        
    async def authenticate(self, credentials: Dict[str, str]) -> Optional[User]:
        try:
            code = credentials.get("code")
            if not code:
                return None
                
            # Exchange code for access token
            access_token = await self._exchange_code_for_token(code)
            
            # Get user info from OAuth provider
            user_info = await self._get_user_info(access_token)
            
            # Normalize user info across providers
            normalized_info = self._normalize_user_info(user_info)
            
            return User(
                id=str(uuid.uuid4()),
                email=normalized_info["email"],
                role=UserRole.CUSTOMER,  # OAuth users are always customers
                organization_id=normalized_info.get("organization_id"),
                is_active=True,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
                metadata={
                    "provider": self.provider,
                    "provider_id": normalized_info["provider_id"],
                    "name": normalized_info.get("name"),
                    "avatar": normalized_info.get("avatar"),
                    "locale": normalized_info.get("locale")
                },
                oauth_provider=self.provider,
                oauth_id=normalized_info["provider_id"]
            )
        except Exception as e:
            logger.error(f"OAuth authentication failed: {str(e)}")
            return None
            
    async def _exchange_code_for_token(self, code: str) -> str:
        """Exchange authorization code for access token."""
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost:3000/oauth/callback"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self._token_endpoints[self.provider],
                data=params
            ) as response:
                data = await response.json()
                if not response.ok:
                    raise Exception(f"Token exchange failed: {data}")
                return data["access_token"]
                
    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth provider."""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._user_info_endpoints[self.provider],
                headers=headers
            ) as response:
                data = await response.json()
                if not response.ok:
                    raise Exception(f"User info retrieval failed: {data}")
                return data
                
    def _normalize_user_info(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize user info across different providers."""
        provider_specific = {
            "google": {
                "email": user_info["email"],
                "provider_id": user_info["sub"],
                "name": user_info.get("name"),
                "avatar": user_info.get("picture"),
                "locale": user_info.get("locale")
            },
            "github": {
                "email": user_info.get("email"),
                "provider_id": str(user_info["id"]),
                "name": user_info.get("name"),
                "avatar": user_info.get("avatar_url"),
                "locale": None
            },
            "microsoft": {
                "email": user_info.get("userPrincipalName"),
                "provider_id": user_info["id"],
                "name": user_info.get("displayName"),
                "avatar": None,
                "locale": user_info.get("preferredLanguage")
            },
            "slack": {
                "email": user_info["user"]["email"],
                "provider_id": user_info["user"]["id"],
                "name": user_info["user"].get("name"),
                "avatar": user_info["user"].get("image_192"),
                "locale": None
            },
            "linkedin": {
                "email": user_info.get("emailAddress"),
                "provider_id": user_info["id"],
                "name": f"{user_info.get('localizedFirstName', '')} {user_info.get('localizedLastName', '')}".strip(),
                "avatar": None,
                "locale": user_info.get("preferredLocale")
            },
            "facebook": {
                "email": user_info.get("email"),
                "provider_id": user_info["id"],
                "name": user_info.get("name"),
                "avatar": user_info.get("picture", {}).get("data", {}).get("url"),
                "locale": user_info.get("locale")
            },
            "twitter": {
                "email": user_info.get("data", {}).get("email"),
                "provider_id": user_info.get("data", {}).get("id"),
                "name": user_info.get("data", {}).get("name"),
                "avatar": user_info.get("data", {}).get("profile_image_url"),
                "locale": None
            },
            "discord": {
                "email": user_info.get("email"),
                "provider_id": user_info["id"],
                "name": user_info.get("username"),
                "avatar": f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info.get('avatar')}.png",
                "locale": None
            },
            "gitlab": {
                "email": user_info.get("email"),
                "provider_id": str(user_info["id"]),
                "name": user_info.get("name"),
                "avatar": user_info.get("avatar_url"),
                "locale": None
            },
            "bitbucket": {
                "email": user_info.get("email"),
                "provider_id": user_info["uuid"],
                "name": user_info.get("display_name"),
                "avatar": user_info.get("links", {}).get("avatar", {}).get("href"),
                "locale": None
            },
            "dropbox": {
                "email": user_info.get("email"),
                "provider_id": user_info["account_id"],
                "name": user_info.get("name", {}).get("display_name"),
                "avatar": None,
                "locale": user_info.get("locale")
            },
            "box": {
                "email": user_info.get("login"),
                "provider_id": user_info["id"],
                "name": user_info.get("name"),
                "avatar": user_info.get("avatar_url"),
                "locale": None
            },
            "salesforce": {
                "email": user_info.get("email"),
                "provider_id": user_info["sub"],
                "name": user_info.get("name"),
                "avatar": None,
                "locale": user_info.get("locale")
            },
            "zoom": {
                "email": user_info.get("email"),
                "provider_id": user_info["id"],
                "name": user_info.get("first_name") + " " + user_info.get("last_name"),
                "avatar": user_info.get("pic_url"),
                "locale": None
            },
            "okta": {
                "email": user_info.get("email"),
                "provider_id": user_info["sub"],
                "name": user_info.get("name"),
                "avatar": None,
                "locale": user_info.get("locale")
            }
        }
        
        return provider_specific.get(self.provider, {})
        
    def get_authorization_url(self, state: str, code_verifier: str = None) -> str:
        """Generate OAuth authorization URL with PKCE support."""
        base_urls = {
            "google": "https://accounts.google.com/o/oauth2/v2/auth",
            "github": "https://github.com/login/oauth/authorize",
            "microsoft": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "slack": "https://slack.com/oauth/v2/authorize",
            "linkedin": "https://www.linkedin.com/oauth/v2/authorization",
            "facebook": "https://www.facebook.com/v12.0/dialog/oauth",
            "twitter": "https://twitter.com/i/oauth2/authorize",
            "discord": "https://discord.com/api/oauth2/authorize",
            "gitlab": "https://gitlab.com/oauth/authorize",
            "bitbucket": "https://bitbucket.org/site/oauth2/authorize",
            "dropbox": "https://www.dropbox.com/oauth2/authorize",
            "box": "https://account.box.com/api/oauth2/authorize",
            "salesforce": "https://login.salesforce.com/services/oauth2/authorize",
            "zoom": "https://zoom.us/oauth/authorize",
            "okta": "https://{domain}/oauth2/v1/authorize"
        }
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": "http://localhost:3000/oauth/callback",
            "response_type": "code",
            "scope": " ".join(self._scope_mapping[self.provider]),
            "state": state
        }
        
        # Add PKCE parameters if supported
        if self._pkce_support.get(self.provider) and code_verifier:
            code_challenge = self._generate_code_challenge(code_verifier)
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
            
        return f"{base_urls[self.provider]}?{urlencode(params)}"
        
    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate PKCE code challenge."""
        import hashlib
        import base64
        
        sha256 = hashlib.sha256(code_verifier.encode()).digest()
        return base64.urlsafe_b64encode(sha256).decode().rstrip("=")

class AuthService:
    def __init__(
        self,
        jwt_secret: str,
        oauth_config: Dict[str, Dict[str, str]],
        token_expiry: int = 3600  # 1 hour
    ):
        self.jwt_provider = JWTProvider(jwt_secret)
        self.oauth_providers = {
            provider: OAuthProvider(
                config["client_id"],
                config["client_secret"],
                provider
            )
            for provider, config in oauth_config.items()
        }
        self.token_expiry = token_expiry
        self._permission_cache: Dict[str, List[str]] = {}
        
    async def authenticate(self, credentials: Dict[str, str]) -> Optional[User]:
        """Authenticate user using appropriate provider."""
        # Try JWT first
        user = self.jwt_provider.authenticate(credentials)
        if user:
            return user
            
        # Try OAuth providers
        for provider in self.oauth_providers.values():
            user = await provider.authenticate(credentials)
            if user:
                return user
                
        return None
        
    def generate_token(self, user: User) -> str:
        """Generate JWT token for authenticated user."""
        now = datetime.utcnow()
        payload = TokenPayload(
            sub=user.id,
            role=user.role,
            org_id=user.organization_id,
            exp=now + timedelta(seconds=self.token_expiry),
            iat=now,
            permissions=self._get_user_permissions(user),
            oauth_provider=user.oauth_provider
        )
        
        return jwt.encode(
            payload.__dict__,
            self.jwt_provider.secret_key,
            algorithm=self.jwt_provider.algorithm
        )
        
    def validate_token(self, token: str) -> Optional[TokenPayload]:
        """Validate JWT token and return payload."""
        try:
            payload = jwt.decode(
                token,
                self.jwt_provider.secret_key,
                algorithms=[self.jwt_provider.algorithm]
            )
            return TokenPayload(**payload)
        except jwt.InvalidTokenError as e:
            logger.error(f"Token validation failed: {str(e)}")
            return None
            
    def _get_user_permissions(self, user: User) -> List[str]:
        """Get user permissions based on role."""
        if user.id in self._permission_cache:
            return self._permission_cache[user.id]
            
        permissions = self._calculate_permissions(user.role)
        self._permission_cache[user.id] = permissions
        return permissions
        
    def _calculate_permissions(self, role: UserRole) -> List[str]:
        """Calculate permissions based on role hierarchy."""
        base_permissions = {
            UserRole.OWNER: [
                "manage_organization",
                "manage_users",
                "manage_roles",
                "manage_permissions",
                "manage_billing",
                "view_analytics",
                "manage_infrastructure",
                "manage_teams",
                "manage_integrations",
                "manage_api_keys",
                "view_audit_logs",
                "manage_subscriptions"
            ],
            UserRole.ADMIN: [
                "manage_users",
                "manage_roles",
                "view_analytics",
                "manage_billing",
                "manage_teams",
                "view_audit_logs",
                "manage_api_keys"
            ],
            UserRole.TECHNICAL_STAFF: [
                "view_analytics",
                "manage_infrastructure",
                "view_logs",
                "manage_api_keys",
                "view_audit_logs"
            ],
            UserRole.CUSTOMER: [
                "view_own_data",
                "manage_own_profile",
                "view_own_analytics",
                "manage_own_api_keys"
            ]
        }
        
        # Get base permissions for role
        permissions = base_permissions.get(role, [])
        
        # Add inherited permissions from lower roles
        if role == UserRole.OWNER:
            permissions.extend(base_permissions[UserRole.ADMIN])
            permissions.extend(base_permissions[UserRole.TECHNICAL_STAFF])
            permissions.extend(base_permissions[UserRole.CUSTOMER])
        elif role == UserRole.ADMIN:
            permissions.extend(base_permissions[UserRole.TECHNICAL_STAFF])
            permissions.extend(base_permissions[UserRole.CUSTOMER])
        elif role == UserRole.TECHNICAL_STAFF:
            permissions.extend(base_permissions[UserRole.CUSTOMER])
            
        return list(set(permissions))  # Remove duplicates
        
    def has_permission(self, user: User, permission: str) -> bool:
        """Check if user has specific permission."""
        permissions = self._get_user_permissions(user)
        return permission in permissions
        
    def require_permission(self, permission: str):
        """Decorator to require specific permission."""
        def decorator(func):
            def wrapper(self, user: User, *args, **kwargs):
                if not self.has_permission(user, permission):
                    raise PermissionError(
                        f"User {user.id} does not have permission: {permission}"
                    )
                return func(self, user, *args, **kwargs)
            return wrapper
        return decorator
        
    def clear_permission_cache(self, user_id: str):
        """Clear permission cache for user."""
        self._permission_cache.pop(user_id, None)
        
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh expired token if possible."""
        payload = self.validate_token(token)
        if not payload:
            return None
            
        # Check if token is expired but within refresh window
        now = datetime.utcnow()
        if payload.exp < now and (now - payload.exp).total_seconds() < 300:  # 5 minutes
            user = User(
                id=payload.sub,
                email="",  # Not needed for token refresh
                role=payload.role,
                organization_id=payload.org_id,
                is_active=True,
                created_at=payload.iat,
                last_login=now,
                metadata={},
                oauth_provider=payload.oauth_provider
            )
            return self.generate_token(user)
            
        return None 