import pytest
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

from src.storage.document.mongodb import MongoDBRepository
from src.storage.document.models import Plan, Task, TaskStatus
from tests.persistence.data_validator import DataValidator

# Test configuration
TEST_DB_NAME = "ade_test_db"
TEST_CONNECTION_STRING = "mongodb://localhost:27017"

@pytest.fixture
async def mongodb_repo():
    """Create a test MongoDB repository instance"""
    repo = MongoDBRepository(
        connection_string=TEST_CONNECTION_STRING,
        database_name=TEST_DB_NAME
    )
    await repo.initialize()
    yield repo
    # Cleanup: Drop test database after tests
    await repo.client.drop_database(TEST_DB_NAME)

@pytest.fixture
def sample_plan() -> Plan:
    """Create a sample plan for testing"""
    return Plan(
        title="Test Plan",
        description="Test Description",
        status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

@pytest.fixture
def sample_task(sample_plan) -> Task:
    """Create a sample task for testing"""
    return Task(
        title="Test Task",
        description="Test Task Description",
        plan_id=sample_plan.id,
        status=TaskStatus.PENDING,
        priority=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

class TestMongoDBCRUD:
    """Test CRUD operations for MongoDB repository"""
    
    async def test_create_and_read(self, mongodb_repo, sample_plan):
        """Test document creation and retrieval"""
        # Create plan
        created_plan = await mongodb_repo.create(sample_plan)
        assert created_plan.id is not None
        
        # Read plan
        retrieved_plan = await mongodb_repo.get(Plan, created_plan.id)
        assert retrieved_plan is not None
        assert retrieved_plan.id == created_plan.id
        
        # Validate data integrity
        differences = DataValidator.compare_documents(
            created_plan.dict(),
            retrieved_plan.dict()
        )
        assert not differences
    
    async def test_update(self, mongodb_repo, sample_plan):
        """Test document update"""
        # Create and update plan
        created_plan = await mongodb_repo.create(sample_plan)
        created_plan.title = "Updated Title"
        updated_plan = await mongodb_repo.update(created_plan)
        
        # Verify update
        retrieved_plan = await mongodb_repo.get(Plan, updated_plan.id)
        assert retrieved_plan.title == "Updated Title"
        
        # Validate data integrity
        differences = DataValidator.compare_documents(
            updated_plan.dict(),
            retrieved_plan.dict()
        )
        assert not differences
    
    async def test_delete(self, mongodb_repo, sample_plan):
        """Test document deletion"""
        # Create and delete plan
        created_plan = await mongodb_repo.create(sample_plan)
        deleted = await mongodb_repo.delete(created_plan)
        assert deleted
        
        # Verify deletion
        retrieved_plan = await mongodb_repo.get(Plan, created_plan.id)
        assert retrieved_plan is None
    
    async def test_bulk_operations(self, mongodb_repo, sample_plan):
        """Test bulk CRUD operations"""
        # Create multiple plans
        plans = [Plan(**sample_plan.dict()) for _ in range(5)]
        created_plans = await mongodb_repo.bulk_create(plans)
        assert len(created_plans) == 5
        
        # Update multiple plans
        for plan in created_plans:
            plan.title = f"Updated {plan.title}"
        updated_plans = await mongodb_repo.bulk_update(created_plans)
        assert len(updated_plans) == 5
        
        # Delete multiple plans
        deleted_count = await mongodb_repo.bulk_delete(updated_plans)
        assert deleted_count == 5

class TestMongoDBTransactions:
    """Test transaction operations"""
    
    async def test_transaction_commit(self, mongodb_repo, sample_plan, sample_task):
        """Test successful transaction commit"""
        async def transaction_operation(session):
            # Create plan and task in transaction
            created_plan = await mongodb_repo.create(sample_plan)
            sample_task.plan_id = created_plan.id
            created_task = await mongodb_repo.create(sample_task)
            return created_plan, created_task
        
        plan, task = await mongodb_repo._with_transaction(transaction_operation)
        
        # Verify transaction results
        retrieved_plan = await mongodb_repo.get(Plan, plan.id)
        retrieved_task = await mongodb_repo.get(Task, task.id)
        assert retrieved_plan is not None
        assert retrieved_task is not None
        assert retrieved_task.plan_id == plan.id
    
    async def test_transaction_rollback(self, mongodb_repo, sample_plan, sample_task):
        """Test transaction rollback on error"""
        async def failing_transaction(session):
            # Create plan and fail on task creation
            created_plan = await mongodb_repo.create(sample_plan)
            sample_task.plan_id = created_plan.id
            await mongodb_repo.create(sample_task)
            raise ValueError("Simulated error")
        
        # Verify transaction rollback
        with pytest.raises(ValueError):
            await mongodb_repo._with_transaction(failing_transaction)
        
        # Verify no documents were created
        plans = await mongodb_repo.find(Plan, {})
        tasks = await mongodb_repo.find(Task, {})
        assert len(plans) == 0
        assert len(tasks) == 0

class TestMongoDBConcurrency:
    """Test concurrent operations"""
    
    async def test_concurrent_writes(self, mongodb_repo, sample_plan):
        """Test concurrent write operations"""
        async def write_operation(plan_id: str):
            plan = await mongodb_repo.get(Plan, plan_id)
            plan.title = f"Concurrent Update {plan_id}"
            return await mongodb_repo.update(plan)
        
        # Create initial plan
        created_plan = await mongodb_repo.create(sample_plan)
        
        # Perform concurrent updates
        tasks = [write_operation(created_plan.id) for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # Verify all updates completed
        assert len(results) == 10
        retrieved_plan = await mongodb_repo.get(Plan, created_plan.id)
        assert retrieved_plan is not None
    
    async def test_concurrent_reads(self, mongodb_repo, sample_plan):
        """Test concurrent read operations"""
        # Create test data
        created_plan = await mongodb_repo.create(sample_plan)
        
        async def read_operation():
            return await mongodb_repo.get(Plan, created_plan.id)
        
        # Perform concurrent reads
        tasks = [read_operation() for _ in range(20)]
        results = await asyncio.gather(*tasks)
        
        # Verify all reads returned consistent data
        assert len(results) == 20
        assert all(result is not None for result in results)
        assert all(result.id == created_plan.id for result in results)

class TestMongoDBIndexes:
    """Test index operations and performance"""
    
    async def test_index_creation(self, mongodb_repo):
        """Test index creation and validation"""
        # Get existing indexes
        plan_indexes = await mongodb_repo.db.plans.list_indexes().to_list(None)
        task_indexes = await mongodb_repo.db.tasks.list_indexes().to_list(None)
        
        # Validate required indexes exist
        missing_plan_indexes = DataValidator.validate_indexes(
            plan_indexes,
            mongodb_repo.get_plan_indexes()
        )
        missing_task_indexes = DataValidator.validate_indexes(
            task_indexes,
            mongodb_repo.get_task_indexes()
        )
        
        assert not missing_plan_indexes
        assert not missing_task_indexes
    
    async def test_index_performance(self, mongodb_repo, sample_plan):
        """Test index performance with large datasets"""
        # Create test data
        plans = [Plan(**sample_plan.dict()) for _ in range(1000)]
        await mongodb_repo.bulk_create(plans)
        
        # Test query performance with and without index
        start_time = datetime.utcnow()
        results_with_index = await mongodb_repo.find(
            Plan,
            {"status": "active"},
            sort=[("created_at", -1)]
        )
        indexed_query_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Drop index temporarily
        await mongodb_repo.db.plans.drop_index("plan_status_idx")
        
        start_time = datetime.utcnow()
        results_without_index = await mongodb_repo.find(
            Plan,
            {"status": "active"},
            sort=[("created_at", -1)]
        )
        unindexed_query_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Verify index improves performance
        assert indexed_query_time < unindexed_query_time
        
        # Restore index
        await mongodb_repo.initialize() 