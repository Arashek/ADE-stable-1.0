import pytest
import asyncio
from datetime import datetime
import os
import shutil
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

from src.storage.document.mongodb import MongoDBRepository
from src.storage.document.models import Plan, Task, TaskStatus
from tests.persistence.data_validator import DataValidator

# Test configuration
TEST_DB_NAME = "ade_test_db"
TEST_CONNECTION_STRING = "mongodb://localhost:27017"
BACKUP_DIR = "test_backups"
RESTORE_DIR = "test_restore"

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

@pytest.fixture
def backup_directories():
    """Create and cleanup backup directories"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(RESTORE_DIR, exist_ok=True)
    yield
    shutil.rmtree(BACKUP_DIR, ignore_errors=True)
    shutil.rmtree(RESTORE_DIR, ignore_errors=True)

class TestBackupProcedures:
    """Test backup procedures"""
    
    async def test_full_backup(self, mongodb_repo, sample_plan, backup_directories):
        """Test full database backup"""
        # Create test data
        created_plan = await mongodb_repo.create(sample_plan)
        
        # Perform backup
        backup_path = os.path.join(BACKUP_DIR, "full_backup")
        await mongodb_repo.backup_database(backup_path)
        
        # Verify backup files
        assert os.path.exists(backup_path)
        assert os.path.exists(os.path.join(backup_path, "plans.bson"))
        assert os.path.exists(os.path.join(backup_path, "tasks.bson"))
        
        # Verify backup integrity
        backup_data = await mongodb_repo.restore_database(backup_path)
        assert backup_data["plans"] == 1
        assert backup_data["tasks"] == 0
    
    async def test_incremental_backup(self, mongodb_repo, sample_plan, backup_directories):
        """Test incremental backup"""
        # Create initial data
        created_plan = await mongodb_repo.create(sample_plan)
        
        # Perform full backup
        full_backup_path = os.path.join(BACKUP_DIR, "full_backup")
        await mongodb_repo.backup_database(full_backup_path)
        
        # Create additional data
        new_plan = await mongodb_repo.create(sample_plan)
        
        # Perform incremental backup
        incremental_backup_path = os.path.join(BACKUP_DIR, "incremental_backup")
        await mongodb_repo.backup_database(
            incremental_backup_path,
            incremental=True,
            last_backup_path=full_backup_path
        )
        
        # Verify incremental backup
        assert os.path.exists(incremental_backup_path)
        assert os.path.exists(os.path.join(incremental_backup_path, "plans.bson"))
        
        # Verify backup contains only new data
        backup_data = await mongodb_repo.restore_database(incremental_backup_path)
        assert backup_data["plans"] == 1  # Only new plan

class TestRestorationProcedures:
    """Test restoration procedures"""
    
    async def test_full_restore(self, mongodb_repo, sample_plan, backup_directories):
        """Test full database restoration"""
        # Create test data
        created_plan = await mongodb_repo.create(sample_plan)
        
        # Perform backup
        backup_path = os.path.join(BACKUP_DIR, "full_backup")
        await mongodb_repo.backup_database(backup_path)
        
        # Drop database
        await mongodb_repo.client.drop_database(TEST_DB_NAME)
        
        # Restore database
        restore_data = await mongodb_repo.restore_database(backup_path)
        assert restore_data["plans"] == 1
        
        # Verify restored data
        restored_plan = await mongodb_repo.get(Plan, created_plan.id)
        assert restored_plan is not None
        assert restored_plan.id == created_plan.id
        
        # Verify data integrity
        differences = DataValidator.compare_documents(
            created_plan.dict(),
            restored_plan.dict()
        )
        assert not differences
    
    async def test_partial_restore(self, mongodb_repo, sample_plan, sample_task, backup_directories):
        """Test partial database restoration"""
        # Create test data
        created_plan = await mongodb_repo.create(sample_plan)
        created_task = await mongodb_repo.create(sample_task)
        
        # Perform backup
        backup_path = os.path.join(BACKUP_DIR, "partial_backup")
        await mongodb_repo.backup_database(backup_path)
        
        # Drop database
        await mongodb_repo.client.drop_database(TEST_DB_NAME)
        
        # Restore only plans collection
        restore_data = await mongodb_repo.restore_database(
            backup_path,
            collections=["plans"]
        )
        assert restore_data["plans"] == 1
        assert "tasks" not in restore_data
        
        # Verify partial restoration
        restored_plan = await mongodb_repo.get(Plan, created_plan.id)
        assert restored_plan is not None
        restored_task = await mongodb_repo.get(Task, created_task.id)
        assert restored_task is None

class TestPartialRecovery:
    """Test partial recovery scenarios"""
    
    async def test_corrupted_collection_recovery(self, mongodb_repo, sample_plan, backup_directories):
        """Test recovery from corrupted collection"""
        # Create test data
        created_plan = await mongodb_repo.create(sample_plan)
        
        # Perform backup
        backup_path = os.path.join(BACKUP_DIR, "corrupted_backup")
        await mongodb_repo.backup_database(backup_path)
        
        # Corrupt plans collection
        await mongodb_repo.db.plans.update_one(
            {"_id": created_plan.id},
            {"$set": {"status": "invalid_status"}}
        )
        
        # Verify corruption
        corrupted_plan = await mongodb_repo.get(Plan, created_plan.id)
        assert corrupted_plan.status == "invalid_status"
        
        # Restore only plans collection
        restore_data = await mongodb_repo.restore_database(
            backup_path,
            collections=["plans"]
        )
        assert restore_data["plans"] == 1
        
        # Verify recovery
        recovered_plan = await mongodb_repo.get(Plan, created_plan.id)
        assert recovered_plan.status == "active"
    
    async def test_missing_index_recovery(self, mongodb_repo, sample_plan, backup_directories):
        """Test recovery from missing indexes"""
        # Create test data
        created_plan = await mongodb_repo.create(sample_plan)
        
        # Perform backup
        backup_path = os.path.join(BACKUP_DIR, "index_backup")
        await mongodb_repo.backup_database(backup_path)
        
        # Drop indexes
        await mongodb_repo.db.plans.drop_indexes()
        
        # Verify missing indexes
        plan_indexes = await mongodb_repo.db.plans.list_indexes().to_list(None)
        missing_indexes = DataValidator.validate_indexes(
            plan_indexes,
            mongodb_repo.get_plan_indexes()
        )
        assert missing_indexes
        
        # Restore database
        restore_data = await mongodb_repo.restore_database(backup_path)
        assert restore_data["plans"] == 1
        
        # Verify index recovery
        restored_indexes = await mongodb_repo.db.plans.list_indexes().to_list(None)
        missing_indexes = DataValidator.validate_indexes(
            restored_indexes,
            mongodb_repo.get_plan_indexes()
        )
        assert not missing_indexes

class TestCrossVersionCompatibility:
    """Test cross-version compatibility"""
    
    async def test_schema_version_compatibility(self, mongodb_repo, sample_plan, backup_directories):
        """Test compatibility with different schema versions"""
        # Create test data with current schema
        created_plan = await mongodb_repo.create(sample_plan)
        
        # Perform backup
        backup_path = os.path.join(BACKUP_DIR, "version_backup")
        await mongodb_repo.backup_database(backup_path)
        
        # Simulate schema version change
        plan_data = created_plan.dict()
        plan_data["schema_version"] = "1.0.0"  # Add version field
        
        # Verify backward compatibility
        schema_error = DataValidator.validate_schema(
            plan_data,
            Plan
        )
        assert not schema_error
        
        # Restore database
        restore_data = await mongodb_repo.restore_database(backup_path)
        assert restore_data["plans"] == 1
    
    async def test_data_format_compatibility(self, mongodb_repo, sample_plan, backup_directories):
        """Test compatibility with different data formats"""
        # Create test data
        created_plan = await mongodb_repo.create(sample_plan)
        
        # Perform backup
        backup_path = os.path.join(BACKUP_DIR, "format_backup")
        await mongodb_repo.backup_database(backup_path)
        
        # Modify data format (simulating old format)
        plan_data = created_plan.dict()
        plan_data["created_at"] = plan_data["created_at"].isoformat()
        plan_data["updated_at"] = plan_data["updated_at"].isoformat()
        
        # Verify format compatibility
        schema_error = DataValidator.validate_schema(
            plan_data,
            Plan
        )
        assert not schema_error
        
        # Restore database
        restore_data = await mongodb_repo.restore_database(backup_path)
        assert restore_data["plans"] == 1 