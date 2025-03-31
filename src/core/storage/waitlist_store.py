from typing import Optional, Dict, List
from datetime import datetime
import uuid
from ..db.database import get_database
from ..db.models.early_access import EarlyAccessRequest, WaitlistStatus

class WaitlistStore:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.early_access_requests

    async def create_request(self, request_data: Dict) -> Dict:
        """Create a new early access request"""
        request = EarlyAccessRequest(
            id=str(uuid.uuid4()),
            **request_data
        )
        
        await self.collection.insert_one(request.dict())
        return request.dict()

    async def get_request_by_email(self, email: str) -> Optional[Dict]:
        """Get an early access request by email"""
        request = await self.collection.find_one({"email": email})
        return request

    async def get_next_position(self) -> int:
        """Get the next available position in the waitlist"""
        last_request = await self.collection.find_one(
            sort=[("position", -1)]
        )
        return (last_request["position"] + 1) if last_request else 1

    async def update_request_status(
        self,
        email: str,
        status: WaitlistStatus,
        invitation_code: Optional[str] = None
    ) -> Dict:
        """Update the status of an early access request"""
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if invitation_code:
            update_data["invitation_code"] = invitation_code

        await self.collection.update_one(
            {"email": email},
            {"$set": update_data}
        )
        
        return await self.get_request_by_email(email)

    async def get_pending_requests(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """Get pending early access requests"""
        cursor = self.collection.find(
            {"status": WaitlistStatus.PENDING}
        ).sort("position", 1).skip(skip).limit(limit)
        
        return await cursor.to_list(length=limit)

    async def get_approved_requests(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """Get approved early access requests"""
        cursor = self.collection.find(
            {"status": WaitlistStatus.APPROVED}
        ).sort("position", 1).skip(skip).limit(limit)
        
        return await cursor.to_list(length=limit)

    async def generate_invitation_code(self) -> str:
        """Generate a unique invitation code"""
        while True:
            code = str(uuid.uuid4())[:8].upper()
            existing = await self.collection.find_one(
                {"invitation_code": code}
            )
            if not existing:
                return code

    async def get_waitlist_stats(self) -> Dict:
        """Get waitlist statistics"""
        total = await self.collection.count_documents({})
        pending = await self.collection.count_documents(
            {"status": WaitlistStatus.PENDING}
        )
        approved = await self.collection.count_documents(
            {"status": WaitlistStatus.APPROVED}
        )
        rejected = await self.collection.count_documents(
            {"status": WaitlistStatus.REJECTED}
        )

        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
        }

    async def get_use_case_distribution(self) -> Dict[str, int]:
        """Get distribution of use cases"""
        pipeline = [
            {"$group": {"_id": "$use_case", "count": {"$sum": 1}}}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        return {
            result["_id"]: result["count"]
            for result in results
            if result["_id"]
        }

    async def get_referral_sources(self) -> Dict[str, int]:
        """Get distribution of referral sources"""
        pipeline = [
            {"$group": {"_id": "$referral_source", "count": {"$sum": 1}}}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        return {
            result["_id"]: result["count"]
            for result in results
            if result["_id"]
        }

# Create a global instance
waitlist_store = WaitlistStore() 