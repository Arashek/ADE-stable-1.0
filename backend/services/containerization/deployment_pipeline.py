"""
Deployment Pipeline Service

This module provides functionality for deploying containerized applications
through a structured pipeline, including build, test, and deployment stages.
"""

import os
import logging
import asyncio
import json
import uuid
from typing import Dict, List, Optional, Union, Any, Callable
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

from .container_manager import ContainerManager, Container, ContainerStatus
from .template_repository import TemplateRepository, ContainerTemplate
from .registry import ContainerRegistry, ContainerImage
from .orchestration import ContainerOrchestrator, KubernetesResource

# Configure logging
logger = logging.getLogger(__name__)

class PipelineStageType(str, Enum):
    """Types of pipeline stages."""
    BUILD = "build"
    TEST = "test"
    SECURITY_SCAN = "security_scan"
    DEPLOY = "deploy"
    VALIDATE = "validate"
    ROLLBACK = "rollback"

class PipelineStageStatus(str, Enum):
    """Status of a pipeline stage."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

class PipelineStatus(str, Enum):
    """Status of a deployment pipeline."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PipelineStage(BaseModel):
    """A stage in a deployment pipeline."""
    id: str
    name: str
    type: PipelineStageType
    status: PipelineStageStatus = PipelineStageStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    order: int
    timeout_seconds: int = 3600  # Default timeout of 1 hour
    config: Dict[str, Any] = Field(default_factory=dict)
    logs: List[str] = Field(default_factory=list)
    artifacts: Dict[str, str] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)

class DeploymentPipeline(BaseModel):
    """A deployment pipeline for a containerized application."""
    id: str
    name: str
    description: Optional[str] = None
    status: PipelineStatus = PipelineStatus.PENDING
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_id: str
    project_id: str
    application_id: str
    container_id: Optional[str] = None
    image_id: Optional[str] = None
    stages: List[PipelineStage] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)
    environment: Dict[str, str] = Field(default_factory=dict)
    resources: Dict[str, Any] = Field(default_factory=dict)

class DeploymentTarget(str, Enum):
    """Types of deployment targets."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    CUSTOM = "custom"

class DeploymentPipelineService:
    """
    Deployment Pipeline Service
    
    Manages the deployment of containerized applications through a structured pipeline,
    including:
    - Creating and managing deployment pipelines
    - Executing pipeline stages
    - Managing deployment artifacts
    - Handling deployment rollbacks
    """
    
    def __init__(
        self,
        container_manager: ContainerManager = None,
        template_repository: TemplateRepository = None,
        container_registry: ContainerRegistry = None,
        container_orchestrator: ContainerOrchestrator = None
    ):
        """
        Initialize the Deployment Pipeline Service.
        
        Args:
            container_manager: Container Manager instance
            template_repository: Template Repository instance
            container_registry: Container Registry instance
            container_orchestrator: Container Orchestrator instance
        """
        # Import here to avoid circular imports
        from .container_manager import container_manager as default_container_manager
        from .template_repository import template_repository as default_template_repository
        from .registry import container_registry as default_container_registry
        from .orchestration import container_orchestrator as default_container_orchestrator
        
        self.container_manager = container_manager or default_container_manager
        self.template_repository = template_repository or default_template_repository
        self.container_registry = container_registry or default_container_registry
        self.container_orchestrator = container_orchestrator or default_container_orchestrator
        
        self.pipelines: Dict[str, DeploymentPipeline] = {}
        self.stage_handlers: Dict[PipelineStageType, Callable] = self._register_stage_handlers()
        
        logger.info("Deployment Pipeline Service initialized")
    
    def _register_stage_handlers(self) -> Dict[PipelineStageType, Callable]:
        """
        Register handlers for pipeline stages.
        
        Returns:
            Dictionary mapping stage types to handler functions
        """
        return {
            PipelineStageType.BUILD: self._handle_build_stage,
            PipelineStageType.TEST: self._handle_test_stage,
            PipelineStageType.SECURITY_SCAN: self._handle_security_scan_stage,
            PipelineStageType.DEPLOY: self._handle_deploy_stage,
            PipelineStageType.VALIDATE: self._handle_validate_stage,
            PipelineStageType.ROLLBACK: self._handle_rollback_stage
        }
    
    async def create_pipeline(
        self,
        name: str,
        user_id: str,
        project_id: str,
        application_id: str,
        description: Optional[str] = None,
        config: Dict[str, Any] = None,
        environment: Dict[str, str] = None,
        resources: Dict[str, Any] = None
    ) -> DeploymentPipeline:
        """
        Create a new deployment pipeline.
        
        Args:
            name: Name of the pipeline
            user_id: ID of the user
            project_id: ID of the project
            application_id: ID of the application
            description: Description of the pipeline
            config: Pipeline configuration
            environment: Environment variables
            resources: Resource requirements
            
        Returns:
            The created pipeline
        """
        pipeline_id = str(uuid.uuid4())
        now = datetime.now()
        
        pipeline = DeploymentPipeline(
            id=pipeline_id,
            name=name,
            description=description,
            created_at=now,
            updated_at=now,
            user_id=user_id,
            project_id=project_id,
            application_id=application_id,
            config=config or {},
            environment=environment or {},
            resources=resources or {}
        )
        
        # Add default stages
        pipeline.stages = self._create_default_stages()
        
        # Store the pipeline
        self.pipelines[pipeline_id] = pipeline
        
        logger.info(f"Pipeline created: {pipeline_id}")
        return pipeline
    
    def _create_default_stages(self) -> List[PipelineStage]:
        """
        Create default pipeline stages.
        
        Returns:
            List of default pipeline stages
        """
        return [
            PipelineStage(
                id=str(uuid.uuid4()),
                name="Build Application",
                type=PipelineStageType.BUILD,
                order=1,
                config={
                    "build_args": {}
                }
            ),
            PipelineStage(
                id=str(uuid.uuid4()),
                name="Run Tests",
                type=PipelineStageType.TEST,
                order=2,
                config={
                    "test_command": "npm test",
                    "test_timeout": 300
                },
                dependencies=[1]  # Depends on Build stage
            ),
            PipelineStage(
                id=str(uuid.uuid4()),
                name="Security Scan",
                type=PipelineStageType.SECURITY_SCAN,
                order=3,
                config={
                    "scan_type": "vulnerability",
                    "severity_threshold": "high"
                },
                dependencies=[1]  # Depends on Build stage
            ),
            PipelineStage(
                id=str(uuid.uuid4()),
                name="Deploy Application",
                type=PipelineStageType.DEPLOY,
                order=4,
                config={
                    "deployment_target": DeploymentTarget.DEVELOPMENT,
                    "replicas": 1
                },
                dependencies=[2, 3]  # Depends on Test and Security Scan stages
            ),
            PipelineStage(
                id=str(uuid.uuid4()),
                name="Validate Deployment",
                type=PipelineStageType.VALIDATE,
                order=5,
                config={
                    "health_check_path": "/health",
                    "health_check_timeout": 60
                },
                dependencies=[4]  # Depends on Deploy stage
            )
        ]
    
    async def get_pipeline(self, pipeline_id: str) -> DeploymentPipeline:
        """
        Get a pipeline by ID.
        
        Args:
            pipeline_id: ID of the pipeline
            
        Returns:
            The pipeline
        """
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        return self.pipelines[pipeline_id]
    
    async def list_pipelines(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        application_id: Optional[str] = None,
        status: Optional[PipelineStatus] = None
    ) -> List[DeploymentPipeline]:
        """
        List pipelines with optional filtering.
        
        Args:
            user_id: Filter by user ID
            project_id: Filter by project ID
            application_id: Filter by application ID
            status: Filter by status
            
        Returns:
            List of pipelines matching the filters
        """
        pipelines = list(self.pipelines.values())
        
        if user_id:
            pipelines = [p for p in pipelines if p.user_id == user_id]
        
        if project_id:
            pipelines = [p for p in pipelines if p.project_id == project_id]
        
        if application_id:
            pipelines = [p for p in pipelines if p.application_id == application_id]
        
        if status:
            pipelines = [p for p in pipelines if p.status == status]
        
        return pipelines
    
    async def start_pipeline(self, pipeline_id: str) -> DeploymentPipeline:
        """
        Start a pipeline.
        
        Args:
            pipeline_id: ID of the pipeline
            
        Returns:
            The updated pipeline
        """
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        pipeline = self.pipelines[pipeline_id]
        
        if pipeline.status != PipelineStatus.PENDING:
            raise ValueError(f"Pipeline cannot be started: {pipeline.status}")
        
        # Update pipeline status
        pipeline.status = PipelineStatus.RUNNING
        pipeline.started_at = datetime.now()
        pipeline.updated_at = datetime.now()
        
        # Start the pipeline execution in the background
        asyncio.create_task(self._execute_pipeline(pipeline_id))
        
        logger.info(f"Pipeline started: {pipeline_id}")
        return pipeline
    
    async def cancel_pipeline(self, pipeline_id: str) -> DeploymentPipeline:
        """
        Cancel a pipeline.
        
        Args:
            pipeline_id: ID of the pipeline
            
        Returns:
            The updated pipeline
        """
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        pipeline = self.pipelines[pipeline_id]
        
        if pipeline.status != PipelineStatus.RUNNING:
            raise ValueError(f"Pipeline cannot be cancelled: {pipeline.status}")
        
        # Update pipeline status
        pipeline.status = PipelineStatus.CANCELLED
        pipeline.completed_at = datetime.now()
        pipeline.updated_at = datetime.now()
        
        # Update running stages
        for stage in pipeline.stages:
            if stage.status == PipelineStageStatus.RUNNING:
                stage.status = PipelineStageStatus.CANCELLED
                stage.completed_at = datetime.now()
            elif stage.status == PipelineStageStatus.PENDING:
                stage.status = PipelineStageStatus.SKIPPED
        
        logger.info(f"Pipeline cancelled: {pipeline_id}")
        return pipeline
    
    async def _execute_pipeline(self, pipeline_id: str) -> None:
        """
        Execute a pipeline.
        
        Args:
            pipeline_id: ID of the pipeline
        """
        if pipeline_id not in self.pipelines:
            logger.error(f"Pipeline not found: {pipeline_id}")
            return
        
        pipeline = self.pipelines[pipeline_id]
        
        try:
            # Sort stages by order
            stages = sorted(pipeline.stages, key=lambda s: s.order)
            
            # Execute stages
            for stage in stages:
                # Skip cancelled stages
                if stage.status == PipelineStageStatus.SKIPPED or stage.status == PipelineStageStatus.CANCELLED:
                    continue
                
                # Check dependencies
                dependencies_met = True
                for dep_order in stage.dependencies:
                    dep_stages = [s for s in stages if s.order == dep_order]
                    if not dep_stages or dep_stages[0].status != PipelineStageStatus.SUCCEEDED:
                        dependencies_met = False
                        break
                
                if not dependencies_met:
                    stage.status = PipelineStageStatus.SKIPPED
                    stage.logs.append(f"Skipped due to failed dependencies")
                    continue
                
                # Execute the stage
                try:
                    stage.status = PipelineStageStatus.RUNNING
                    stage.started_at = datetime.now()
                    pipeline.updated_at = datetime.now()
                    
                    # Call the appropriate stage handler
                    handler = self.stage_handlers.get(stage.type)
                    if handler:
                        await handler(pipeline, stage)
                    else:
                        raise ValueError(f"No handler for stage type: {stage.type}")
                    
                    stage.status = PipelineStageStatus.SUCCEEDED
                except Exception as e:
                    logger.error(f"Stage failed: {stage.id} - {e}")
                    stage.status = PipelineStageStatus.FAILED
                    stage.logs.append(f"Error: {str(e)}")
                    
                    # If a stage fails, the pipeline fails
                    pipeline.status = PipelineStatus.FAILED
                    break
                finally:
                    stage.completed_at = datetime.now()
                    pipeline.updated_at = datetime.now()
            
            # If all stages succeeded, mark the pipeline as succeeded
            if pipeline.status == PipelineStatus.RUNNING:
                pipeline.status = PipelineStatus.SUCCEEDED
            
            pipeline.completed_at = datetime.now()
            pipeline.updated_at = datetime.now()
            
            logger.info(f"Pipeline completed: {pipeline_id} with status {pipeline.status}")
        except Exception as e:
            logger.error(f"Pipeline execution failed: {pipeline_id} - {e}")
            pipeline.status = PipelineStatus.FAILED
            pipeline.completed_at = datetime.now()
            pipeline.updated_at = datetime.now()
    
    async def _handle_build_stage(self, pipeline: DeploymentPipeline, stage: PipelineStage) -> None:
        """
        Handle a build stage.
        
        Args:
            pipeline: The pipeline
            stage: The stage
        """
        stage.logs.append(f"Starting build for application {pipeline.application_id}")
        
        # In a real implementation, this would:
        # 1. Clone the application code
        # 2. Build the container image
        # 3. Push the image to the registry
        
        # For now, we'll simulate these steps
        await asyncio.sleep(2)
        stage.logs.append("Cloning application code")
        
        await asyncio.sleep(2)
        stage.logs.append("Building container image")
        
        # Create a mock image
        image = await self.container_registry.create_image(
            name=f"app-{pipeline.application_id}",
            repository=f"user-{pipeline.user_id}",
            owner_id=pipeline.user_id,
            visibility="private",
            description=f"Application image for {pipeline.application_id}",
            labels={
                "project_id": pipeline.project_id,
                "application_id": pipeline.application_id,
                "pipeline_id": pipeline.id
            }
        )
        
        pipeline.image_id = image.id
        
        await asyncio.sleep(2)
        stage.logs.append(f"Image built and pushed to registry: {image.repository}/{image.name}:latest")
        
        # Store the image ID as an artifact
        stage.artifacts["image_id"] = image.id
        stage.artifacts["image_name"] = f"{image.repository}/{image.name}:latest"
    
    async def _handle_test_stage(self, pipeline: DeploymentPipeline, stage: PipelineStage) -> None:
        """
        Handle a test stage.
        
        Args:
            pipeline: The pipeline
            stage: The stage
        """
        stage.logs.append(f"Running tests for application {pipeline.application_id}")
        
        # In a real implementation, this would:
        # 1. Pull the image from the registry
        # 2. Run tests against the image
        # 3. Collect test results
        
        # For now, we'll simulate these steps
        await asyncio.sleep(2)
        stage.logs.append("Pulling image from registry")
        
        await asyncio.sleep(2)
        stage.logs.append(f"Running test command: {stage.config.get('test_command', 'npm test')}")
        
        await asyncio.sleep(2)
        stage.logs.append("Tests completed successfully")
        
        # Store test results as artifacts
        stage.artifacts["test_results"] = "All tests passed"
        stage.artifacts["test_coverage"] = "85%"
    
    async def _handle_security_scan_stage(self, pipeline: DeploymentPipeline, stage: PipelineStage) -> None:
        """
        Handle a security scan stage.
        
        Args:
            pipeline: The pipeline
            stage: The stage
        """
        stage.logs.append(f"Running security scan for application {pipeline.application_id}")
        
        # In a real implementation, this would:
        # 1. Scan the image for vulnerabilities
        # 2. Check against security policies
        # 3. Generate security reports
        
        # For now, we'll simulate these steps
        await asyncio.sleep(2)
        stage.logs.append("Scanning image for vulnerabilities")
        
        await asyncio.sleep(2)
        stage.logs.append("Checking against security policies")
        
        await asyncio.sleep(2)
        stage.logs.append("Security scan completed")
        
        # Store security scan results as artifacts
        stage.artifacts["security_scan_results"] = "No critical vulnerabilities found"
        stage.artifacts["security_score"] = "A"
    
    async def _handle_deploy_stage(self, pipeline: DeploymentPipeline, stage: PipelineStage) -> None:
        """
        Handle a deploy stage.
        
        Args:
            pipeline: The pipeline
            stage: The stage
        """
        deployment_target = stage.config.get("deployment_target", DeploymentTarget.DEVELOPMENT)
        replicas = stage.config.get("replicas", 1)
        
        stage.logs.append(f"Deploying application {pipeline.application_id} to {deployment_target}")
        
        # In a real implementation, this would:
        # 1. Create or update Kubernetes resources
        # 2. Deploy the application
        # 3. Wait for the deployment to complete
        
        # For now, we'll simulate these steps
        await asyncio.sleep(2)
        stage.logs.append("Creating Kubernetes resources")
        
        # Create a namespace for the application
        namespace = f"user-{pipeline.user_id}-project-{pipeline.project_id}"
        namespace_resource = await self.container_orchestrator.create_namespace(
            name=namespace,
            labels={
                "user_id": pipeline.user_id,
                "project_id": pipeline.project_id
            }
        )
        
        stage.logs.append(f"Created namespace: {namespace}")
        
        # Get the image name
        image_name = stage.artifacts.get("image_name", f"user-{pipeline.user_id}/app-{pipeline.application_id}:latest")
        
        # Create a deployment
        deployment_name = f"app-{pipeline.application_id}"
        deployment_resource = await self.container_orchestrator.create_deployment(
            name=deployment_name,
            namespace=namespace,
            image=image_name,
            replicas=replicas,
            labels={
                "app": deployment_name,
                "user_id": pipeline.user_id,
                "project_id": pipeline.project_id,
                "application_id": pipeline.application_id
            },
            env_vars=pipeline.environment,
            ports=[8080]
        )
        
        stage.logs.append(f"Created deployment: {deployment_name}")
        
        # Create a service
        service_name = f"app-{pipeline.application_id}"
        service_resource = await self.container_orchestrator.create_service(
            name=service_name,
            namespace=namespace,
            selector={
                "app": deployment_name
            },
            ports=[
                {
                    "port": 80,
                    "target_port": 8080,
                    "protocol": "TCP"
                }
            ],
            service_type="ClusterIP",
            labels={
                "app": service_name,
                "user_id": pipeline.user_id,
                "project_id": pipeline.project_id,
                "application_id": pipeline.application_id
            }
        )
        
        stage.logs.append(f"Created service: {service_name}")
        
        # Store deployment information as artifacts
        stage.artifacts["namespace"] = namespace
        stage.artifacts["deployment_name"] = deployment_name
        stage.artifacts["service_name"] = service_name
        stage.artifacts["service_url"] = f"http://{service_name}.{namespace}.svc.cluster.local"
    
    async def _handle_validate_stage(self, pipeline: DeploymentPipeline, stage: PipelineStage) -> None:
        """
        Handle a validate stage.
        
        Args:
            pipeline: The pipeline
            stage: The stage
        """
        stage.logs.append(f"Validating deployment for application {pipeline.application_id}")
        
        # In a real implementation, this would:
        # 1. Check if the deployment is healthy
        # 2. Run validation tests
        # 3. Verify the application is working as expected
        
        # For now, we'll simulate these steps
        await asyncio.sleep(2)
        stage.logs.append("Checking deployment status")
        
        # Get deployment information from previous stage
        deployment_stage = next((s for s in pipeline.stages if s.type == PipelineStageType.DEPLOY), None)
        if not deployment_stage or not deployment_stage.artifacts:
            raise ValueError("Deployment information not found")
        
        namespace = deployment_stage.artifacts.get("namespace")
        deployment_name = deployment_stage.artifacts.get("deployment_name")
        service_name = deployment_stage.artifacts.get("service_name")
        
        if not namespace or not deployment_name or not service_name:
            raise ValueError("Deployment information incomplete")
        
        # Check deployment status
        deployment_status = await self.container_orchestrator.get_resource_status(
            kind="Deployment",
            name=deployment_name,
            namespace=namespace
        )
        
        stage.logs.append(f"Deployment status: {json.dumps(deployment_status)}")
        
        # Check if the deployment is available
        if deployment_status.get("available_replicas", 0) < 1:
            raise ValueError("Deployment is not available")
        
        await asyncio.sleep(2)
        stage.logs.append("Running health checks")
        
        # Simulate health checks
        health_check_path = stage.config.get("health_check_path", "/health")
        health_check_url = f"http://{service_name}.{namespace}.svc.cluster.local{health_check_path}"
        
        stage.logs.append(f"Health check URL: {health_check_url}")
        stage.logs.append("Health check passed")
        
        # Store validation results as artifacts
        stage.artifacts["validation_status"] = "passed"
        stage.artifacts["health_check_url"] = health_check_url
    
    async def _handle_rollback_stage(self, pipeline: DeploymentPipeline, stage: PipelineStage) -> None:
        """
        Handle a rollback stage.
        
        Args:
            pipeline: The pipeline
            stage: The stage
        """
        stage.logs.append(f"Rolling back deployment for application {pipeline.application_id}")
        
        # In a real implementation, this would:
        # 1. Identify the previous successful deployment
        # 2. Roll back to that deployment
        # 3. Verify the rollback was successful
        
        # For now, we'll simulate these steps
        await asyncio.sleep(2)
        stage.logs.append("Identifying previous deployment")
        
        # Get deployment information from deploy stage
        deployment_stage = next((s for s in pipeline.stages if s.type == PipelineStageType.DEPLOY), None)
        if not deployment_stage or not deployment_stage.artifacts:
            raise ValueError("Deployment information not found")
        
        namespace = deployment_stage.artifacts.get("namespace")
        deployment_name = deployment_stage.artifacts.get("deployment_name")
        
        if not namespace or not deployment_name:
            raise ValueError("Deployment information incomplete")
        
        await asyncio.sleep(2)
        stage.logs.append(f"Rolling back deployment: {deployment_name} in namespace {namespace}")
        
        # Simulate rollback
        await asyncio.sleep(2)
        stage.logs.append("Rollback completed successfully")
        
        # Store rollback results as artifacts
        stage.artifacts["rollback_status"] = "succeeded"
        stage.artifacts["previous_revision"] = "1"

# Singleton instance
deployment_pipeline_service = DeploymentPipelineService()
