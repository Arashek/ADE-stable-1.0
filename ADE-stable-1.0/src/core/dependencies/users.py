"""User repository dependency."""
from typing import AsyncGenerator
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient

from src.storage.document.repositories import UserRepository
from src.core.dependencies.database import get_database

async def get_user_repository(
    db: AsyncIOMotorClient = Depends(get_database)
) -> AsyncGenerator[UserRepository, None]:
    """Get user repository instance.
    
    Args:
        db: MongoDB client instance
        
    Returns:
        User repository instance
    """
    repository = UserRepository(db.client, db.name)
    yield repository 