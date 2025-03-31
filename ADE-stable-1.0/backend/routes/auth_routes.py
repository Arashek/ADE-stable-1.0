from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ..auth.auth import auth_manager
from ..models.management_components import User, Role, Permission
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Token endpoint
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get access token"""
    try:
        user = await auth_manager.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=auth_manager.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_manager.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# User management endpoints
@router.post("/users", response_model=User)
async def create_user(
    username: str,
    password: str,
    email: str,
    full_name: str,
    current_user: User = Depends(auth_manager.require_permissions(["create_user"]))
):
    """Create a new user"""
    try:
        user = await auth_manager.create_user(username, password, email, full_name)
        return user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_data: dict,
    current_user: User = Depends(auth_manager.require_permissions(["update_user"]))
):
    """Update user information"""
    try:
        user = await auth_manager.update_user(user_id, user_data)
        return user
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(auth_manager.require_permissions(["delete_user"]))
):
    """Delete a user"""
    try:
        success = await auth_manager.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "User deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )

# Role management endpoints
@router.post("/roles", response_model=Role)
async def create_role(
    name: str,
    description: str,
    permissions: List[str],
    current_user: User = Depends(auth_manager.require_permissions(["create_role"]))
):
    """Create a new role"""
    try:
        role = await auth_manager.create_role(name, description, permissions)
        return role
    except Exception as e:
        logger.error(f"Error creating role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating role"
        )

@router.put("/roles/{role_id}", response_model=Role)
async def update_role(
    role_id: str,
    role_data: dict,
    current_user: User = Depends(auth_manager.require_permissions(["update_role"]))
):
    """Update role information"""
    try:
        role = await auth_manager.update_role(role_id, role_data)
        return role
    except Exception as e:
        logger.error(f"Error updating role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating role"
        )

@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: str,
    current_user: User = Depends(auth_manager.require_permissions(["delete_role"]))
):
    """Delete a role"""
    try:
        success = await auth_manager.delete_role(role_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return {"message": "Role deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting role"
        )

# Permission management endpoints
@router.post("/permissions", response_model=Permission)
async def create_permission(
    name: str,
    description: str,
    resource_type: str,
    actions: List[str],
    current_user: User = Depends(auth_manager.require_permissions(["create_permission"]))
):
    """Create a new permission"""
    try:
        permission = await auth_manager.create_permission(name, description, resource_type, actions)
        return permission
    except Exception as e:
        logger.error(f"Error creating permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating permission"
        )

@router.put("/permissions/{permission_id}", response_model=Permission)
async def update_permission(
    permission_id: str,
    permission_data: dict,
    current_user: User = Depends(auth_manager.require_permissions(["update_permission"]))
):
    """Update permission information"""
    try:
        permission = await auth_manager.update_permission(permission_id, permission_data)
        return permission
    except Exception as e:
        logger.error(f"Error updating permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating permission"
        )

@router.delete("/permissions/{permission_id}")
async def delete_permission(
    permission_id: str,
    current_user: User = Depends(auth_manager.require_permissions(["delete_permission"]))
):
    """Delete a permission"""
    try:
        success = await auth_manager.delete_permission(permission_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        return {"message": "Permission deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting permission"
        )

# Role assignment endpoints
@router.post("/users/{user_id}/roles/{role_id}")
async def assign_role(
    user_id: str,
    role_id: str,
    current_user: User = Depends(auth_manager.require_permissions(["assign_role"]))
):
    """Assign a role to a user"""
    try:
        success = await auth_manager.assign_role(user_id, role_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User or role not found"
            )
        return {"message": "Role assigned successfully"}
    except Exception as e:
        logger.error(f"Error assigning role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error assigning role"
        )

@router.delete("/users/{user_id}/roles/{role_id}")
async def remove_role(
    user_id: str,
    role_id: str,
    current_user: User = Depends(auth_manager.require_permissions(["remove_role"]))
):
    """Remove a role from a user"""
    try:
        success = await auth_manager.remove_role(user_id, role_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User or role not found"
            )
        return {"message": "Role removed successfully"}
    except Exception as e:
        logger.error(f"Error removing role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error removing role"
        )

# Current user endpoint
@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(auth_manager.get_current_active_user)):
    """Get current user information"""
    return current_user 