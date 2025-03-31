from typing import Dict, List, Any
from datetime import timedelta
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT, GEOSPHERE

from .models import Plan, Task, TaskStatus

# Configure logging
logger = logging.getLogger("ade-indexes")

def get_plan_indexes() -> List[Dict[str, Any]]:
    """Get index definitions for the plans collection"""
    return [
        # Primary key index
        {
            "key": [("_id", 1)],
            "name": "plan_id_idx",
            "unique": True
        },
        
        # Text search indexes
        {
            "key": [
                ("title", "text"),
                ("description", "text")
            ],
            "name": "plan_text_search_idx",
            "weights": {
                "title": 10,
                "description": 5
            }
        },
        
        # Status index
        {
            "key": [("status", 1)],
            "name": "plan_status_idx"
        },
        
        # Created at index for sorting and time-based queries
        {
            "key": [("created_at", 1)],
            "name": "plan_created_at_idx"
        },
        
        # Updated at index for sorting and time-based queries
        {
            "key": [("updated_at", 1)],
            "name": "plan_updated_at_idx"
        },
        
        # TTL index for temporary plans
        {
            "key": [("expires_at", 1)],
            "name": "plan_ttl_idx",
            "expireAfterSeconds": 0
        }
    ]

def get_task_indexes() -> List[Dict[str, Any]]:
    """Get index definitions for the tasks collection"""
    return [
        # Primary key index
        {
            "key": [("_id", 1)],
            "name": "task_id_idx",
            "unique": True
        },
        
        # Compound index for plan_id and status
        {
            "key": [
                ("plan_id", 1),
                ("status", 1)
            ],
            "name": "task_plan_status_idx"
        },
        
        # Text search indexes
        {
            "key": [
                ("title", "text"),
                ("description", "text")
            ],
            "name": "task_text_search_idx",
            "weights": {
                "title": 10,
                "description": 5
            }
        },
        
        # Status index for filtering
        {
            "key": [("status", 1)],
            "name": "task_status_idx"
        },
        
        # Created at index for sorting and time-based queries
        {
            "key": [("created_at", 1)],
            "name": "task_created_at_idx"
        },
        
        # Updated at index for sorting and time-based queries
        {
            "key": [("updated_at", 1)],
            "name": "task_updated_at_idx"
        },
        
        # Priority index for sorting
        {
            "key": [("priority", 1)],
            "name": "task_priority_idx"
        },
        
        # Compound index for status and priority
        {
            "key": [
                ("status", 1),
                ("priority", 1)
            ],
            "name": "task_status_priority_idx"
        },
        
        # TTL index for temporary tasks
        {
            "key": [("expires_at", 1)],
            "name": "task_ttl_idx",
            "expireAfterSeconds": 0
        },
        
        # Index for task dependencies
        {
            "key": [("dependencies", 1)],
            "name": "task_dependencies_idx"
        },
        
        # Index for task tags
        {
            "key": [("tags", 1)],
            "name": "task_tags_idx"
        }
    ]

def get_indexes() -> Dict[str, List[Dict[str, Any]]]:
    """Get all index definitions for the database"""
    return {
        "plans": get_plan_indexes(),
        "tasks": get_task_indexes()
    }

async def create_indexes(db: AsyncIOMotorDatabase):
    """Create indexes for all collections"""
    logger.info("Creating database indexes...")
    
    # Plans collection indexes
    await create_plan_indexes(db)
    
    # Tasks collection indexes
    await create_task_indexes(db)
    
    # Users collection indexes
    await create_user_indexes(db)
    
    # Providers collection indexes
    await create_provider_indexes(db)
    
    logger.info("Database indexes created successfully")

async def create_plan_indexes(db: AsyncIOMotorDatabase):
    """Create indexes for plans collection"""
    # Create indexes for the plans collection
    plan_indexes = [
        # Primary ID index for lookups
        IndexModel([("id", ASCENDING)], unique=True),
        
        # Status index for filtering
        IndexModel([("status", ASCENDING)]),
        
        # Text index for searching
        IndexModel([
            ("title", TEXT),
            ("description", TEXT)
        ], weights={"title": 10, "description": 5}, default_language="english", name="plan_text_search"),
        
        # Created/updated time indexes for sorting and filtering
        IndexModel([("created_at", DESCENDING)]),
        IndexModel([("updated_at", DESCENDING)])
    ]
    
    # Create all indexes
    await db.plans.create_indexes(plan_indexes)
    logger.info("Created indexes for plans collection")

async def create_task_indexes(db: AsyncIOMotorDatabase):
    """Create indexes for tasks collection"""
    # Create indexes for the tasks collection
    task_indexes = [
        # Primary ID index for lookups
        IndexModel([("id", ASCENDING)], unique=True),
        
        # Plan ID index for task lookups by plan
        IndexModel([("plan_id", ASCENDING)]),
        
        # Compound index for plan_id and status
        IndexModel([("plan_id", ASCENDING), ("status", ASCENDING)]),
        
        # Status index for filtering
        IndexModel([("status", ASCENDING)]),
        
        # Text index for searching
        IndexModel([
            ("title", TEXT),
            ("description", TEXT)
        ], weights={"title": 10, "description": 5}, default_language="english", name="task_text_search"),
        
        # Created/updated time indexes for sorting and filtering
        IndexModel([("created_at", DESCENDING)]),
        IndexModel([("updated_at", DESCENDING)])
    ]
    
    # Create all indexes
    await db.tasks.create_indexes(task_indexes)
    logger.info("Created indexes for tasks collection")

async def create_user_indexes(db: AsyncIOMotorDatabase):
    """Create indexes for users collection"""
    # Create indexes for the users collection
    user_indexes = [
        # Username index for lookups
        IndexModel([("username", ASCENDING)], unique=True),
        
        # Email index for lookups
        IndexModel([("email", ASCENDING)], unique=True, sparse=True),
        
        # API key index for lookups
        IndexModel([("api_key", ASCENDING)], unique=True, sparse=True),
        
        # Roles index for filtering
        IndexModel([("roles", ASCENDING)]),
        
        # Last login time index for sorting
        IndexModel([("last_login", DESCENDING)]),
        
        # Text index for searching
        IndexModel([
            ("username", TEXT),
            ("full_name", TEXT),
            ("email", TEXT)
        ], weights={"username": 10, "full_name": 5, "email": 5}, default_language="english", name="user_text_search")
    ]
    
    # Create all indexes
    await db.users.create_indexes(user_indexes)
    logger.info("Created indexes for users collection")

async def create_provider_indexes(db: AsyncIOMotorDatabase):
    """Create indexes for providers collection"""
    # Create indexes for the providers collection
    provider_indexes = [
        # Provider ID index for lookups
        IndexModel([("provider_id", ASCENDING)], unique=True),
        
        # Provider type index for filtering
        IndexModel([("provider_type", ASCENDING)]),
        
        # Active status index for filtering
        IndexModel([("is_active", ASCENDING)]),
        
        # Capabilities index for filtering
        IndexModel([("capabilities", ASCENDING)])
    ]
    
    # Create all indexes
    await db.providers.create_indexes(provider_indexes)
    logger.info("Created indexes for providers collection")

# Function to initialize indexes
async def initialize_indexes(mongodb_uri: str, db_name: str = "ade"):
    """Initialize all database indexes"""
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[db_name]
    
    logger.info(f"Initializing indexes for database: {db_name}")
    await create_indexes(db)
    
    # Close client
    client.close()
    
    return True

# Example usage:
"""
from storage.document.indexes import get_indexes

# Get all index definitions
indexes = get_indexes()

# Create indexes for a collection
async def create_indexes(db):
    for collection_name, collection_indexes in indexes.items():
        collection = db[collection_name]
        for index in collection_indexes:
            await collection.create_index(**index)
""" 