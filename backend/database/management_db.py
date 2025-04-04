from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Enum, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid

logger = logging.getLogger(__name__)
Base = declarative_base()

# Security & Access Control Models
class PermissionDB(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    resource_type = Column(String, nullable=False)
    actions = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RoleDB(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    permissions = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdminSettingsDB(Base):
    __tablename__ = "admin_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    setting_key = Column(String, unique=True, nullable=False)
    setting_value = Column(JSON, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserActivityDB(Base):
    __tablename__ = "user_activity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    details = Column(JSON)
    ip_address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Architecture Management Models
class ComponentDB(Base):
    __tablename__ = "components"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(String)
    version = Column(String, nullable=False)
    status = Column(String, nullable=False)
    configuration = Column(JSON)
    dependencies = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ModelDB(Base):
    __tablename__ = "models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    schema = Column(JSON, nullable=False)
    relationships = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ServiceConfigDB(Base):
    __tablename__ = "service_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(UUID(as_uuid=True), nullable=False)
    environment = Column(String, nullable=False)
    configuration = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InfrastructureSettingsDB(Base):
    __tablename__ = "infrastructure_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    setting_key = Column(String, unique=True, nullable=False)
    setting_value = Column(JSON, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Integration Management Models
class ExternalServiceDB(Base):
    __tablename__ = "external_services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    configuration = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class APIConfigDB(Base):
    __tablename__ = "api_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    authentication = Column(JSON)
    rate_limit = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WebhookConfigDB(Base):
    __tablename__ = "webhook_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    events = Column(JSON, nullable=False)
    secret = Column(String)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Marketplace Models
class MarketplaceItemDB(Base):
    __tablename__ = "marketplace_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    tags = Column(JSON)
    item_metadata = Column(JSON)  # Renamed from 'metadata' which is reserved in SQLAlchemy
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MarketplaceOrderDB(Base):
    __tablename__ = "marketplace_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    item_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    payment_details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ManagementDB:
    def __init__(self):
        self.engine = None
        self.async_session = None

    async def connect(self):
        """Initialize database connection"""
        try:
            # Replace with your actual database URL
            database_url = "postgresql+asyncpg://user:password@localhost:5432/management_db"
            self.engine = create_async_engine(database_url, echo=True)
            self.async_session = async_sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise

    async def close(self):
        """Close database connection"""
        try:
            await self.engine.dispose()
            logger.info("Database connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connection: {str(e)}")
            raise

    # Security & Access Control Methods
    async def get_permissions(self) -> List[Dict[str, Any]]:
        async with self.async_session() as session:
            result = await session.query(PermissionDB).all()
            return [dict(row) for row in result]

    async def create_permission(self, permission_data: Dict[str, Any]) -> Dict[str, Any]:
        async with self.async_session() as session:
            permission = PermissionDB(**permission_data)
            session.add(permission)
            await session.commit()
            return dict(permission)

    async def get_roles(self) -> List[Dict[str, Any]]:
        async with self.async_session() as session:
            result = await session.query(RoleDB).all()
            return [dict(row) for row in result]

    async def create_role(self, role_data: Dict[str, Any]) -> Dict[str, Any]:
        async with self.async_session() as session:
            role = RoleDB(**role_data)
            session.add(role)
            await session.commit()
            return dict(role)

    async def get_admin_settings(self) -> List[Dict[str, Any]]:
        async with self.async_session() as session:
            result = await session.query(AdminSettingsDB).all()
            return [dict(row) for row in result]

    async def update_admin_setting(self, setting_id: str, setting_data: Dict[str, Any]) -> Dict[str, Any]:
        async with self.async_session() as session:
            setting = await session.query(AdminSettingsDB).filter(AdminSettingsDB.id == setting_id).first()
            for key, value in setting_data.items():
                setattr(setting, key, value)
            await session.commit()
            return dict(setting)

    async def get_user_activity(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        async with self.async_session() as session:
            query = session.query(UserActivityDB)
            
            if user_id:
                query = query.filter(UserActivityDB.user_id == user_id)
            if action:
                query = query.filter(UserActivityDB.action == action)
            if resource_type:
                query = query.filter(UserActivityDB.resource_type == resource_type)
            if start_date:
                query = query.filter(UserActivityDB.created_at >= start_date)
            if end_date:
                query = query.filter(UserActivityDB.created_at <= end_date)
            
            query = query.offset((page - 1) * limit).limit(limit)
            result = await query.all()
            return [dict(row) for row in result]

    # Architecture Management Methods
    async def get_components(
        self,
        type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        async with self.async_session() as session:
            query = session.query(ComponentDB)
            
            if type:
                query = query.filter(ComponentDB.type == type)
            if status:
                query = query.filter(ComponentDB.status == status)
            
            result = await query.all()
            return [dict(row) for row in result]

    async def create_component(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        async with self.async_session() as session:
            component = ComponentDB(**component_data)
            session.add(component)
            await session.commit()
            return dict(component)

    async def get_models(self) -> List[Dict[str, Any]]:
        async with self.async_session() as session:
            result = await session.query(ModelDB).all()
            return [dict(row) for row in result]

    async def create_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        async with self.async_session() as session:
            model = ModelDB(**model_data)
            session.add(model)
            await session.commit()
            return dict(model)

    async def get_service_configs(
        self,
        service_id: Optional[str] = None,
        environment: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        async with self.async_session() as session:
            query = session.query(ServiceConfigDB)
            
            if service_id:
                query = query.filter(ServiceConfigDB.service_id == service_id)
            if environment:
                query = query.filter(ServiceConfigDB.environment == environment)
            
            result = await query.all()
            return [dict(row) for row in result]

    async def update_service_config(
        self,
        config_id: str,
        config_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        async with self.async_session() as session:
            config = await session.query(ServiceConfigDB).filter(ServiceConfigDB.id == config_id).first()
            for key, value in config_data.items():
                setattr(config, key, value)
            await session.commit()
            return dict(config)

    async def get_infrastructure_settings(self) -> List[Dict[str, Any]]:
        async with self.async_session() as session:
            result = await session.query(InfrastructureSettingsDB).all()
            return [dict(row) for row in result]

    async def update_infrastructure_setting(
        self,
        setting_id: str,
        setting_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        async with self.async_session() as session:
            setting = await session.query(InfrastructureSettingsDB).filter(InfrastructureSettingsDB.id == setting_id).first()
            for key, value in setting_data.items():
                setattr(setting, key, value)
            await session.commit()
            return dict(setting)

    # Integration Management Methods
    async def get_external_services(
        self,
        type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        async with self.async_session() as session:
            query = session.query(ExternalServiceDB)
            
            if type:
                query = query.filter(ExternalServiceDB.type == type)
            if status:
                query = query.filter(ExternalServiceDB.status == status)
            
            result = await query.all()
            return [dict(row) for row in result]

    async def create_external_service(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        async with self.async_session() as session:
            service = ExternalServiceDB(**service_data)
            session.add(service)
            await session.commit()
            return dict(service)

    async def get_api_configs(self) -> List[Dict[str, Any]]:
        async with self.async_session() as session:
            result = await session.query(APIConfigDB).all()
            return [dict(row) for row in result]

    async def create_api_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        async with self.async_session() as session:
            config = APIConfigDB(**config_data)
            session.add(config)
            await session.commit()
            return dict(config)

    async def get_webhook_configs(self) -> List[Dict[str, Any]]:
        async with self.async_session() as session:
            result = await session.query(WebhookConfigDB).all()
            return [dict(row) for row in result]

    async def create_webhook_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        async with self.async_session() as session:
            config = WebhookConfigDB(**config_data)
            session.add(config)
            await session.commit()
            return dict(config)

    # Marketplace Methods
    async def get_marketplace_items(
        self,
        type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        page: int = 1,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        async with self.async_session() as session:
            query = session.query(MarketplaceItemDB)
            
            if type:
                query = query.filter(MarketplaceItemDB.type == type)
            if tags:
                query = query.filter(MarketplaceItemDB.tags.contains(tags))
            
            query = query.offset((page - 1) * limit).limit(limit)
            result = await query.all()
            return [dict(row) for row in result]

    async def create_marketplace_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        async with self.async_session() as session:
            item = MarketplaceItemDB(**item_data)
            session.add(item)
            await session.commit()
            return dict(item)

    async def get_marketplace_orders(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        async with self.async_session() as session:
            query = session.query(MarketplaceOrderDB)
            
            if user_id:
                query = query.filter(MarketplaceOrderDB.user_id == user_id)
            if status:
                query = query.filter(MarketplaceOrderDB.status == status)
            
            query = query.offset((page - 1) * limit).limit(limit)
            result = await query.all()
            return [dict(row) for row in result]

    async def create_marketplace_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        async with self.async_session() as session:
            order = MarketplaceOrderDB(**order_data)
            session.add(order)
            await session.commit()
            return dict(order) 