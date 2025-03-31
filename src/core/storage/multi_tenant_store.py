from typing import Dict, List, Optional, Any, Type, TypeVar, Generic, ContextManager, Union
from datetime import datetime
import logging
from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import threading
from abc import ABC, abstractmethod
import uuid
import json
import os
import shutil
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import hashlib
from pathlib import Path
import subprocess
from typing import Optional, List, Dict, Any
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type variables for generic type hints
T = TypeVar('T')

class TenantIsolationStrategy(Enum):
    SCHEMA_BASED = "schema_based"
    ROW_BASED = "row_based"

@dataclass
class TenantContext:
    tenant_id: str
    schema_name: Optional[str] = None
    database_url: Optional[str] = None
    isolation_strategy: TenantIsolationStrategy = TenantIsolationStrategy.SCHEMA_BASED
    created_at: datetime = datetime.utcnow()
    metadata: Dict[str, Any] = None
    encryption_key: Optional[bytes] = None
    backup_config: Optional[Dict[str, Any]] = None

class TenantEncryption:
    """Handles tenant-specific encryption of sensitive data."""
    
    def __init__(self, tenant_id: str, encryption_key: Optional[bytes] = None):
        self.tenant_id = tenant_id
        self.encryption_key = encryption_key or self._generate_key()
        self.fernet = Fernet(self.encryption_key)
        
    def _generate_key(self) -> bytes:
        """Generate a new encryption key for the tenant."""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.tenant_id.encode()))
        return key
        
    def encrypt(self, data: str) -> str:
        """Encrypt data for the tenant."""
        return self.fernet.encrypt(data.encode()).decode()
        
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data for the tenant."""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
        
    def rotate_key(self) -> bytes:
        """Rotate the encryption key for the tenant."""
        self.encryption_key = self._generate_key()
        self.fernet = Fernet(self.encryption_key)
        return self.encryption_key

class TenantBackupManager:
    """Manages tenant-specific database backups."""
    
    def __init__(self, backup_dir: str, tenant_id: str):
        self.backup_dir = Path(backup_dir)
        self.tenant_id = tenant_id
        self.tenant_backup_dir = self.backup_dir / tenant_id
        self.tenant_backup_dir.mkdir(parents=True, exist_ok=True)
        
    def create_backup(self, database_url: str) -> str:
        """Create a backup of the tenant's database."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.tenant_backup_dir / f"backup_{timestamp}.sql"
        
        # Use pg_dump for PostgreSQL databases
        if database_url.startswith("postgresql"):
            subprocess.run([
                "pg_dump",
                database_url,
                "-f", str(backup_file)
            ], check=True)
            
        return str(backup_file)
        
    def restore_backup(self, backup_file: str, database_url: str) -> None:
        """Restore a backup for the tenant's database."""
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
        # Use psql for PostgreSQL databases
        if database_url.startswith("postgresql"):
            subprocess.run([
                "psql",
                database_url,
                "-f", backup_file
            ], check=True)
            
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all backups for the tenant."""
        backups = []
        for backup_file in self.tenant_backup_dir.glob("backup_*.sql"):
            backups.append({
                "file": str(backup_file),
                "created_at": datetime.fromtimestamp(backup_file.stat().st_mtime),
                "size": backup_file.stat().st_size
            })
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)
        
    def cleanup_old_backups(self, max_backups: int = 5) -> None:
        """Clean up old backups, keeping only the most recent ones."""
        backups = self.list_backups()
        if len(backups) > max_backups:
            for backup in backups[max_backups:]:
                os.remove(backup["file"])

class CrossTenantPrevention:
    """Prevents cross-tenant data access."""
    
    def __init__(self):
        self._tenant_context = ContextVar('tenant_context', default=None)
        
    def validate_tenant_access(self, tenant_id: str) -> None:
        """Validate that the current context matches the requested tenant."""
        current_tenant = self._tenant_context.get()
        if not current_tenant or current_tenant.tenant_id != tenant_id:
            raise ValueError("Cross-tenant access attempted")
            
    def set_tenant_context(self, tenant: TenantContext) -> None:
        """Set the current tenant context."""
        self._tenant_context.set(tenant)
        
    def clear_tenant_context(self) -> None:
        """Clear the current tenant context."""
        self._tenant_context.set(None)

class TenantContextManager:
    """Manages tenant context for database operations."""
    
    def __init__(self):
        self._context: ContextVar[Optional[TenantContext]] = ContextVar('tenant_context', default=None)
        self._lock = threading.Lock()
        
    @property
    def current_tenant(self) -> Optional[TenantContext]:
        """Get current tenant context."""
        return self._context.get()
        
    def set_tenant(self, tenant: TenantContext) -> None:
        """Set current tenant context."""
        self._context.set(tenant)
        
    def clear_tenant(self) -> None:
        """Clear current tenant context."""
        self._context.set(None)
        
    def __enter__(self) -> TenantContext:
        """Context manager entry."""
        return self.current_tenant
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.clear_tenant()

class ConnectionManager:
    """Manages database connections for different tenants."""
    
    def __init__(self, default_url: str, pool_size: int = 5, max_overflow: int = 10):
        self.default_url = default_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self._engines: Dict[str, sa.engine.Engine] = {}
        self._sessions: Dict[str, sessionmaker] = {}
        self._lock = threading.Lock()
        self._cross_tenant_prevention = CrossTenantPrevention()
        
    def get_engine(self, tenant_id: str, database_url: Optional[str] = None) -> sa.engine.Engine:
        """Get SQLAlchemy engine for tenant."""
        self._cross_tenant_prevention.validate_tenant_access(tenant_id)
        
        with self._lock:
            if tenant_id not in self._engines:
                url = database_url or self.default_url
                self._engines[tenant_id] = sa.create_engine(
                    url,
                    poolclass=QueuePool,
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                    pool_pre_ping=True
                )
            return self._engines[tenant_id]
            
    def get_session(self, tenant_id: str) -> sessionmaker:
        """Get session factory for tenant."""
        self._cross_tenant_prevention.validate_tenant_access(tenant_id)
        
        with self._lock:
            if tenant_id not in self._sessions:
                engine = self.get_engine(tenant_id)
                self._sessions[tenant_id] = sessionmaker(
                    bind=engine,
                    autocommit=False,
                    autoflush=False
                )
            return self._sessions[tenant_id]
            
    def close_all(self) -> None:
        """Close all database connections."""
        for engine in self._engines.values():
            engine.dispose()
        self._engines.clear()
        self._sessions.clear()

class MultiTenantRepository(ABC, Generic[T]):
    """Base class for multi-tenant repositories."""
    
    def __init__(
        self,
        model_class: Type[T],
        connection_manager: ConnectionManager,
        tenant_context_manager: TenantContextManager
    ):
        self.model_class = model_class
        self.connection_manager = connection_manager
        self.tenant_context_manager = tenant_context_manager
        
    @abstractmethod
    def get_session(self) -> Session:
        """Get database session for current tenant."""
        pass
        
    def get_by_id(self, id: str) -> Optional[T]:
        """Get entity by ID with tenant isolation."""
        tenant = self.tenant_context_manager.current_tenant
        if not tenant:
            raise ValueError("No tenant context set")
            
        session = self.get_session()
        try:
            query = session.query(self.model_class).filter_by(id=id)
            
            if tenant.isolation_strategy == TenantIsolationStrategy.ROW_BASED:
                query = query.filter_by(tenant_id=tenant.tenant_id)
                
            return query.first()
        finally:
            session.close()
            
    def get_all(self) -> List[T]:
        """Get all entities with tenant isolation."""
        tenant = self.tenant_context_manager.current_tenant
        if not tenant:
            raise ValueError("No tenant context set")
            
        session = self.get_session()
        try:
            query = session.query(self.model_class)
            
            if tenant.isolation_strategy == TenantIsolationStrategy.ROW_BASED:
                query = query.filter_by(tenant_id=tenant.tenant_id)
                
            return query.all()
        finally:
            session.close()
            
    def create(self, entity: T) -> T:
        """Create entity with tenant isolation."""
        tenant = self.tenant_context_manager.current_tenant
        if not tenant:
            raise ValueError("No tenant context set")
            
        session = self.get_session()
        try:
            if tenant.isolation_strategy == TenantIsolationStrategy.ROW_BASED:
                entity.tenant_id = tenant.tenant_id
                
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return entity
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
            
    def update(self, entity: T) -> T:
        """Update entity with tenant isolation."""
        tenant = self.tenant_context_manager.current_tenant
        if not tenant:
            raise ValueError("No tenant context set")
            
        session = self.get_session()
        try:
            if tenant.isolation_strategy == TenantIsolationStrategy.ROW_BASED:
                existing = session.query(self.model_class).filter_by(
                    id=entity.id,
                    tenant_id=tenant.tenant_id
                ).first()
                if not existing:
                    raise ValueError("Entity not found or not accessible")
                    
            session.merge(entity)
            session.commit()
            session.refresh(entity)
            return entity
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
            
    def delete(self, id: str) -> bool:
        """Delete entity with tenant isolation."""
        tenant = self.tenant_context_manager.current_tenant
        if not tenant:
            raise ValueError("No tenant context set")
            
        session = self.get_session()
        try:
            query = session.query(self.model_class).filter_by(id=id)
            
            if tenant.isolation_strategy == TenantIsolationStrategy.ROW_BASED:
                query = query.filter_by(tenant_id=tenant.tenant_id)
                
            result = query.delete()
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

class SchemaBasedRepository(MultiTenantRepository[T]):
    """Repository implementation for schema-based tenant isolation."""
    
    def __init__(
        self,
        model_class: Type[T],
        connection_manager: ConnectionManager,
        tenant_context_manager: TenantContextManager,
        encryption: Optional[TenantEncryption] = None
    ):
        super().__init__(model_class, connection_manager, tenant_context_manager)
        self.encryption = encryption
        
    def get_session(self) -> Session:
        tenant = self.tenant_context_manager.current_tenant
        if not tenant or not tenant.schema_name:
            raise ValueError("No tenant context or schema name set")
            
        session = self.connection_manager.get_session(tenant.tenant_id)()
        session.execute(f"SET search_path TO {tenant.schema_name}")
        return session
        
    def _encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive data before storage."""
        if not self.encryption:
            return data
            
        encrypted_data = {}
        for key, value in data.items():
            if key in self.model_class.__sensitive_fields__:
                encrypted_data[key] = self.encryption.encrypt(str(value))
            else:
                encrypted_data[key] = value
        return encrypted_data
        
    def _decrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive data after retrieval."""
        if not self.encryption:
            return data
            
        decrypted_data = {}
        for key, value in data.items():
            if key in self.model_class.__sensitive_fields__:
                decrypted_data[key] = self.encryption.decrypt(str(value))
            else:
                decrypted_data[key] = value
        return decrypted_data

class RowBasedRepository(MultiTenantRepository[T]):
    """Repository implementation for row-based tenant isolation."""
    
    def get_session(self) -> Session:
        tenant = self.tenant_context_manager.current_tenant
        if not tenant:
            raise ValueError("No tenant context set")
            
        return self.connection_manager.get_session(tenant.tenant_id)()

class MultiTenantStore:
    """Main class for managing multi-tenant data storage."""
    
    def __init__(
        self,
        default_database_url: str,
        isolation_strategy: TenantIsolationStrategy = TenantIsolationStrategy.SCHEMA_BASED,
        backup_dir: Optional[str] = None
    ):
        self.connection_manager = ConnectionManager(default_database_url)
        self.tenant_context_manager = TenantContextManager()
        self.isolation_strategy = isolation_strategy
        self.backup_dir = backup_dir
        self._encryption: Dict[str, TenantEncryption] = {}
        self._backup_managers: Dict[str, TenantBackupManager] = {}
        
    def get_repository(
        self,
        model_class: Type[T],
        tenant_id: Optional[str] = None
    ) -> MultiTenantRepository[T]:
        """Get repository for model class."""
        tenant_id = tenant_id or self.tenant_context_manager.current_tenant.tenant_id
        encryption = self._get_encryption(tenant_id)
        
        if self.isolation_strategy == TenantIsolationStrategy.SCHEMA_BASED:
            return SchemaBasedRepository(
                model_class,
                self.connection_manager,
                self.tenant_context_manager,
                encryption
            )
        else:
            return RowBasedRepository(
                model_class,
                self.connection_manager,
                self.tenant_context_manager
            )
            
    def _get_encryption(self, tenant_id: str) -> TenantEncryption:
        """Get or create encryption for tenant."""
        if tenant_id not in self._encryption:
            self._encryption[tenant_id] = TenantEncryption(tenant_id)
        return self._encryption[tenant_id]
        
    def _get_backup_manager(self, tenant_id: str) -> TenantBackupManager:
        """Get or create backup manager for tenant."""
        if not self.backup_dir:
            raise ValueError("Backup directory not configured")
            
        if tenant_id not in self._backup_managers:
            self._backup_managers[tenant_id] = TenantBackupManager(
                self.backup_dir,
                tenant_id
            )
        return self._backup_managers[tenant_id]
        
    def create_backup(self, tenant_id: str) -> str:
        """Create a backup for a tenant."""
        tenant = self.tenant_context_manager.current_tenant
        if not tenant or tenant.tenant_id != tenant_id:
            raise ValueError("Invalid tenant context")
            
        backup_manager = self._get_backup_manager(tenant_id)
        return backup_manager.create_backup(tenant.database_url or self.connection_manager.default_url)
        
    def restore_backup(self, tenant_id: str, backup_file: str) -> None:
        """Restore a backup for a tenant."""
        tenant = self.tenant_context_manager.current_tenant
        if not tenant or tenant.tenant_id != tenant_id:
            raise ValueError("Invalid tenant context")
            
        backup_manager = self._get_backup_manager(tenant_id)
        backup_manager.restore_backup(
            backup_file,
            tenant.database_url or self.connection_manager.default_url
        )
        
    def list_backups(self, tenant_id: str) -> List[Dict[str, Any]]:
        """List backups for a tenant."""
        tenant = self.tenant_context_manager.current_tenant
        if not tenant or tenant.tenant_id != tenant_id:
            raise ValueError("Invalid tenant context")
            
        backup_manager = self._get_backup_manager(tenant_id)
        return backup_manager.list_backups()
        
    def rotate_encryption_key(self, tenant_id: str) -> bytes:
        """Rotate encryption key for a tenant."""
        tenant = self.tenant_context_manager.current_tenant
        if not tenant or tenant.tenant_id != tenant_id:
            raise ValueError("Invalid tenant context")
            
        encryption = self._get_encryption(tenant_id)
        return encryption.rotate_key()
        
    def set_tenant_context(
        self,
        tenant_id: str,
        schema_name: Optional[str] = None,
        database_url: Optional[str] = None,
        backup_config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Set tenant context for current thread."""
        context = TenantContext(
            tenant_id=tenant_id,
            schema_name=schema_name,
            database_url=database_url,
            isolation_strategy=self.isolation_strategy,
            backup_config=backup_config
        )
        self.tenant_context_manager.set_tenant(context)
        self.connection_manager._cross_tenant_prevention.set_tenant_context(context)
        
    def clear_tenant_context(self) -> None:
        """Clear tenant context for current thread."""
        self.tenant_context_manager.clear_tenant()
        self.connection_manager._cross_tenant_prevention.clear_tenant_context()
        
    def close(self) -> None:
        """Close all database connections."""
        self.connection_manager.close_all()
        
    def __enter__(self) -> 'MultiTenantStore':
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close() 