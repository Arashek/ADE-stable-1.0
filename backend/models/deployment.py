from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from uuid import UUID

from models.codebase import Codebase

class EnvironmentType(str, Enum):
    """Types of deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
    CUSTOM = "custom"

class PlatformType(str, Enum):
    """Types of deployment platforms"""
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    SERVERLESS = "serverless"
    STATIC = "static"
    VM = "virtual_machine"
    CUSTOM = "custom"

class Environment(BaseModel):
    """Model representing a deployment environment"""
    id: str
    name: str
    type: EnvironmentType
    platform: PlatformType
    config: Dict[str, Any] = {}
    variables: Dict[str, str] = {}
    region: Optional[str] = None
    provider: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class DeploymentConfig(BaseModel):
    """Model representing deployment configuration"""
    id: str
    name: str
    environment_id: str
    codebase_id: str
    version: str = "1.0.0"
    resources: Dict[str, Any] = {}
    scaling: Dict[str, Any] = {}
    networking: Dict[str, Any] = {}
    storage: Dict[str, Any] = {}
    security: Dict[str, Any] = {}
    dependencies: List[str] = []
    health_checks: List[Dict[str, Any]] = []
    rollback_strategy: Optional[str] = None
    custom_config: Dict[str, Any] = {}
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class DockerConfig(BaseModel):
    """Model representing Docker deployment configuration"""
    base_image: str = "python:3.9-slim"
    expose_ports: List[int] = []
    environment_variables: Dict[str, str] = {}
    volumes: List[Dict[str, str]] = []
    commands: List[str] = []
    healthcheck: Optional[Dict[str, Any]] = None
    restart_policy: str = "unless-stopped"
    network_mode: str = "bridge"
    resource_limits: Optional[Dict[str, str]] = None

class KubernetesConfig(BaseModel):
    """Model representing Kubernetes deployment configuration"""
    namespace: str = "default"
    replicas: int = 1
    container: Dict[str, Any] = {}
    service: Dict[str, Any] = {}
    ingress: Optional[Dict[str, Any]] = None
    volumes: List[Dict[str, Any]] = []
    config_maps: List[Dict[str, Any]] = []
    secrets: List[Dict[str, Any]] = []
    resource_quotas: Optional[Dict[str, str]] = None
    autoscaling: Optional[Dict[str, Any]] = None
    readiness_probe: Optional[Dict[str, Any]] = None
    liveness_probe: Optional[Dict[str, Any]] = None

class StaticSiteConfig(BaseModel):
    """Model representing static site deployment configuration"""
    build_command: str
    output_dir: str = "dist"
    environment_variables: Dict[str, str] = {}
    cache_control: Optional[Dict[str, str]] = None
    custom_domain: Optional[str] = None
    spa_fallback: bool = False
    cdn_enabled: bool = False
    basic_auth: Optional[Dict[str, str]] = None

class ServerlessConfig(BaseModel):
    """Model representing serverless deployment configuration"""
    runtime: str
    handler: str
    memory: int = 128
    timeout: int = 30
    environment_variables: Dict[str, str] = {}
    vpc_config: Optional[Dict[str, Any]] = None
    layers: List[str] = []
    triggers: List[Dict[str, Any]] = []
    concurrency: Optional[int] = None

class DeploymentStatus(str, Enum):
    """Status of a deployment"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"

class Deployment(BaseModel):
    """Model representing a deployment"""
    id: str
    config_id: str
    environment_id: str
    codebase_id: str
    status: DeploymentStatus = DeploymentStatus.PENDING
    version: str
    artifacts: List[Dict[str, Any]] = []
    logs: List[Dict[str, Any]] = []
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: Optional[int] = None
    deployed_by: Optional[str] = None
    deployment_url: Optional[str] = None
    rollback_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

class DeploymentResult(BaseModel):
    """Model representing the result of a deployment operation"""
    deployment_id: str
    status: DeploymentStatus
    logs: List[Dict[str, Any]] = []
    deployment_url: Optional[str] = None
    success: bool = False
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = {}
