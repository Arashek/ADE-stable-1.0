from typing import Dict, List, Optional, Any, Type, TypeVar, Generic, Union, Callable
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum
import sqlalchemy as sa
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql import Select, and_, or_, not_
from sqlalchemy.exc import SQLAlchemyError
import threading
from abc import ABC, abstractmethod
from functools import wraps
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type variables for generic type hints
T = TypeVar('T')

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

@dataclass
class QueryFilter:
    field: str
    operator: str
    value: Any
    
    def to_sqlalchemy(self) -> Any:
        """Convert filter to SQLAlchemy expression."""
        if self.operator == "eq":
            return getattr(self.model_class, self.field) == self.value
        elif self.operator == "ne":
            return getattr(self.model_class, self.field) != self.value
        elif self.operator == "gt":
            return getattr(self.model_class, self.field) > self.value
        elif self.operator == "lt":
            return getattr(self.model_class, self.field) < self.value
        elif self.operator == "gte":
            return getattr(self.model_class, self.field) >= self.value
        elif self.operator == "lte":
            return getattr(self.model_class, self.field) <= self.value
        elif self.operator == "in":
            return getattr(self.model_class, self.field).in_(self.value)
        elif self.operator == "nin":
            return not_(getattr(self.model_class, self.field).in_(self.value))
        elif self.operator == "contains":
            return getattr(self.model_class, self.field).contains(self.value)
        elif self.operator == "startswith":
            return getattr(self.model_class, self.field).startswith(self.value)
        elif self.operator == "endswith":
            return getattr(self.model_class, self.field).endswith(self.value)
        else:
            raise ValueError(f"Unsupported operator: {self.operator}")

class QueryBuilder:
    """Builder for constructing complex database queries."""
    
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
        self.filters: List[QueryFilter] = []
        self.order_by: List[tuple] = []
        self.limit: Optional[int] = None
        self.offset: Optional[int] = None
        
    def filter(self, field: str, operator: str, value: Any) -> 'QueryBuilder':
        """Add filter to query."""
        self.filters.append(QueryFilter(field, operator, value))
        return self
        
    def order_by_field(self, field: str, desc: bool = False) -> 'QueryBuilder':
        """Add ordering to query."""
        self.order_by.append((field, desc))
        return self
        
    def limit_results(self, limit: int) -> 'QueryBuilder':
        """Set limit for query results."""
        self.limit = limit
        return self
        
    def offset_results(self, offset: int) -> 'QueryBuilder':
        """Set offset for query results."""
        self.offset = offset
        return self
        
    def build(self) -> Query:
        """Build SQLAlchemy query."""
        query = self.model_class.query
        
        # Apply filters
        for filter in self.filters:
            query = query.filter(filter.to_sqlalchemy())
            
        # Apply ordering
        for field, desc in self.order_by:
            column = getattr(self.model_class, field)
            if desc:
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column)
                
        # Apply limit and offset
        if self.limit is not None:
            query = query.limit(self.limit)
        if self.offset is not None:
            query = query.offset(self.offset)
            
        return query

class TransactionManager:
    """Manages database transactions with rollback support."""
    
    def __init__(self, session: Session):
        self.session = session
        self._nested_transactions = 0
        
    def begin(self) -> None:
        """Begin a new transaction."""
        if self._nested_transactions == 0:
            self.session.begin()
        self._nested_transactions += 1
        
    def commit(self) -> None:
        """Commit the current transaction."""
        self._nested_transactions -= 1
        if self._nested_transactions == 0:
            self.session.commit()
            
    def rollback(self) -> None:
        """Rollback the current transaction."""
        self._nested_transactions = 0
        self.session.rollback()
        
    def __enter__(self) -> 'TransactionManager':
        self.begin()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

class PermissionChecker:
    """Checks permissions for database operations."""
    
    def __init__(self, user_permissions: List[Permission]):
        self.user_permissions = user_permissions
        
    def has_permission(self, required_permission: Permission) -> bool:
        """Check if user has required permission."""
        if Permission.ADMIN in self.user_permissions:
            return True
        return required_permission in self.user_permissions
        
    def require_permission(self, permission: Permission):
        """Decorator to require permission for function."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.has_permission(permission):
                    raise PermissionError(f"Permission {permission.value} required")
                return func(*args, **kwargs)
            return wrapper
        return decorator

class DataAccessLayer(Generic[T]):
    """Main data access layer with permission-aware operations."""
    
    def __init__(
        self,
        model_class: Type[T],
        session: Session,
        permission_checker: PermissionChecker
    ):
        self.model_class = model_class
        self.session = session
        self.permission_checker = permission_checker
        self.transaction_manager = TransactionManager(session)
        
    def query(self) -> QueryBuilder:
        """Create new query builder."""
        return QueryBuilder(self.model_class)
        
    @PermissionChecker.require_permission(Permission.READ)
    def get_by_id(self, id: str) -> Optional[T]:
        """Get entity by ID with permission check."""
        return self.session.query(self.model_class).get(id)
        
    @PermissionChecker.require_permission(Permission.READ)
    def get_all(self) -> List[T]:
        """Get all entities with permission check."""
        return self.session.query(self.model_class).all()
        
    @PermissionChecker.require_permission(Permission.WRITE)
    def create(self, entity: T) -> T:
        """Create entity with permission check."""
        with self.transaction_manager:
            self.session.add(entity)
            self.session.flush()
            return entity
            
    @PermissionChecker.require_permission(Permission.WRITE)
    def update(self, entity: T) -> T:
        """Update entity with permission check."""
        with self.transaction_manager:
            self.session.merge(entity)
            self.session.flush()
            return entity
            
    @PermissionChecker.require_permission(Permission.DELETE)
    def delete(self, id: str) -> bool:
        """Delete entity with permission check."""
        with self.transaction_manager:
            entity = self.get_by_id(id)
            if entity:
                self.session.delete(entity)
                return True
            return False
            
    def execute_query(self, query: Union[Query, QueryBuilder]) -> List[T]:
        """Execute query with permission check."""
        if isinstance(query, QueryBuilder):
            query = query.build()
        return query.all()
        
    def count(self, query: Union[Query, QueryBuilder]) -> int:
        """Count query results with permission check."""
        if isinstance(query, QueryBuilder):
            query = query.build()
        return query.count()
        
    def exists(self, query: Union[Query, QueryBuilder]) -> bool:
        """Check if query has results with permission check."""
        if isinstance(query, QueryBuilder):
            query = query.build()
        return query.first() is not None
        
    def bulk_create(self, entities: List[T]) -> List[T]:
        """Bulk create entities with permission check."""
        with self.transaction_manager:
            self.session.bulk_save_objects(entities)
            return entities
            
    def bulk_update(self, entities: List[T]) -> List[T]:
        """Bulk update entities with permission check."""
        with self.transaction_manager:
            self.session.bulk_save_objects(entities)
            return entities
            
    def bulk_delete(self, ids: List[str]) -> int:
        """Bulk delete entities with permission check."""
        with self.transaction_manager:
            result = self.session.query(self.model_class).filter(
                self.model_class.id.in_(ids)
            ).delete(synchronize_session=False)
            return result
            
    def transaction(self) -> TransactionManager:
        """Get transaction manager."""
        return self.transaction_manager
        
    def __enter__(self) -> 'DataAccessLayer[T]':
        self.transaction_manager.begin()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.transaction_manager.rollback()
        else:
            self.transaction_manager.commit() 