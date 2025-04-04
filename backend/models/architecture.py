from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

class ComponentType(str, Enum):
    """Types of components in a system architecture"""
    SERVICE = "service"
    DATABASE = "database"
    FRONTEND = "frontend"
    API = "api"
    LIBRARY = "library"
    UTILITY = "utility"
    CONNECTOR = "connector"
    OTHER = "other"

class ConnectionType(str, Enum):
    """Types of connections between components"""
    REST = "rest"
    GRPC = "grpc"
    GRAPHQL = "graphql"
    EVENT = "event"
    DATABASE = "database"
    DIRECT = "direct"
    OTHER = "other"

class Component(BaseModel):
    """Component in the system architecture"""
    id: str = Field(..., description="Unique component identifier")
    name: str = Field(..., description="Component name")
    description: Optional[str] = Field(None, description="Component description")
    type: ComponentType = Field(..., description="Component type")
    
    tech_stack: List[str] = Field(default=[], description="Technologies used in this component")
    responsibilities: List[str] = Field(default=[], description="Key responsibilities of this component")
    
    # Deployment information
    is_deployed: bool = Field(default=False, description="Whether component is deployed")
    deployment_url: Optional[str] = Field(None, description="URL where component is deployed")
    
    # Connectivity
    depends_on: List[str] = Field(default=[], description="IDs of components this component depends on")
    metadata: Dict[str, Any] = Field(default={}, description="Additional component metadata")
    
    class Config:
        use_enum_values = True

class Connection(BaseModel):
    """Connection between two components in the system architecture"""
    id: str = Field(..., description="Unique connection identifier")
    source_id: str = Field(..., description="ID of the source component")
    target_id: str = Field(..., description="ID of the target component")
    
    name: Optional[str] = Field(None, description="Connection name")
    type: ConnectionType = Field(..., description="Connection type")
    
    is_bidirectional: bool = Field(default=False, description="Whether connection is bidirectional")
    description: Optional[str] = Field(None, description="Connection description")
    
    metadata: Dict[str, Any] = Field(default={}, description="Additional connection metadata")
    
    class Config:
        use_enum_values = True

class SystemArchitecture(BaseModel):
    """Complete system architecture for a project"""
    id: str = Field(..., description="Unique architecture identifier")
    project_id: str = Field(..., description="ID of the project this architecture belongs to")
    
    name: str = Field(..., description="Architecture name")
    description: Optional[str] = Field(None, description="Architecture description")
    version: str = Field(default="1.0", description="Architecture version")
    
    components: List[Component] = Field(default=[], description="Components in the architecture")
    connections: List[Connection] = Field(default=[], description="Connections between components")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # High-level architecture metadata
    primary_language: Optional[str] = Field(None, description="Primary programming language")
    cloud_provider: Optional[str] = Field(None, description="Target cloud provider")
    deployment_strategy: Optional[str] = Field(None, description="Deployment strategy")
    
    metadata: Dict[str, Any] = Field(default={}, description="Additional architecture metadata")
    
    class Config:
        use_enum_values = True
