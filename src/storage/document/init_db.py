import asyncio
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

from src.storage.document.indexes import initialize_indexes

# Configure logging
logger = logging.getLogger("ade-db-init")

async def ensure_db_connection(mongodb_uri: str, max_retries: int = 5, retry_delay: int = 2):
    """Ensure database connection is available"""
    client = AsyncIOMotorClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    
    for retry in range(max_retries):
        try:
            # Check connection
            await client.admin.command('ping')
            logger.info("MongoDB connection successful")
            client.close()
            return True
        except ServerSelectionTimeoutError:
            logger.warning(f"MongoDB connection failed, retrying ({retry+1}/{max_retries})...")
            await asyncio.sleep(retry_delay)
    
    logger.error(f"Failed to connect to MongoDB after {max_retries} retries")
    client.close()
    return False

async def init_database(mongodb_uri: str = None):
    """Initialize database with required collections and indexes"""
    if not mongodb_uri:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/ade")
    
    # Ensure database connection
    connection_success = await ensure_db_connection(mongodb_uri)
    if not connection_success:
        logger.error("Cannot initialize database, connection failed")
        return False
    
    try:
        # Initialize indexes
        await initialize_indexes(mongodb_uri)
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        return False

# Main function for direct script execution
async def main():
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/ade")
    await init_database(mongodb_uri)

if __name__ == "__main__":
    asyncio.run(main()) 