from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security configuration
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(str, Enum):
    """Predefined user roles with associated permissions"""
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"

@dataclass
class User:
    """User model with authentication and authorization attributes"""
    username: str
    password_hash: str
    roles: List[UserRole]
    api_key: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    last_login: Optional[datetime] = None

class TokenPayload:
    """JWT token payload structure"""
    def __init__(
        self,
        sub: str,
        roles: List[str],
        exp: Optional[datetime] = None
    ):
        self.sub = sub
        self.roles = roles
        self.exp = exp or datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    def to_dict(self) -> Dict[str, Any]:
        """Convert payload to dictionary for JWT encoding"""
        return {
            "sub": self.sub,
            "roles": self.roles,
            "exp": self.exp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenPayload':
        """Create payload from dictionary"""
        return cls(
            sub=data["sub"],
            roles=data["roles"],
            exp=datetime.fromtimestamp(data["exp"])
        )

class AuthManager:
    """Manages authentication and authorization operations"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.security = HTTPBearer()

    def create_user(
        self,
        username: str,
        password: str,
        roles: List[UserRole],
        api_key: Optional[str] = None
    ) -> User:
        """Create a new user with hashed password"""
        if username in self.users:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        user = User(
            username=username,
            password_hash=self.hash_password(password),
            roles=roles,
            api_key=api_key
        )
        self.users[username] = user
        return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password"""
        user = self.users.get(username)
        if not user or not self.verify_password(password, user.password_hash):
            return None
        return user

    def create_access_token(self, user: User) -> str:
        """Generate a JWT access token for a user"""
        payload = TokenPayload(
            sub=user.username,
            roles=[role.value for role in user.roles]
        )
        return jwt.encode(payload.to_dict(), SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> TokenPayload:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return TokenPayload.from_dict(payload)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())
    ) -> User:
        """Get the current user from the JWT token"""
        payload = self.verify_token(credentials.credentials)
        user = self.users.get(payload.sub)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

    def check_permissions(
        self,
        user: User,
        required_roles: List[UserRole]
    ) -> bool:
        """Check if a user has the required roles"""
        return any(role in user.roles for role in required_roles)

    def require_roles(
        self,
        required_roles: List[UserRole]
    ) -> Depends:
        """Dependency for checking role-based permissions"""
        async def role_checker(user: User = Depends(self.get_current_user)):
            if not self.check_permissions(user, required_roles):
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )
            return user
        return Depends(role_checker)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """Get a user by their API key"""
        for user in self.users.values():
            if user.api_key == api_key:
                return user
        return None

    def authenticate_api_key(
        self,
        api_key: str = Security(HTTPBearer())
    ) -> User:
        """Authenticate a request using an API key"""
        user = self.get_user_by_api_key(api_key.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return user

# Create a global instance of the auth manager
auth_manager = AuthManager() 