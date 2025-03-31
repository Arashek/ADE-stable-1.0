from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import User, Role, Permission
from ..models.base import TimestampMixin
import logging

logger = logging.getLogger(__name__)

class UserOperations:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            result = await self.session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            raise

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            result = await self.session.execute(
                select(User).where(User.username == username)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            result = await self.session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise

    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        try:
            user = User(**user_data)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            await self.session.rollback()
            raise

    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
        """Update user information"""
        try:
            result = await self.session.execute(
                update(User)
                .where(User.id == user_id)
                .values(**user_data)
                .returning(User)
            )
            await self.session.commit()
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            await self.session.rollback()
            raise

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        try:
            result = await self.session.execute(
                delete(User)
                .where(User.id == user_id)
                .returning(User.id)
            )
            await self.session.commit()
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            await self.session.rollback()
            raise

    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Get user roles"""
        try:
            result = await self.session.execute(
                select(Role)
                .join(User.roles)
                .where(User.id == user_id)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting user roles: {str(e)}")
            raise

    async def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Assign a role to a user"""
        try:
            user = await self.get_user_by_id(user_id)
            role = await self.get_role_by_id(role_id)
            
            if not user or not role:
                return False
            
            user.roles.append(role)
            await self.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error assigning role to user: {str(e)}")
            await self.session.rollback()
            raise

    async def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Remove a role from a user"""
        try:
            user = await self.get_user_by_id(user_id)
            role = await self.get_role_by_id(role_id)
            
            if not user or not role:
                return False
            
            user.roles.remove(role)
            await self.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing role from user: {str(e)}")
            await self.session.rollback()
            raise

    async def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID"""
        try:
            result = await self.session.execute(
                select(Role).where(Role.id == role_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting role by ID: {str(e)}")
            raise

    async def get_role_permissions(self, role_id: str) -> List[Permission]:
        """Get role permissions"""
        try:
            result = await self.session.execute(
                select(Permission)
                .where(Permission.role_id == role_id)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting role permissions: {str(e)}")
            raise

    async def create_role(self, role_data: Dict[str, Any]) -> Role:
        """Create a new role"""
        try:
            role = Role(**role_data)
            self.session.add(role)
            await self.session.commit()
            await self.session.refresh(role)
            return role
        except Exception as e:
            logger.error(f"Error creating role: {str(e)}")
            await self.session.rollback()
            raise

    async def update_role(self, role_id: str, role_data: Dict[str, Any]) -> Optional[Role]:
        """Update role information"""
        try:
            result = await self.session.execute(
                update(Role)
                .where(Role.id == role_id)
                .values(**role_data)
                .returning(Role)
            )
            await self.session.commit()
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error updating role: {str(e)}")
            await self.session.rollback()
            raise

    async def delete_role(self, role_id: str) -> bool:
        """Delete a role"""
        try:
            result = await self.session.execute(
                delete(Role)
                .where(Role.id == role_id)
                .returning(Role.id)
            )
            await self.session.commit()
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Error deleting role: {str(e)}")
            await self.session.rollback()
            raise

    async def create_permission(self, permission_data: Dict[str, Any]) -> Permission:
        """Create a new permission"""
        try:
            permission = Permission(**permission_data)
            self.session.add(permission)
            await self.session.commit()
            await self.session.refresh(permission)
            return permission
        except Exception as e:
            logger.error(f"Error creating permission: {str(e)}")
            await self.session.rollback()
            raise

    async def update_permission(self, permission_id: str, permission_data: Dict[str, Any]) -> Optional[Permission]:
        """Update permission information"""
        try:
            result = await self.session.execute(
                update(Permission)
                .where(Permission.id == permission_id)
                .values(**permission_data)
                .returning(Permission)
            )
            await self.session.commit()
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error updating permission: {str(e)}")
            await self.session.rollback()
            raise

    async def delete_permission(self, permission_id: str) -> bool:
        """Delete a permission"""
        try:
            result = await self.session.execute(
                delete(Permission)
                .where(Permission.id == permission_id)
                .returning(Permission.id)
            )
            await self.session.commit()
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Error deleting permission: {str(e)}")
            await self.session.rollback()
            raise 