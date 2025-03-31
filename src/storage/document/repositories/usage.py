from typing import Dict, List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from src.storage.document.models.usage import UsageRecord, UserUsageSummary
from src.storage.document.repositories.base import BaseRepository
from src.models.user import User, UserCreate, UserUpdate, UserInDB

class UsageRepository(BaseRepository):
    """Repository for managing usage records and summaries"""
    
    def __init__(self, client: AsyncIOMotorClient, database: str):
        super().__init__(client, database)
        self.usage_collection = self.db.usage_records
        self.summary_collection = self.db.usage_summaries
        
        # Create indexes
        self._create_indexes()
    
    async def _create_indexes(self):
        """Create necessary indexes for usage collections"""
        # Indexes for usage records
        await self.usage_collection.create_index([
            ("user_id", 1),
            ("timestamp", -1)
        ])
        await self.usage_collection.create_index([
            ("project_id", 1),
            ("timestamp", -1)
        ])
        await self.usage_collection.create_index([
            ("provider", 1),
            ("timestamp", -1)
        ])
        
        # Indexes for usage summaries
        await self.summary_collection.create_index("user_id", unique=True)
    
    async def create(self, record: UsageRecord) -> UsageRecord:
        """Create a new usage record"""
        await self.usage_collection.insert_one(record.model_dump())
        return record
    
    async def find(
        self,
        query: Dict,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_order: int = -1
    ) -> List[UsageRecord]:
        """Find usage records matching the query"""
        cursor = self.usage_collection.find(query)
        
        if sort_by:
            cursor = cursor.sort(sort_by, sort_order)
        
        cursor = cursor.skip(skip).limit(limit)
        
        records = []
        async for doc in cursor:
            records.append(UsageRecord(**doc))
        
        return records
    
    async def get_summary(self, user_id: str) -> Optional[UserUsageSummary]:
        """Get usage summary for a user"""
        doc = await self.summary_collection.find_one({"user_id": user_id})
        if doc:
            return UserUsageSummary(**doc)
        return None
    
    async def update_summary(self, user_id: str, summary: UserUsageSummary) -> UserUsageSummary:
        """Update or create usage summary for a user"""
        await self.summary_collection.update_one(
            {"user_id": user_id},
            {"$set": summary.model_dump()},
            upsert=True
        )
        return summary
    
    async def get_usage_by_date_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[UsageRecord]:
        """Get usage records for a date range"""
        query = {
            "user_id": user_id,
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        return await self.find(query, sort_by="timestamp")
    
    async def get_usage_by_provider(
        self,
        user_id: str,
        provider: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[UsageRecord]:
        """Get usage records for a specific provider"""
        query = {
            "user_id": user_id,
            "provider": provider
        }
        
        if start_date:
            query["timestamp"] = {"$gte": start_date}
        if end_date:
            query["timestamp"] = {"$lte": end_date}
            
        return await self.find(query, sort_by="timestamp")
    
    async def get_usage_by_type(
        self,
        user_id: str,
        usage_type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[UsageRecord]:
        """Get usage records for a specific usage type"""
        query = {
            "user_id": user_id,
            "usage_type": usage_type
        }
        
        if start_date:
            query["timestamp"] = {"$gte": start_date}
        if end_date:
            query["timestamp"] = {"$lte": end_date}
            
        return await self.find(query, sort_by="timestamp")
    
    async def get_project_usage(
        self,
        project_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[UsageRecord]:
        """Get usage records for a specific project"""
        query = {"project_id": project_id}
        
        if start_date:
            query["timestamp"] = {"$gte": start_date}
        if end_date:
            query["timestamp"] = {"$lte": end_date}
            
        return await self.find(query, sort_by="timestamp")
    
    async def aggregate_usage(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        group_by: str = "day"
    ) -> List[Dict]:
        """Aggregate usage data by time period"""
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "timestamp": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d" if group_by == "day" else "%Y-%m",
                            "date": "$timestamp"
                        }
                    },
                    "total_tokens": {"$sum": "$tokens_used"},
                    "total_cost": {"$sum": "$cost"},
                    "requests": {"$sum": 1},
                    "successful_requests": {
                        "$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}
                    }
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        cursor = self.usage_collection.aggregate(pipeline)
        return await cursor.to_list(length=None)
    
    async def delete_old_records(self, cutoff_date: datetime) -> int:
        """Delete usage records older than the cutoff date.
        
        Args:
            cutoff_date: Delete records older than this date
            
        Returns:
            Number of records deleted
        """
        result = await self.usage_collection.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        return result.deleted_count

class UserRepository(BaseRepository):
    """Repository for managing user data"""
    
    def __init__(self, client: AsyncIOMotorClient, database: str):
        super().__init__(client, database)
        self.collection = self.db.users
        
        # Create indexes
        self._create_indexes()
    
    async def _create_indexes(self):
        """Create necessary indexes for user collection"""
        await self.collection.create_index("email", unique=True)
        await self.collection.create_index("username", unique=True)
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by their ID"""
        doc = await self.collection.find_one({"id": user_id})
        if doc:
            return User(**doc)
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email"""
        doc = await self.collection.find_one({"email": email})
        if doc:
            return User(**doc)
        return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by their username"""
        doc = await self.collection.find_one({"username": username})
        if doc:
            return User(**doc)
        return None
    
    async def create(self, user: UserCreate) -> User:
        """Create a new user"""
        user_dict = user.model_dump()
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = user_dict["created_at"]
        
        result = await self.collection.insert_one(user_dict)
        user_dict["id"] = str(result.inserted_id)
        
        return User(**user_dict)
    
    async def update(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Update a user's information"""
        update_data = user_update.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            result = await self.collection.update_one(
                {"id": user_id},
                {"$set": update_data}
            )
            if result.modified_count:
                return await self.get_by_id(user_id)
        return None
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user"""
        result = await self.collection.delete_one({"id": user_id})
        return result.deleted_count > 0
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> List[User]:
        """List users with pagination"""
        cursor = self.collection.find()
        cursor = cursor.sort(sort_by, sort_order).skip(skip).limit(limit)
        
        users = []
        async for doc in cursor:
            users.append(User(**doc))
        return users
    
    async def get_user_in_db(self, username: str) -> Optional[UserInDB]:
        """Get a user with their hashed password for authentication"""
        doc = await self.collection.find_one({"username": username})
        if doc:
            return UserInDB(**doc)
        return None 