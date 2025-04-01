from typing import Dict, List, Optional
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, delete
from .models.core_components import (
    UserProfile, Notification, DashboardMetrics, NavigationItem,
    UserSettings, SystemHealth, ResourceUsage, DeploymentStatus,
    UserManagement, SystemOverview
)
from .config import settings

logger = logging.getLogger(__name__)

class CoreDB:
    def __init__(self):
        self.engine = create_async_engine(settings.DATABASE_URL)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def connect(self):
        """Establish database connection"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(self._create_tables)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise

    async def _create_tables(self, connection):
        """Create necessary database tables"""
        # Create users table
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT,
                avatar_url TEXT,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                settings JSONB DEFAULT '{}',
                permissions JSONB DEFAULT '[]',
                is_active BOOLEAN DEFAULT true,
                mfa_enabled BOOLEAN DEFAULT false
            )
        """)

        # Create notifications table
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                priority TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP,
                user_id INTEGER REFERENCES users(id),
                metadata JSONB DEFAULT '{}'
            )
        """)

        # Create navigation table
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS navigation (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                path TEXT NOT NULL,
                icon TEXT NOT NULL,
                order INTEGER NOT NULL,
                permissions JSONB DEFAULT '[]',
                parent_id INTEGER REFERENCES navigation(id),
                is_active BOOLEAN DEFAULT true
            )
        """)

        # Create system_health table
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS system_health (
                id SERIAL PRIMARY KEY,
                status TEXT NOT NULL,
                components JSONB DEFAULT '{}',
                last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                issues JSONB DEFAULT '[]',
                recommendations JSONB DEFAULT '[]',
                metrics JSONB DEFAULT '{}'
            )
        """)

        # Create deployments table
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS deployments (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                version TEXT NOT NULL,
                environment TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                logs JSONB DEFAULT '[]',
                metrics JSONB DEFAULT '{}',
                errors JSONB DEFAULT '[]'
            )
        """)

        # Create services table
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metrics JSONB DEFAULT '{}',
                config JSONB DEFAULT '{}'
            )
        """)

    async def get_dashboard_metrics(self) -> Dict:
        """Get dashboard metrics"""
        async with self.async_session() as session:
            result = await session.execute("""
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(*) FILTER (WHERE last_login > NOW() - INTERVAL '1 hour') as active_users,
                    COUNT(*) FILTER (WHERE status >= 400)::float / NULLIF(COUNT(*), 0)::float as error_rate,
                    AVG(response_time) as response_time
                FROM users
                CROSS JOIN api_requests
                WHERE api_requests.created_at > NOW() - INTERVAL '1 hour'
            """)
            return dict(result.first())

    async def get_system_overview(self) -> Dict:
        """Get system overview"""
        async with self.async_session() as session:
            result = await session.execute("""
                SELECT 
                    version,
                    environment,
                    last_update,
                    next_maintenance,
                    active_services,
                    system_info,
                    performance_metrics
                FROM system_info
                ORDER BY last_update DESC
                LIMIT 1
            """)
            return dict(result.first())

    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions"""
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT permissions FROM users WHERE id = :user_id",
                {"user_id": user_id}
            )
            return result.scalar() or []

    async def get_navigation_items(self) -> List[Dict]:
        """Get navigation items"""
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT * FROM navigation WHERE is_active = true ORDER BY order"
            )
            return [dict(row) for row in result]

    async def get_user_profile(self, user_id: str) -> Dict:
        """Get user profile"""
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT * FROM users WHERE id = :user_id",
                {"user_id": user_id}
            )
            return dict(result.first())

    async def update_user_profile(self, user_id: str, profile: Dict) -> Dict:
        """Update user profile"""
        async with self.async_session() as session:
            await session.execute(
                """
                UPDATE users 
                SET 
                    username = :username,
                    email = :email,
                    role = :role,
                    full_name = :full_name,
                    avatar_url = :avatar_url,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :user_id
                """,
                {**profile, "user_id": user_id}
            )
            await session.commit()
            return await self.get_user_profile(user_id)

    async def get_user_settings(self, user_id: str) -> Dict:
        """Get user settings"""
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT settings FROM users WHERE id = :user_id",
                {"user_id": user_id}
            )
            return result.scalar() or {}

    async def update_user_settings(self, user_id: str, settings: Dict) -> Dict:
        """Update user settings"""
        async with self.async_session() as session:
            await session.execute(
                """
                UPDATE users 
                SET settings = :settings, updated_at = CURRENT_TIMESTAMP
                WHERE id = :user_id
                """,
                {"settings": settings, "user_id": user_id}
            )
            await session.commit()
            return await self.get_user_settings(user_id)

    async def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        page: int = 1,
        limit: int = 10
    ) -> List[Dict]:
        """Get user notifications"""
        async with self.async_session() as session:
            query = """
                SELECT * FROM notifications 
                WHERE user_id = :user_id
            """
            if unread_only:
                query += " AND read_at IS NULL"
            
            query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            
            result = await session.execute(
                query,
                {
                    "user_id": user_id,
                    "limit": limit,
                    "offset": (page - 1) * limit
                }
            )
            return [dict(row) for row in result]

    async def mark_notification_read(self, user_id: str, notification_id: str) -> Dict:
        """Mark notification as read"""
        async with self.async_session() as session:
            await session.execute(
                """
                UPDATE notifications 
                SET read_at = CURRENT_TIMESTAMP
                WHERE id = :notification_id AND user_id = :user_id
                """,
                {"notification_id": notification_id, "user_id": user_id}
            )
            await session.commit()
            return {"status": "success"}

    async def get_system_health(self) -> Dict:
        """Get system health"""
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT * FROM system_health ORDER BY last_check DESC LIMIT 1"
            )
            return dict(result.first())

    async def get_service_status(self) -> Dict:
        """Get service status"""
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT * FROM services ORDER BY last_check DESC"
            )
            return {row.name: dict(row) for row in result}

    async def get_deployments(
        self,
        status: Optional[str] = None,
        environment: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> List[Dict]:
        """Get deployments"""
        async with self.async_session() as session:
            query = "SELECT * FROM deployments WHERE 1=1"
            params = {}
            
            if status:
                query += " AND status = :status"
                params["status"] = status
            if environment:
                query += " AND environment = :environment"
                params["environment"] = environment
                
            query += " ORDER BY started_at DESC LIMIT :limit OFFSET :offset"
            params["limit"] = limit
            params["offset"] = (page - 1) * limit
            
            result = await session.execute(query, params)
            return [dict(row) for row in result]

    async def get_user_management(self) -> Dict:
        """Get user management overview"""
        async with self.async_session() as session:
            result = await session.execute("""
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(*) FILTER (WHERE is_active = true) as active_users,
                    COUNT(*) FILTER (WHERE is_active = false) as suspended_users,
                    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '1 day') as new_users_today,
                    jsonb_object_agg(role, count) as user_roles
                FROM users
                CROSS JOIN LATERAL (
                    SELECT role, COUNT(*) as count
                    FROM users
                    GROUP BY role
                ) roles
            """)
            return dict(result.first())

    async def get_user(self, user_id: str) -> Dict:
        """Get user details"""
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT * FROM users WHERE id = :user_id",
                {"user_id": user_id}
            )
            return dict(result.first())

    async def update_user(self, user_id: str, user_data: Dict) -> Dict:
        """Update user details"""
        async with self.async_session() as session:
            await session.execute(
                """
                UPDATE users 
                SET 
                    username = :username,
                    email = :email,
                    role = :role,
                    is_active = :is_active,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :user_id
                """,
                {**user_data, "user_id": user_id}
            )
            await session.commit()
            return await self.get_user(user_id)

    async def delete_user(self, user_id: str) -> Dict:
        """Delete user"""
        async with self.async_session() as session:
            await session.execute(
                "DELETE FROM users WHERE id = :user_id",
                {"user_id": user_id}
            )
            await session.commit()
            return {"status": "success"}

    async def close(self):
        """Close database connection"""
        await self.engine.dispose() 