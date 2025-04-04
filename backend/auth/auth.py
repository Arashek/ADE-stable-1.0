from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from models.management_components import User, Role, Permission
from database.management_db import ManagementDB
import logging

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = "your-secret-key-here"  # Replace with environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthManager:
    def __init__(self):
        self.db = ManagementDB()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        try:
            user = await self.db.get_user_by_username(username)
            if not user:
                return None
            if not self.verify_password(password, user.hashed_password):
                return None
            return user
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        """Get current user from token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except jwt.JWTError:
            raise credentials_exception
        
        user = await self.db.get_user_by_username(username)
        if user is None:
            raise credentials_exception
        return user

    async def get_current_active_user(self, current_user: User = Depends(get_current_user)) -> User:
        """Get current active user"""
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

    async def check_permissions(self, user: User, required_permissions: List[str]) -> bool:
        """Check if user has required permissions"""
        try:
            user_roles = await self.db.get_user_roles(user.id)
            user_permissions = set()
            
            for role in user_roles:
                role_permissions = await self.db.get_role_permissions(role.id)
                user_permissions.update(role_permissions)
            
            return all(permission in user_permissions for permission in required_permissions)
        except Exception as e:
            logger.error(f"Error checking permissions: {str(e)}")
            return False

    async def require_permissions(self, required_permissions: List[str]):
        """Dependency for checking required permissions"""
        async def permission_checker(current_user: User = Depends(get_current_active_user)):
            has_permissions = await self.check_permissions(current_user, required_permissions)
            if not has_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return current_user
        return permission_checker

    async def create_user(self, username: str, password: str, email: str, full_name: str) -> User:
        """Create a new user"""
        try:
            hashed_password = self.get_password_hash(password)
            user_data = {
                "username": username,
                "hashed_password": hashed_password,
                "email": email,
                "full_name": full_name,
                "is_active": True,
                "is_superuser": False
            }
            user = await self.db.create_user(user_data)
            return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> User:
        """Update user information"""
        try:
            if "password" in user_data:
                user_data["hashed_password"] = self.get_password_hash(user_data.pop("password"))
            user = await self.db.update_user(user_id, user_data)
            return user
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        try:
            return await self.db.delete_user(user_id)
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise

    async def assign_role(self, user_id: str, role_id: str) -> bool:
        """Assign a role to a user"""
        try:
            return await self.db.assign_role_to_user(user_id, role_id)
        except Exception as e:
            logger.error(f"Error assigning role: {str(e)}")
            raise

    async def remove_role(self, user_id: str, role_id: str) -> bool:
        """Remove a role from a user"""
        try:
            return await self.db.remove_role_from_user(user_id, role_id)
        except Exception as e:
            logger.error(f"Error removing role: {str(e)}")
            raise

    async def create_role(self, name: str, description: str, permissions: List[str]) -> Role:
        """Create a new role"""
        try:
            role_data = {
                "name": name,
                "description": description,
                "permissions": permissions
            }
            role = await self.db.create_role(role_data)
            return role
        except Exception as e:
            logger.error(f"Error creating role: {str(e)}")
            raise

    async def update_role(self, role_id: str, role_data: Dict[str, Any]) -> Role:
        """Update role information"""
        try:
            role = await self.db.update_role(role_id, role_data)
            return role
        except Exception as e:
            logger.error(f"Error updating role: {str(e)}")
            raise

    async def delete_role(self, role_id: str) -> bool:
        """Delete a role"""
        try:
            return await self.db.delete_role(role_id)
        except Exception as e:
            logger.error(f"Error deleting role: {str(e)}")
            raise

    async def create_permission(self, name: str, description: str, resource_type: str, actions: List[str]) -> Permission:
        """Create a new permission"""
        try:
            permission_data = {
                "name": name,
                "description": description,
                "resource_type": resource_type,
                "actions": actions
            }
            permission = await self.db.create_permission(permission_data)
            return permission
        except Exception as e:
            logger.error(f"Error creating permission: {str(e)}")
            raise

    async def update_permission(self, permission_id: str, permission_data: Dict[str, Any]) -> Permission:
        """Update permission information"""
        try:
            permission = await self.db.update_permission(permission_id, permission_data)
            return permission
        except Exception as e:
            logger.error(f"Error updating permission: {str(e)}")
            raise

    async def delete_permission(self, permission_id: str) -> bool:
        """Delete a permission"""
        try:
            return await self.db.delete_permission(permission_id)
        except Exception as e:
            logger.error(f"Error deleting permission: {str(e)}")
            raise

# Dependency to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    
    auth_manager = AuthManager()
    user = await auth_manager.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user

# Dependency to get the current active user
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Dependency to get the current admin user
async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user

# Dependency to require admin role
async def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

# Dependency to require system role
async def require_system(current_user: User = Depends(get_current_user)):
    if not current_user.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System privileges required"
        )
    return current_user

# Create a global instance of AuthManager
auth_manager = AuthManager()