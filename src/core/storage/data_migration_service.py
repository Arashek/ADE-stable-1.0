from typing import Dict, List, Optional, Any, Type, TypeVar, Generic, Union, Callable
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import threading
from abc import ABC, abstractmethod
from functools import wraps
import json
import os
from pathlib import Path
import yaml
import hashlib
import subprocess
from sqlalchemy import text
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MigrationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class MigrationVersion:
    version: str
    description: str
    created_at: datetime
    checksum: str
    dependencies: List[str]
    status: MigrationStatus = MigrationStatus.PENDING
    executed_at: Optional[datetime] = None
    error: Optional[str] = None

class MigrationError(Exception):
    """Base class for migration errors."""
    pass

class MigrationValidationError(MigrationError):
    """Raised when migration validation fails."""
    pass

class MigrationExecutionError(MigrationError):
    """Raised when migration execution fails."""
    pass

class MigrationRollbackError(MigrationError):
    """Raised when migration rollback fails."""
    pass

class MigrationScript:
    """Represents a database migration script."""
    
    def __init__(
        self,
        version: str,
        description: str,
        up_sql: str,
        down_sql: str,
        dependencies: List[str] = None
    ):
        self.version = version
        self.description = description
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.dependencies = dependencies or []
        self.created_at = datetime.now()
        self.checksum = self._calculate_checksum()
        
    def _calculate_checksum(self) -> str:
        """Calculate checksum of migration script."""
        content = f"{self.version}{self.description}{self.up_sql}{self.down_sql}"
        return hashlib.sha256(content.encode()).hexdigest()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert migration script to dictionary."""
        return {
            "version": self.version,
            "description": self.description,
            "up_sql": self.up_sql,
            "down_sql": self.down_sql,
            "dependencies": self.dependencies,
            "created_at": self.created_at.isoformat(),
            "checksum": self.checksum
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MigrationScript':
        """Create migration script from dictionary."""
        return cls(
            version=data["version"],
            description=data["description"],
            up_sql=data["up_sql"],
            down_sql=data["down_sql"],
            dependencies=data.get("dependencies", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            checksum=data["checksum"]
        )

class MigrationValidator:
    """Validates migration scripts."""
    
    def __init__(self):
        self._sql_keywords = {
            "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP",
            "TRUNCATE", "GRANT", "REVOKE", "COMMIT", "ROLLBACK", "BEGIN", "END"
        }
        
    def validate_migration(self, migration: MigrationScript) -> None:
        """Validate migration script."""
        self._validate_version(migration.version)
        self._validate_sql(migration.up_sql)
        self._validate_sql(migration.down_sql)
        self._validate_dependencies(migration.dependencies)
        
    def _validate_version(self, version: str) -> None:
        """Validate version string format."""
        if not re.match(r"^\d{4}\.\d{2}\.\d{2}\.\d{4}$", version):
            raise MigrationValidationError(
                f"Invalid version format: {version}. Expected format: YYYY.MM.DD.NNNN"
            )
            
    def _validate_sql(self, sql: str) -> None:
        """Validate SQL statements."""
        if not sql.strip():
            raise MigrationValidationError("SQL statement cannot be empty")
            
        # Check for dangerous operations
        dangerous_ops = {"DROP", "TRUNCATE", "DELETE"}
        sql_upper = sql.upper()
        for op in dangerous_ops:
            if op in sql_upper:
                raise MigrationValidationError(
                    f"Dangerous operation '{op}' detected in SQL statement"
                )
                
    def _validate_dependencies(self, dependencies: List[str]) -> None:
        """Validate migration dependencies."""
        for dep in dependencies:
            if not re.match(r"^\d{4}\.\d{2}\.\d{2}\.\d{4}$", dep):
                raise MigrationValidationError(
                    f"Invalid dependency version format: {dep}"
                )

class MigrationExecutor:
    """Executes database migrations."""
    
    def __init__(self, session: Session):
        self.session = session
        self._lock = threading.Lock()
        
    def execute_migration(self, migration: MigrationScript) -> None:
        """Execute migration script."""
        with self._lock:
            try:
                # Begin transaction
                self.session.begin()
                
                # Execute up migration
                for statement in self._split_sql(migration.up_sql):
                    self.session.execute(text(statement))
                    
                # Update migration version
                self._update_migration_version(migration)
                
                # Commit transaction
                self.session.commit()
                
            except Exception as e:
                self.session.rollback()
                raise MigrationExecutionError(f"Migration failed: {str(e)}")
                
    def rollback_migration(self, migration: MigrationScript) -> None:
        """Rollback migration script."""
        with self._lock:
            try:
                # Begin transaction
                self.session.begin()
                
                # Execute down migration
                for statement in self._split_sql(migration.down_sql):
                    self.session.execute(text(statement))
                    
                # Remove migration version
                self._remove_migration_version(migration)
                
                # Commit transaction
                self.session.commit()
                
            except Exception as e:
                self.session.rollback()
                raise MigrationRollbackError(f"Rollback failed: {str(e)}")
                
    def _split_sql(self, sql: str) -> List[str]:
        """Split SQL script into individual statements."""
        statements = []
        current = []
        
        for line in sql.splitlines():
            line = line.strip()
            if not line or line.startswith("--"):
                continue
                
            current.append(line)
            
            if line.endswith(";"):
                statements.append(" ".join(current))
                current = []
                
        if current:
            statements.append(" ".join(current))
            
        return statements
        
    def _update_migration_version(self, migration: MigrationScript) -> None:
        """Update migration version in database."""
        self.session.execute(
            text("""
                INSERT INTO migration_versions (
                    version, description, checksum, dependencies,
                    status, executed_at
                ) VALUES (
                    :version, :description, :checksum, :dependencies,
                    :status, :executed_at
                )
            """),
            {
                "version": migration.version,
                "description": migration.description,
                "checksum": migration.checksum,
                "dependencies": json.dumps(migration.dependencies),
                "status": MigrationStatus.COMPLETED.value,
                "executed_at": datetime.now()
            }
        )
        
    def _remove_migration_version(self, migration: MigrationScript) -> None:
        """Remove migration version from database."""
        self.session.execute(
            text("DELETE FROM migration_versions WHERE version = :version"),
            {"version": migration.version}
        )

class DataMigrationService:
    """Service for managing database migrations."""
    
    def __init__(
        self,
        session: Session,
        migrations_dir: str,
        tenant_id: Optional[str] = None
    ):
        self.session = session
        self.migrations_dir = Path(migrations_dir)
        self.tenant_id = tenant_id
        self.validator = MigrationValidator()
        self.executor = MigrationExecutor(session)
        self._ensure_migrations_table()
        
    def _ensure_migrations_table(self) -> None:
        """Ensure migration versions table exists."""
        self.session.execute(
            text("""
                CREATE TABLE IF NOT EXISTS migration_versions (
                    version VARCHAR(20) PRIMARY KEY,
                    description TEXT,
                    checksum VARCHAR(64),
                    dependencies JSONB,
                    status VARCHAR(20),
                    executed_at TIMESTAMP,
                    error TEXT
                )
            """)
        )
        self.session.commit()
        
    def create_migration(
        self,
        description: str,
        up_sql: str,
        down_sql: str,
        dependencies: List[str] = None
    ) -> MigrationScript:
        """Create new migration script."""
        version = self._generate_version()
        migration = MigrationScript(
            version=version,
            description=description,
            up_sql=up_sql,
            down_sql=down_sql,
            dependencies=dependencies
        )
        
        # Validate migration
        self.validator.validate_migration(migration)
        
        # Save migration script
        migration_file = self.migrations_dir / f"{version}_{description}.sql"
        with open(migration_file, "w") as f:
            yaml.dump(migration.to_dict(), f)
            
        return migration
        
    def _generate_version(self) -> str:
        """Generate new migration version."""
        timestamp = datetime.now()
        return timestamp.strftime("%Y.%m.%d.%H%M")
        
    def get_pending_migrations(self) -> List[MigrationScript]:
        """Get list of pending migrations."""
        executed_versions = self._get_executed_versions()
        all_migrations = self._load_migrations()
        
        return [
            migration for migration in all_migrations
            if migration.version not in executed_versions
            and all(dep in executed_versions for dep in migration.dependencies)
        ]
        
    def _get_executed_versions(self) -> Set[str]:
        """Get set of executed migration versions."""
        result = self.session.execute(
            text("SELECT version FROM migration_versions WHERE status = :status"),
            {"status": MigrationStatus.COMPLETED.value}
        )
        return {row[0] for row in result}
        
    def _load_migrations(self) -> List[MigrationScript]:
        """Load all migration scripts."""
        migrations = []
        for file in self.migrations_dir.glob("*.sql"):
            with open(file) as f:
                data = yaml.safe_load(f)
                migrations.append(MigrationScript.from_dict(data))
        return sorted(migrations, key=lambda x: x.version)
        
    def execute_pending_migrations(self) -> List[MigrationScript]:
        """Execute all pending migrations."""
        executed = []
        pending = self.get_pending_migrations()
        
        for migration in pending:
            try:
                self.executor.execute_migration(migration)
                executed.append(migration)
                logger.info(f"Executed migration: {migration.version}")
            except Exception as e:
                logger.error(f"Failed to execute migration {migration.version}: {str(e)}")
                raise
                
        return executed
        
    def rollback_migration(self, version: str) -> None:
        """Rollback specific migration."""
        migration = self._get_migration_by_version(version)
        if not migration:
            raise ValueError(f"Migration not found: {version}")
            
        try:
            self.executor.rollback_migration(migration)
            logger.info(f"Rolled back migration: {version}")
        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {str(e)}")
            raise
            
    def _get_migration_by_version(self, version: str) -> Optional[MigrationScript]:
        """Get migration script by version."""
        for migration in self._load_migrations():
            if migration.version == version:
                return migration
        return None
        
    def get_migration_status(self, version: str) -> Optional[MigrationStatus]:
        """Get status of specific migration."""
        result = self.session.execute(
            text("SELECT status FROM migration_versions WHERE version = :version"),
            {"version": version}
        )
        row = result.first()
        return MigrationStatus(row[0]) if row else None
        
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history."""
        result = self.session.execute(
            text("""
                SELECT version, description, checksum, dependencies,
                       status, executed_at, error
                FROM migration_versions
                ORDER BY version
            """)
        )
        
        return [
            {
                "version": row[0],
                "description": row[1],
                "checksum": row[2],
                "dependencies": json.loads(row[3]),
                "status": row[4],
                "executed_at": row[5],
                "error": row[6]
            }
            for row in result
        ]
        
    def validate_migrations(self) -> List[str]:
        """Validate all migration scripts."""
        errors = []
        for migration in self._load_migrations():
            try:
                self.validator.validate_migration(migration)
            except MigrationValidationError as e:
                errors.append(f"Migration {migration.version}: {str(e)}")
        return errors
        
    def get_schema_version(self) -> Optional[str]:
        """Get current schema version."""
        result = self.session.execute(
            text("""
                SELECT version FROM migration_versions
                WHERE status = :status
                ORDER BY version DESC
                LIMIT 1
            """),
            {"status": MigrationStatus.COMPLETED.value}
        )
        row = result.first()
        return row[0] if row else None 