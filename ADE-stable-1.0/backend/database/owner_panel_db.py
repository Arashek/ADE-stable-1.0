from typing import Dict, List, Optional
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, delete
from ..models.owner_panel import (
    SystemMetrics,
    UserStats,
    SecurityConfig,
    FrontendConfig,
    SupportTicket,
    AuditLog,
    SystemDiagnostics,
    APIKey
)
from ..config import settings

logger = logging.getLogger(__name__)

class OwnerPanelDB:
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
        # Create tables for owner panel data
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active_users INTEGER,
                total_users INTEGER,
                system_load FLOAT,
                memory_usage FLOAT,
                storage_usage FLOAT,
                api_requests INTEGER,
                error_rate FLOAT
            )
        """)

        await connection.execute("""
            CREATE TABLE IF NOT EXISTS security_config (
                id SERIAL PRIMARY KEY,
                auth_providers JSONB,
                mfa_enabled BOOLEAN,
                session_timeout INTEGER,
                password_policy JSONB,
                ip_whitelist JSONB,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await connection.execute("""
            CREATE TABLE IF NOT EXISTS frontend_config (
                id SERIAL PRIMARY KEY,
                theme JSONB,
                navigation JSONB,
                components JSONB,
                content JSONB,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await connection.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                id SERIAL PRIMARY KEY,
                title TEXT,
                description TEXT,
                status TEXT,
                priority TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await connection.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id SERIAL PRIMARY KEY,
                user_id TEXT,
                action_type TEXT,
                details JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await connection.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                key TEXT UNIQUE,
                hashed_key TEXT,
                description TEXT,
                permissions JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                revoked_at TIMESTAMP
            )
        """)

    async def get_active_users_count(self) -> int:
        """Get count of active users"""
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT COUNT(*) FROM users WHERE last_active > NOW() - INTERVAL '1 hour'"
            )
            return result.scalar()

    async def get_total_users_count(self) -> int:
        """Get total count of users"""
        async with self.async_session() as session:
            result = await session.execute("SELECT COUNT(*) FROM users")
            return result.scalar()

    async def get_api_requests_count(self) -> int:
        """Get count of API requests in the last hour"""
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT COUNT(*) FROM api_requests WHERE created_at > NOW() - INTERVAL '1 hour'"
            )
            return result.scalar()

    async def get_error_rate(self) -> float:
        """Get error rate in the last hour"""
        async with self.async_session() as session:
            result = await session.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE status >= 400)::float / 
                    NULLIF(COUNT(*), 0)::float
                FROM api_requests 
                WHERE created_at > NOW() - INTERVAL '1 hour'
            """)
            return result.scalar() or 0.0

    async def get_user_statistics(self) -> Dict:
        """Get user-related statistics"""
        async with self.async_session() as session:
            result = await session.execute("""
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(*) FILTER (WHERE last_active > NOW() - INTERVAL '1 hour') as active_users,
                    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '24 hours') as new_users,
                    COUNT(*) FILTER (WHERE status = 'suspended') as suspended_users,
                    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '30 days')::float / 
                    NULLIF(COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '60 days'), 0)::float as user_growth
                FROM users
            """)
            return dict(result.first())

    async def get_security_config(self) -> Dict:
        """Get current security configuration"""
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT * FROM security_config ORDER BY updated_at DESC LIMIT 1"
            )
            return dict(result.first())

    async def update_security_config(self, config: Dict) -> None:
        """Update security configuration"""
        async with self.async_session() as session:
            await session.execute(
                """
                INSERT INTO security_config 
                (auth_providers, mfa_enabled, session_timeout, password_policy, ip_whitelist)
                VALUES (:auth_providers, :mfa_enabled, :session_timeout, :password_policy, :ip_whitelist)
                """,
                config
            )
            await session.commit()

    async def get_frontend_config(self) -> Dict:
        """Get frontend configuration"""
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT * FROM frontend_config ORDER BY updated_at DESC LIMIT 1"
            )
            return dict(result.first())

    async def update_frontend_config(self, config: Dict) -> None:
        """Update frontend configuration"""
        async with self.async_session() as session:
            await session.execute(
                """
                INSERT INTO frontend_config 
                (theme, navigation, components, content)
                VALUES (:theme, :navigation, :components, :content)
                """,
                config
            )
            await session.commit()

    async def get_support_tickets(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> List[Dict]:
        """Get support tickets with filtering and pagination"""
        async with self.async_session() as session:
            query = "SELECT * FROM support_tickets WHERE 1=1"
            params = {}
            
            if status:
                query += " AND status = :status"
                params['status'] = status
            if priority:
                query += " AND priority = :priority"
                params['priority'] = priority
                
            query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            params['limit'] = limit
            params['offset'] = (page - 1) * limit
            
            result = await session.execute(query, params)
            return [dict(row) for row in result]

    async def get_system_diagnostics(self) -> Dict:
        """Get system diagnostics and health information"""
        async with self.async_session() as session:
            result = await session.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE status = 'error') as error_count,
                    COUNT(*) FILTER (WHERE status = 'warning') as warning_count,
                    COUNT(*) FILTER (WHERE status = 'info') as info_count,
                    MAX(created_at) as last_check
                FROM system_metrics
                WHERE created_at > NOW() - INTERVAL '1 hour'
            """)
            return dict(result.first())

    async def get_audit_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action_type: Optional[str] = None,
        user_id: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> List[Dict]:
        """Get audit logs with filtering and pagination"""
        async with self.async_session() as session:
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = {}
            
            if start_date:
                query += " AND created_at >= :start_date"
                params['start_date'] = start_date
            if end_date:
                query += " AND created_at <= :end_date"
                params['end_date'] = end_date
            if action_type:
                query += " AND action_type = :action_type"
                params['action_type'] = action_type
            if user_id:
                query += " AND user_id = :user_id"
                params['user_id'] = user_id
                
            query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            params['limit'] = limit
            params['offset'] = (page - 1) * limit
            
            result = await session.execute(query, params)
            return [dict(row) for row in result]

    async def get_api_keys(self) -> List[Dict]:
        """Get all API keys"""
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT * FROM api_keys WHERE revoked_at IS NULL ORDER BY created_at DESC"
            )
            return [dict(row) for row in result]

    async def create_api_key(self, api_key: Dict) -> None:
        """Create a new API key"""
        async with self.async_session() as session:
            await session.execute(
                """
                INSERT INTO api_keys 
                (key, hashed_key, description, permissions)
                VALUES (:key, :hashed_key, :description, :permissions)
                """,
                api_key
            )
            await session.commit()

    async def revoke_api_key(self, key_id: str) -> None:
        """Revoke an API key"""
        async with self.async_session() as session:
            await session.execute(
                """
                UPDATE api_keys 
                SET revoked_at = CURRENT_TIMESTAMP 
                WHERE id = :key_id
                """,
                {"key_id": key_id}
            )
            await session.commit()

    async def close(self):
        """Close database connection"""
        await self.engine.dispose() 