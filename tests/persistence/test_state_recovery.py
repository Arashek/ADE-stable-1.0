import pytest
import asyncio
from datetime import datetime
import signal
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

class TestSystemRestart:
    """Test system restart scenarios"""
    
    async def test_repository_reinitialization(self, mongodb_repo, sample_plan):
        """Test repository reinitialization after restart"""
        # Create test data
        created_plan = await mongodb_repo.create(sample_plan)
        
        # Simulate system restart by creating new repository instance
        new_repo = MongoDBRepository(
            connection_string=TEST_CONNECTION_STRING,
            database_name=TEST_DB_NAME
        )
        await new_repo.initialize()
        
        # Verify data persistence
        retrieved_plan = await new_repo.get(Plan, created_plan.id)
        assert retrieved_plan is not None
        assert retrieved_plan.id == created_plan.id
        
        # Verify index recreation
        plan_indexes = await new_repo.db.plans.list_indexes().to_list(None)
        missing_indexes = DataValidator.validate_indexes(
            plan_indexes,
            new_repo.get_plan_indexes()
        )
        assert not missing_indexes
    
    async def test_connection_pool_recovery(self, mongodb_repo, sample_plan):
        """Test connection pool recovery after restart"""
        # Create test data
        created_plan = await mongodb_repo.create(sample_plan)
        
        # Simulate connection pool exhaustion
        async def exhaust_connections():
            tasks = []
            for _ in range(150):  # Exceed max_pool_size
                tasks.append(mongodb_repo.get(Plan, created_plan.id))
            await asyncio.gather(*tasks)
        
        # Verify connection pool recovers
        await exhaust_connections()
        retrieved_plan = await mongodb_repo.get(Plan, created_plan.id)
        assert retrieved_plan is not None

class TestInterruptedOperations:
    """Test recovery from interrupted operations"""
    
    async def test_interrupted_transaction(self, mongodb_repo, sample_plan, sample_task):
        """Test recovery from interrupted transaction"""
        async def transaction_with_interrupt(session):
            # Start transaction
            created_plan = await mongodb_repo.create(sample_plan)
            sample_task.plan_id = created_plan.id
            
            # Simulate interruption
            os.kill(os.getpid(), signal.SIGINT)
            
            # This should not execute
            await mongodb_repo.create(sample_task)
            return created_plan
        
        # Verify transaction rollback
        with pytest.raises(KeyboardInterrupt):
            await mongodb_repo._with_transaction(transaction_with_interrupt)
        
        # Verify no partial data
        plans = await mongodb_repo.find(Plan, {})
        tasks = await mongodb_repo.find(Task, {})
        assert len(plans) == 0
        assert len(tasks) == 0
    
    async def test_interrupted_bulk_operation(self, mongodb_repo, sample_plan):
        """Test recovery from interrupted bulk operation"""
        # Create test data
        plans = [Plan(**sample_plan.dict()) for _ in range(100)]
        
        async def bulk_create_with_interrupt():
            # Start bulk create
            created = await mongodb_repo.bulk_create(plans[:50])
            
            # Simulate interruption
            os.kill(os.getpid(), signal.SIGINT)
            
            # This should not execute
            await mongodb_repo.bulk_create(plans[50:])
            return created
        
        # Verify operation rollback
        with pytest.raises(KeyboardInterrupt):
            await bulk_create_with_interrupt()
        
        # Verify no partial data
        retrieved_plans = await mongodb_repo.find(Plan, {})
        assert len(retrieved_plans) == 0

class TestStateConsistency:
    """Test state consistency validation"""
    
    async def test_data_integrity_after_restart(self, mongodb_repo, sample_plan):
        """Test data integrity after system restart"""
        # Create test data
        created_plan = await mongodb_repo.create(sample_plan)
        
        # Simulate system restart
        new_repo = MongoDBRepository(
            connection_string=TEST_CONNECTION_STRING,
            database_name=TEST_DB_NAME
        )
        await new_repo.initialize()
        
        # Verify data integrity
        retrieved_plan = await new_repo.get(Plan, created_plan.id)
        differences = DataValidator.compare_documents(
            created_plan.dict(),
            retrieved_plan.dict()
        )
        assert not differences
        
        # Verify no data corruption
        corrupted = DataValidator.check_data_corruption([retrieved_plan.dict()])
        assert not corrupted
    
    async def test_referential_integrity(self, mongodb_repo, sample_plan, sample_task):
        """Test referential integrity after operations"""
        # Create related documents
        created_plan = await mongodb_repo.create(sample_plan)
        sample_task.plan_id = created_plan.id
        created_task = await mongodb_repo.create(sample_task)
        
        # Verify referential integrity
        broken_refs = DataValidator.check_referential_integrity(
            [created_task.dict()],
            "plan_id",
            "plans"
        )
        assert not broken_refs
        
        # Delete parent document
        await mongodb_repo.delete(created_plan)
        
        # Verify referential integrity after deletion
        broken_refs = DataValidator.check_referential_integrity(
            [created_task.dict()],
            "plan_id",
            "plans"
        )
        assert broken_refs  # Should detect orphaned task

class TestSchemaValidation:
    """Test schema validation and compliance"""
    
    async def test_schema_compliance(self, mongodb_repo, sample_plan):
        """Test schema compliance after operations"""
        # Create document
        created_plan = await mongodb_repo.create(sample_plan)
        
        # Verify schema compliance
        schema_error = DataValidator.validate_schema(
            created_plan.dict(),
            Plan
        )
        assert not schema_error
        
        # Modify document to violate schema
        invalid_data = created_plan.dict()
        invalid_data["status"] = "invalid_status"
        
        # Verify schema validation catches error
        schema_error = DataValidator.validate_schema(
            invalid_data,
            Plan
        )
        assert schema_error
    
    async def test_schema_evolution(self, mongodb_repo, sample_plan):
        """Test handling of schema evolution"""
        # Create document with current schema
        created_plan = await mongodb_repo.create(sample_plan)
        
        # Simulate schema evolution by adding new field
        new_data = created_plan.dict()
        new_data["new_field"] = "test_value"
        
        # Verify backward compatibility
        schema_error = DataValidator.validate_schema(
            new_data,
            Plan
        )
        assert not schema_error  # Should handle extra fields gracefully 