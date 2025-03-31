from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging
from .models.base import Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, database_url: str):
        """Initialize database connection manager"""
        self.database_url = database_url
        self.engine = None
        self.async_session = None

    async def connect(self):
        """Create database connection and initialize session"""
        try:
            self.engine = create_async_engine(
                self.database_url,
                echo=True,
                future=True
            )
            self.async_session = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise

    async def disconnect(self):
        """Close database connection"""
        try:
            await self.engine.dispose()
            logger.info("Database connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connection: {str(e)}")
            raise

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        async with self.async_session() as session:
            try:
                yield session
            except Exception as e:
                logger.error(f"Error in database session: {str(e)}")
                await session.rollback()
                raise
            finally:
                await session.close()

    async def create_tables(self):
        """Create database tables"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise

    async def drop_tables(self):
        """Drop database tables"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Error dropping database tables: {str(e)}")
            raise

# Create a global instance of DatabaseManager
# Replace with your actual database URL
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/management_db"
db_manager = DatabaseManager(DATABASE_URL) 