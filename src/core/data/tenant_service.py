from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import uuid
from dataclasses import dataclass
import logging
from enum import Enum
import json
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from ..auth.user_management import Organization, User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TenantStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"
    PENDING = "pending"

@dataclass
class TenantConfig:
    id: str
    organization_id: str
    database_url: str
    schema_name: str
    created_at: datetime
    status: TenantStatus
    metadata: Dict[str, Any]
    max_storage_gb: float
    max_connections: int
    features: Set[str]

class TenantService:
    def __init__(self, default_database_url: str):
        self.default_database_url = default_database_url
        self.engine = create_engine(default_database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.Base = declarative_base()
        self._init_tenant_tables()
        
    def _init_tenant_tables(self):
        """Initialize tenant management tables."""
        class Tenant(Base):
            __tablename__ = 'tenants'
            
            id = Column(String, primary_key=True)
            organization_id = Column(String, ForeignKey('organizations.id'))
            database_url = Column(String, nullable=False)
            schema_name = Column(String, nullable=False)
            created_at = Column(DateTime, nullable=False)
            status = Column(String, nullable=False)
            metadata = Column(JSON)
            max_storage_gb = Column(Integer, nullable=False)
            max_connections = Column(Integer, nullable=False)
            features = Column(JSON)
            
            organization = relationship("Organization", back_populates="tenants")
            
        self.Base.metadata.create_all(self.engine)
        
    def create_tenant(self, organization: Organization,
                     max_storage_gb: float = 10.0,
                     max_connections: int = 20) -> TenantConfig:
        """Create a new tenant with isolated database schema."""
        tenant_id = str(uuid.uuid4())
        schema_name = f"tenant_{tenant_id}"
        
        # Create tenant-specific schema
        with self.engine.connect() as conn:
            conn.execute(f"CREATE SCHEMA {schema_name}")
            
        # Create tenant configuration
        tenant_config = TenantConfig(
            id=tenant_id,
            organization_id=organization.id,
            database_url=self.default_database_url,
            schema_name=schema_name,
            created_at=datetime.utcnow(),
            status=TenantStatus.ACTIVE,
            metadata={},
            max_storage_gb=max_storage_gb,
            max_connections=max_connections,
            features=organization.features
        )
        
        # Store tenant configuration
        session = self.Session()
        try:
            tenant = Tenant(
                id=tenant_config.id,
                organization_id=tenant_config.organization_id,
                database_url=tenant_config.database_url,
                schema_name=tenant_config.schema_name,
                created_at=tenant_config.created_at,
                status=tenant_config.status.value,
                metadata=tenant_config.metadata,
                max_storage_gb=int(tenant_config.max_storage_gb),
                max_connections=tenant_config.max_connections,
                features=list(tenant_config.features)
            )
            session.add(tenant)
            session.commit()
        finally:
            session.close()
            
        return tenant_config
        
    def get_tenant(self, tenant_id: str) -> Optional[TenantConfig]:
        """Retrieve tenant configuration."""
        session = self.Session()
        try:
            tenant = session.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant:
                return None
                
            return TenantConfig(
                id=tenant.id,
                organization_id=tenant.organization_id,
                database_url=tenant.database_url,
                schema_name=tenant.schema_name,
                created_at=tenant.created_at,
                status=TenantStatus(tenant.status),
                metadata=tenant.metadata or {},
                max_storage_gb=float(tenant.max_storage_gb),
                max_connections=tenant.max_connections,
                features=set(tenant.features or [])
            )
        finally:
            session.close()
            
    def update_tenant(self, tenant_id: str,
                     updates: Dict[str, Any]) -> Optional[TenantConfig]:
        """Update tenant configuration."""
        session = self.Session()
        try:
            tenant = session.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant:
                return None
                
            for key, value in updates.items():
                if hasattr(tenant, key):
                    setattr(tenant, key, value)
                    
            session.commit()
            return self.get_tenant(tenant_id)
        finally:
            session.close()
            
    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete tenant and its schema."""
        session = self.Session()
        try:
            tenant = session.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant:
                return False
                
            # Drop tenant schema
            with self.engine.connect() as conn:
                conn.execute(f"DROP SCHEMA {tenant.schema_name} CASCADE")
                
            # Update tenant status
            tenant.status = TenantStatus.DELETED.value
            session.commit()
            return True
        finally:
            session.close()
            
    def suspend_tenant(self, tenant_id: str, reason: str) -> bool:
        """Suspend tenant access."""
        session = self.Session()
        try:
            tenant = session.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant:
                return False
                
            tenant.status = TenantStatus.SUSPENDED.value
            tenant.metadata = tenant.metadata or {}
            tenant.metadata["suspension_reason"] = reason
            tenant.metadata["suspended_at"] = datetime.utcnow().isoformat()
            
            session.commit()
            return True
        finally:
            session.close()
            
    def activate_tenant(self, tenant_id: str) -> bool:
        """Activate suspended tenant."""
        session = self.Session()
        try:
            tenant = session.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant:
                return False
                
            tenant.status = TenantStatus.ACTIVE.value
            if tenant.metadata:
                tenant.metadata.pop("suspension_reason", None)
                tenant.metadata.pop("suspended_at", None)
                
            session.commit()
            return True
        finally:
            session.close()
            
    def get_tenant_usage(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant resource usage statistics."""
        session = self.Session()
        try:
            tenant = session.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant:
                return {}
                
            # Get storage usage
            with self.engine.connect() as conn:
                result = conn.execute(f"""
                    SELECT pg_total_relation_size('{tenant.schema_name}.data') / 1024 / 1024 / 1024 as storage_gb
                """).first()
                storage_gb = float(result[0]) if result else 0.0
                
            # Get connection count
            with self.engine.connect() as conn:
                result = conn.execute(f"""
                    SELECT count(*) FROM pg_stat_activity 
                    WHERE datname = '{tenant.schema_name}'
                """).first()
                connections = int(result[0]) if result else 0
                
            return {
                "storage_gb": storage_gb,
                "connections": connections,
                "max_storage_gb": float(tenant.max_storage_gb),
                "max_connections": tenant.max_connections,
                "storage_usage_percent": (storage_gb / float(tenant.max_storage_gb)) * 100,
                "connection_usage_percent": (connections / tenant.max_connections) * 100
            }
        finally:
            session.close()
            
    def validate_tenant_capacity(self, tenant_id: str) -> bool:
        """Check if tenant has reached resource limits."""
        usage = self.get_tenant_usage(tenant_id)
        if not usage:
            return False
            
        return (usage["storage_usage_percent"] < 100 and
                usage["connection_usage_percent"] < 100)
                
    def get_tenant_schema(self, tenant_id: str) -> Optional[str]:
        """Get tenant's database schema name."""
        session = self.Session()
        try:
            tenant = session.query(Tenant).filter_by(id=tenant_id).first()
            return tenant.schema_name if tenant else None
        finally:
            session.close()
            
    def execute_tenant_query(self, tenant_id: str, query: str,
                           params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute query in tenant's schema."""
        schema_name = self.get_tenant_schema(tenant_id)
        if not schema_name:
            return []
            
        with self.engine.connect() as conn:
            # Set search path to tenant schema
            conn.execute(f"SET search_path TO {schema_name}")
            
            # Execute query
            result = conn.execute(query, params or {})
            return [dict(row) for row in result] 