"""Base repository implementation."""
from typing import Any
from motor.motor_asyncio import AsyncIOMotorCollection

from .connection import MongoDBConnection

class BaseRepository:
    """Base class for repositories."""

    def __init__(self, connection: MongoDBConnection, collection_name: str):
        """Initialize repository."""
        self.connection = connection
        self.collection_name = collection_name
        self.collection: AsyncIOMotorCollection = self.connection.client[
            self.connection.database_name
        ][collection_name] 