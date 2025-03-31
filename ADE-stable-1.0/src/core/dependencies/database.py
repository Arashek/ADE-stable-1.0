from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient
from src.config.settings import get_settings

class Database:
    def __init__(self, client: AsyncIOMotorClient, name: str):
        self.client = client
        self.name = name

async def get_database() -> AsyncGenerator[Database, None]:
    """Get database connection"""
    settings = get_settings()
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    try:
        yield Database(client, settings.MONGODB_DATABASE)
    finally:
        client.close() 