"""State manager for orchestrator persistence using MongoDB."""
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, PyMongoError
from bson import json_util

from .models import Plan, Task, HistoryEntry, PlanStatus, TaskStatus

logger = logging.getLogger(__name__)

class StateManager:
    """Manages persistence of orchestrator state using MongoDB"""
    
    def __init__(self, mongodb_uri: str, database_name: str = "ade", max_retries: int = 3):
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.max_retries = max_retries
        self.client = None
        self.db = None
        self._initialize_connection()
        self._setup_collections()
    
    def _initialize_connection(self):
        """Initialize connection to MongoDB"""
        try:
            self.client = MongoClient(self.mongodb_uri)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            logger.info(f"Connected to MongoDB: {self.database_name}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    def _setup_collections(self):
        """Set up collections and indexes"""
        try:
            # Plans collection
            if "plans" not in self.db.list_collection_names():
                self.db.create_collection("plans")
            
            self.db.plans.create_index([("id", ASCENDING)], unique=True)
            self.db.plans.create_index([("status", ASCENDING)])
            self.db.plans.create_index([("created_at", DESCENDING)])
            
            # Tasks collection
            if "tasks" not in self.db.list_collection_names():
                self.db.create_collection("tasks")
            
            self.db.tasks.create_index([("id", ASCENDING)], unique=True)
            self.db.tasks.create_index([("plan_id", ASCENDING)])
            self.db.tasks.create_index([("status", ASCENDING)])
            self.db.tasks.create_index([("created_at", DESCENDING)])
            
            # History collection
            if "orchestrator_history" not in self.db.list_collection_names():
                self.db.create_collection("orchestrator_history")
            
            self.db.orchestrator_history.create_index([("entity_id", ASCENDING)])
            self.db.orchestrator_history.create_index([("entity_type", ASCENDING)])
            self.db.orchestrator_history.create_index([("timestamp", DESCENDING)])
            
            logger.info("MongoDB collections and indexes set up successfully")
        except PyMongoError as e:
            logger.error(f"Error setting up MongoDB collections: {str(e)}")
            raise
    
    def _serialize_model(self, model):
        """Convert a Pydantic model to a dictionary for MongoDB"""
        return json.loads(model.json())
    
    def _deserialize_plan(self, data) -> Optional[Plan]:
        """Convert MongoDB data to a Plan object"""
        if not data:
            return None
        return Plan.parse_obj(data)
    
    def _deserialize_task(self, data) -> Optional[Task]:
        """Convert MongoDB data to a Task object"""
        if not data:
            return None
        return Task.parse_obj(data)
    
    def _deserialize_history(self, data) -> Optional[HistoryEntry]:
        """Convert MongoDB data to a HistoryEntry object"""
        if not data:
            return None
        return HistoryEntry.parse_obj(data)
    
    # Plan operations
    def save_plan(self, plan: Plan) -> bool:
        """Save a plan to the database"""
        try:
            plan_dict = self._serialize_model(plan)
            plan_dict["updated_at"] = datetime.now()
            
            self.db.plans.update_one(
                {"id": plan.id},
                {"$set": plan_dict},
                upsert=True
            )
            
            logger.info(f"Saved plan {plan.id}")
            return True
        except PyMongoError as e:
            logger.error(f"Error saving plan {plan.id}: {str(e)}")
            return False
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get a plan by ID"""
        try:
            plan_data = self.db.plans.find_one({"id": plan_id})
            return self._deserialize_plan(plan_data)
        except PyMongoError as e:
            logger.error(f"Error getting plan {plan_id}: {str(e)}")
            return None
    
    def get_plans(self, status: Optional[PlanStatus] = None, limit: int = 100, skip: int = 0) -> List[Plan]:
        """Get plans, optionally filtered by status"""
        try:
            query = {}
            if status:
                query["status"] = status.value
                
            plans_data = self.db.plans.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
            return [self._deserialize_plan(p) for p in plans_data]
        except PyMongoError as e:
            logger.error(f"Error getting plans: {str(e)}")
            return []
    
    def delete_plan(self, plan_id: str) -> bool:
        """Delete a plan"""
        try:
            result = self.db.plans.delete_one({"id": plan_id})
            if result.deleted_count > 0:
                logger.info(f"Deleted plan {plan_id}")
                return True
            else:
                logger.warning(f"Plan {plan_id} not found for deletion")
                return False
        except PyMongoError as e:
            logger.error(f"Error deleting plan {plan_id}: {str(e)}")
            return False
    
    # Task operations
    def save_task(self, task: Task) -> bool:
        """Save a task to the database"""
        try:
            task_dict = self._serialize_model(task)
            task_dict["updated_at"] = datetime.now()
            
            self.db.tasks.update_one(
                {"id": task.id},
                {"$set": task_dict},
                upsert=True
            )
            
            logger.info(f"Saved task {task.id}")
            return True
        except PyMongoError as e:
            logger.error(f"Error saving task {task.id}: {str(e)}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        try:
            task_data = self.db.tasks.find_one({"id": task_id})
            return self._deserialize_task(task_data)
        except PyMongoError as e:
            logger.error(f"Error getting task {task_id}: {str(e)}")
            return None
    
    def get_tasks(self, plan_id: Optional[str] = None, status: Optional[TaskStatus] = None, 
                 limit: int = 100, skip: int = 0) -> List[Task]:
        """Get tasks, optionally filtered by plan_id and status"""
        try:
            query = {}
            if plan_id:
                query["plan_id"] = plan_id
            if status:
                query["status"] = status.value
                
            tasks_data = self.db.tasks.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
            return [self._deserialize_task(t) for t in tasks_data]
        except PyMongoError as e:
            logger.error(f"Error getting tasks: {str(e)}")
            return []
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        try:
            result = self.db.tasks.delete_one({"id": task_id})
            if result.deleted_count > 0:
                logger.info(f"Deleted task {task_id}")
                return True
            else:
                logger.warning(f"Task {task_id} not found for deletion")
                return False
        except PyMongoError as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            return False
    
    # History operations
    def add_history_entry(self, entry: HistoryEntry) -> bool:
        """Add a history entry"""
        try:
            entry_dict = self._serialize_model(entry)
            self.db.orchestrator_history.insert_one(entry_dict)
            return True
        except PyMongoError as e:
            logger.error(f"Error adding history entry: {str(e)}")
            return False
    
    def get_history(self, entity_type: Optional[str] = None, entity_id: Optional[str] = None, 
                   limit: int = 100, skip: int = 0) -> List[HistoryEntry]:
        """Get history entries, optionally filtered by entity_type and entity_id"""
        try:
            query = {}
            if entity_type:
                query["entity_type"] = entity_type
            if entity_id:
                query["entity_id"] = entity_id
                
            history_data = self.db.orchestrator_history.find(query).sort("timestamp", DESCENDING).skip(skip).limit(limit)
            return [self._deserialize_history(h) for h in history_data]
        except PyMongoError as e:
            logger.error(f"Error getting history: {str(e)}")
            return []
    
    # Helper methods for common operations
    def get_active_plans(self) -> List[Plan]:
        """Get all active plans (not in terminal state)"""
        return self.get_plans(status=PlanStatus.EXECUTING)
    
    def get_active_tasks(self, plan_id: Optional[str] = None) -> List[Task]:
        """Get all active tasks (not in terminal state)"""
        return self.get_tasks(plan_id=plan_id, status=TaskStatus.RUNNING)
    
    def get_plan_tasks(self, plan_id: str) -> List[Task]:
        """Get all tasks associated with a plan"""
        return self.get_tasks(plan_id=plan_id)
    
    def get_plan_history(self, plan_id: str, limit: int = 100) -> List[HistoryEntry]:
        """Get history entries for a specific plan"""
        return self.get_history(entity_type="plan", entity_id=plan_id, limit=limit)
    
    def get_task_history(self, task_id: str, limit: int = 100) -> List[HistoryEntry]:
        """Get history entries for a specific task"""
        return self.get_history(entity_type="task", entity_id=task_id, limit=limit)
    
    def record_status_change(self, entity_type: str, entity_id: str, old_status: str, new_status: str, details: Optional[str] = None) -> bool:
        """Record a status change in the history"""
        entry = HistoryEntry.create_status_change(
            entity_type=entity_type,
            entity_id=entity_id,
            old_status=old_status,
            new_status=new_status,
            details=details
        )
        return self.add_history_entry(entry)
    
    def record_error(self, entity_type: str, entity_id: str, error: str, details: Optional[str] = None) -> bool:
        """Record an error in the history"""
        entry = HistoryEntry.create_error(
            entity_type=entity_type,
            entity_id=entity_id,
            error=error,
            details=details
        )
        return self.add_history_entry(entry)
    
    def close(self):
        """Close the database connection"""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection") 