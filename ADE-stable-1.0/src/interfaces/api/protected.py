from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any

from src.interfaces.api.auth import User, UserRole, has_role, get_current_active_user

router = APIRouter(
    prefix="/api",
    tags=["protected"]
)

# Public endpoint (no authentication required)
@router.get("/public")
async def public_endpoint():
    return {"message": "This is a public endpoint"}

# User endpoint (any authenticated user)
@router.get("/user")
async def user_endpoint(current_user: User = Depends(get_current_active_user)):
    return {
        "message": f"Hello, {current_user.username}!",
        "roles": current_user.roles
    }

# Developer endpoint (requires DEVELOPER role)
@router.get("/developer")
async def developer_endpoint(current_user: User = Depends(has_role([UserRole.DEVELOPER]))):
    return {
        "message": "Developer access granted",
        "user": current_user.username,
        "roles": current_user.roles
    }

# Admin endpoint (requires ADMIN role)
@router.get("/admin")
async def admin_endpoint(current_user: User = Depends(has_role([UserRole.ADMIN]))):
    return {
        "message": "Admin access granted",
        "user": current_user.username,
        "roles": current_user.roles
    }

# Multi-role endpoint (requires either ADMIN or DEVELOPER role)
@router.get("/manage")
async def management_endpoint(current_user: User = Depends(has_role([UserRole.ADMIN, UserRole.DEVELOPER]))):
    return {
        "message": "Management access granted",
        "user": current_user.username,
        "roles": current_user.roles
    } 