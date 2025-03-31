"""MongoDB connection implementation."""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class MongoDBConnection:
    """MongoDB connection manager."""

    def __init__(
        self,
        uri: str = "mongodb://localhost:27017",
        database_name: str = "ade_platform"
    ):
        """Initialize connection."""
        self.uri = uri
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None

    async def connect(self) -> None:
        """Connect to MongoDB."""
        if not self.client:
            self.client = AsyncIOMotorClient(self.uri)

    async def disconnect(self) -> None:
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            self.client = None 