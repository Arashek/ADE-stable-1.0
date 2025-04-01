"""
Decision Repository

This module implements the repository for accessing and managing decision memory data,
enabling the platform to track design decisions, architectural choices, and technical debt
across the project lifecycle.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorCollection
from memory.repositories.models.decision_memory import (
    Decision, TechnicalDebt, DecisionCategory, 
    DecisionStatus, DecisionImpact, DecisionQuery
)
from memory.repositories.mongodb_connection import mongodb_manager

logger = logging.getLogger(__name__)

class DecisionRepository:
    """Repository for accessing and managing decision memory data"""
    
    def __init__(self):
        """Initialize the decision repository"""
        self.decision_collection_name = "decision_memory"
        self.technical_debt_collection_name = "technical_debt"
        
    async def _get_decision_collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection for decisions"""
        return await mongodb_manager.get_collection(self.decision_collection_name)
        
    async def _get_technical_debt_collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection for technical debt"""
        return await mongodb_manager.get_collection(self.technical_debt_collection_name)
        
    async def create_decision(self, decision: Decision) -> Decision:
        """Create a new decision"""
        try:
            collection = await self._get_decision_collection()
            
            # Convert to dict and insert
            decision_dict = decision.dict()
            result = await collection.insert_one(decision_dict)
            
            # Update ID if necessary
            if result.inserted_id and str(result.inserted_id) != str(decision.id):
                decision.id = result.inserted_id
                
            return decision
        except Exception as e:
            logger.error(f"Error creating decision: {str(e)}")
            raise
            
    async def get_decision(self, decision_id: UUID) -> Optional[Decision]:
        """Get a decision by ID"""
        try:
            collection = await self._get_decision_collection()
            
            # Find decision
            decision_dict = await collection.find_one({"id": str(decision_id)})
            
            if not decision_dict:
                return None
                
            # Convert to Decision object
            return Decision(**decision_dict)
        except Exception as e:
            logger.error(f"Error getting decision: {str(e)}")
            raise
            
    async def update_decision(self, decision: Decision) -> Decision:
        """Update an existing decision"""
        try:
            collection = await self._get_decision_collection()
            
            # Update timestamp
            decision.updated_at = datetime.utcnow()
            
            # Convert to dict and update
            decision_dict = decision.dict()
            await collection.replace_one({"id": str(decision.id)}, decision_dict)
            
            return decision
        except Exception as e:
            logger.error(f"Error updating decision: {str(e)}")
            raise
            
    async def delete_decision(self, decision_id: UUID) -> bool:
        """Delete a decision by ID"""
        try:
            collection = await self._get_decision_collection()
            
            # Delete decision
            result = await collection.delete_one({"id": str(decision_id)})
            
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting decision: {str(e)}")
            raise
            
    async def create_technical_debt(self, debt: TechnicalDebt) -> TechnicalDebt:
        """Create a new technical debt item"""
        try:
            collection = await self._get_technical_debt_collection()
            
            # Convert to dict and insert
            debt_dict = debt.dict()
            result = await collection.insert_one(debt_dict)
            
            # Update ID if necessary
            if result.inserted_id and str(result.inserted_id) != str(debt.id):
                debt.id = result.inserted_id
                
            return debt
        except Exception as e:
            logger.error(f"Error creating technical debt: {str(e)}")
            raise
            
    async def get_technical_debt(self, debt_id: UUID) -> Optional[TechnicalDebt]:
        """Get a technical debt item by ID"""
        try:
            collection = await self._get_technical_debt_collection()
            
            # Find technical debt
            debt_dict = await collection.find_one({"id": str(debt_id)})
            
            if not debt_dict:
                return None
                
            # Convert to TechnicalDebt object
            return TechnicalDebt(**debt_dict)
        except Exception as e:
            logger.error(f"Error getting technical debt: {str(e)}")
            raise
            
    async def update_technical_debt(self, debt: TechnicalDebt) -> TechnicalDebt:
        """Update an existing technical debt item"""
        try:
            collection = await self._get_technical_debt_collection()
            
            # Update timestamp
            debt.updated_at = datetime.utcnow()
            
            # Convert to dict and update
            debt_dict = debt.dict()
            await collection.replace_one({"id": str(debt.id)}, debt_dict)
            
            return debt
        except Exception as e:
            logger.error(f"Error updating technical debt: {str(e)}")
            raise
            
    async def delete_technical_debt(self, debt_id: UUID) -> bool:
        """Delete a technical debt item by ID"""
        try:
            collection = await self._get_technical_debt_collection()
            
            # Delete technical debt
            result = await collection.delete_one({"id": str(debt_id)})
            
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting technical debt: {str(e)}")
            raise
            
    async def resolve_technical_debt(self, debt_id: UUID) -> TechnicalDebt:
        """Mark a technical debt item as resolved"""
        try:
            # Get technical debt
            debt = await self.get_technical_debt(debt_id)
            
            if not debt:
                raise ValueError(f"Technical debt with ID {debt_id} not found")
                
            # Mark as resolved
            debt.resolved_at = datetime.utcnow()
            
            # Update technical debt
            await self.update_technical_debt(debt)
            
            return debt
        except Exception as e:
            logger.error(f"Error resolving technical debt: {str(e)}")
            raise
            
    async def query_decisions(self, query: DecisionQuery) -> List[Decision]:
        """Query decisions based on the specified criteria"""
        try:
            collection = await self._get_decision_collection()
            
            # Build query
            mongo_query = {"project_id": str(query.project_id)}
            
            if query.categories:
                mongo_query["category"] = {"$in": [c.value for c in query.categories]}
                
            if query.statuses:
                mongo_query["status"] = {"$in": [s.value for s in query.statuses]}
                
            if query.impacts:
                mongo_query["impact"] = {"$in": [i.value for i in query.impacts]}
                
            if query.tags:
                mongo_query["tags"] = {"$in": query.tags}
                
            if query.start_date:
                mongo_query["created_at"] = {"$gte": query.start_date}
                
            if query.end_date:
                if "created_at" in mongo_query:
                    mongo_query["created_at"]["$lte"] = query.end_date
                else:
                    mongo_query["created_at"] = {"$lte": query.end_date}
                    
            # Find decisions
            cursor = collection.find(mongo_query)
            
            # Sort by created_at (descending)
            cursor = cursor.sort("created_at", -1)
            
            # Convert to Decision objects
            decisions = [Decision(**decision) async for decision in cursor]
            
            return decisions
        except Exception as e:
            logger.error(f"Error querying decisions: {str(e)}")
            raise
            
    async def get_project_technical_debt(
        self,
        project_id: UUID,
        include_resolved: bool = False
    ) -> List[TechnicalDebt]:
        """Get technical debt items for a project"""
        try:
            collection = await self._get_technical_debt_collection()
            
            # Build query
            query = {"project_id": str(project_id)}
            
            if not include_resolved:
                query["resolved_at"] = None
                
            # Find technical debt items
            cursor = collection.find(query)
            
            # Sort by severity (descending) and created_at (descending)
            cursor = cursor.sort([("severity", -1), ("created_at", -1)])
            
            # Convert to TechnicalDebt objects
            debt_items = [TechnicalDebt(**debt) async for debt in cursor]
            
            return debt_items
        except Exception as e:
            logger.error(f"Error getting project technical debt: {str(e)}")
            raise
            
    async def get_technical_debt_summary(self, project_id: UUID) -> Dict[str, Any]:
        """Get a summary of technical debt for a project"""
        try:
            collection = await self._get_technical_debt_collection()
            
            # Get total count
            total_count = await collection.count_documents({"project_id": str(project_id)})
            
            # Get resolved count
            resolved_count = await collection.count_documents({
                "project_id": str(project_id),
                "resolved_at": {"$ne": None}
            })
            
            # Get counts by severity
            pipeline = [
                {"$match": {"project_id": str(project_id)}},
                {"$group": {
                    "_id": "$severity",
                    "count": {"$sum": 1}
                }}
            ]
            
            cursor = collection.aggregate(pipeline)
            severity_counts = {item["_id"]: item["count"] async for item in cursor}
            
            # Get counts by category
            pipeline = [
                {"$match": {"project_id": str(project_id)}},
                {"$group": {
                    "_id": "$category",
                    "count": {"$sum": 1}
                }}
            ]
            
            cursor = collection.aggregate(pipeline)
            category_counts = {item["_id"]: item["count"] async for item in cursor}
            
            return {
                "total_count": total_count,
                "resolved_count": resolved_count,
                "unresolved_count": total_count - resolved_count,
                "severity_counts": severity_counts,
                "category_counts": category_counts
            }
        except Exception as e:
            logger.error(f"Error getting technical debt summary: {str(e)}")
            raise

# Create a global instance of the decision repository
decision_repository = DecisionRepository()
