"""
Adaptive Workflow Generator

This module provides functionality for generating and adapting project workflows
based on project requirements, team capabilities, and container events.
"""

import os
import logging
import asyncio
import json
import uuid
from typing import Dict, List, Optional, Union, Any, Callable
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

class WorkflowType(str, Enum):
    """Types of project workflows."""
    AGILE = "agile"
    WATERFALL = "waterfall"
    KANBAN = "kanban"
    DEVOPS = "devops"
    CUSTOM = "custom"

class WorkflowStageType(str, Enum):
    """Types of workflow stages."""
    PLANNING = "planning"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    REVIEW = "review"
    MAINTENANCE = "maintenance"

class WorkflowTaskStatus(str, Enum):
    """Status of a workflow task."""
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"

class WorkflowTask(BaseModel):
    """A task in a workflow."""
    id: str
    name: str
    description: Optional[str] = None
    status: WorkflowTaskStatus = WorkflowTaskStatus.BACKLOG
    stage_id: str
    assignee_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    priority: int = 0  # Higher number = higher priority
    dependencies: List[str] = Field(default_factory=list)  # IDs of dependent tasks
    tags: List[str] = Field(default_factory=list)
    container_events: List[str] = Field(default_factory=list)  # IDs of related container events
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowStage(BaseModel):
    """A stage in a workflow."""
    id: str
    name: str
    description: Optional[str] = None
    type: WorkflowStageType
    order: int
    tasks: List[WorkflowTask] = Field(default_factory=list)
    entry_criteria: Dict[str, Any] = Field(default_factory=dict)
    exit_criteria: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProjectWorkflow(BaseModel):
    """A project workflow."""
    id: str
    name: str
    description: Optional[str] = None
    type: WorkflowType
    project_id: str
    created_at: datetime
    updated_at: datetime
    stages: List[WorkflowStage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: int = 1
    is_active: bool = True
    created_by: str
    adapted_from: Optional[str] = None  # ID of the workflow this was adapted from

class WorkflowAdapter(BaseModel):
    """A workflow adaptation rule."""
    id: str
    name: str
    description: Optional[str] = None
    trigger_condition: Dict[str, Any]  # Condition that triggers the adaptation
    adaptation_action: Dict[str, Any]  # Action to take when triggered
    priority: int = 0  # Higher number = higher priority
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AdaptiveWorkflowGenerator:
    """
    Adaptive Workflow Generator
    
    Generates and adapts project workflows based on project requirements,
    team capabilities, and container events, including:
    - Creating workflow templates for different project types
    - Adapting workflows based on project events and metrics
    - Integrating with container events for workflow automation
    - Providing recommendations for workflow optimization
    """
    
    def __init__(self):
        """Initialize the Adaptive Workflow Generator."""
        self.workflows: Dict[str, ProjectWorkflow] = {}
        self.adapters: Dict[str, WorkflowAdapter] = {}
        self.template_workflows: Dict[str, ProjectWorkflow] = {}
        
        # Initialize template workflows
        self._initialize_template_workflows()
        
        # Initialize default adapters
        self._initialize_default_adapters()
        
        logger.info("Adaptive Workflow Generator initialized")
    
    def _initialize_template_workflows(self):
        """Initialize template workflows for different project types."""
        # Agile workflow template
        agile_workflow = self._create_agile_workflow_template()
        self.template_workflows[agile_workflow.id] = agile_workflow
        
        # Waterfall workflow template
        waterfall_workflow = self._create_waterfall_workflow_template()
        self.template_workflows[waterfall_workflow.id] = waterfall_workflow
        
        # Kanban workflow template
        kanban_workflow = self._create_kanban_workflow_template()
        self.template_workflows[kanban_workflow.id] = kanban_workflow
        
        # DevOps workflow template
        devops_workflow = self._create_devops_workflow_template()
        self.template_workflows[devops_workflow.id] = devops_workflow
        
        logger.info(f"Initialized {len(self.template_workflows)} template workflows")
    
    def _create_agile_workflow_template(self) -> ProjectWorkflow:
        """
        Create an Agile workflow template.
        
        Returns:
            Agile workflow template
        """
        template_id = "template-agile"
        now = datetime.now()
        
        # Create stages
        stages = [
            WorkflowStage(
                id=f"{template_id}-stage-1",
                name="Product Backlog",
                description="Prioritized list of features and requirements",
                type=WorkflowStageType.PLANNING,
                order=1,
                entry_criteria={},
                exit_criteria={"min_stories": 5}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-2",
                name="Sprint Planning",
                description="Planning the work for the current sprint",
                type=WorkflowStageType.PLANNING,
                order=2,
                entry_criteria={"backlog_prioritized": True},
                exit_criteria={"sprint_backlog_defined": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-3",
                name="Sprint Backlog",
                description="Tasks planned for the current sprint",
                type=WorkflowStageType.DEVELOPMENT,
                order=3,
                entry_criteria={"sprint_planning_complete": True},
                exit_criteria={}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-4",
                name="In Progress",
                description="Tasks currently being worked on",
                type=WorkflowStageType.DEVELOPMENT,
                order=4,
                entry_criteria={},
                exit_criteria={}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-5",
                name="Testing",
                description="Tasks being tested",
                type=WorkflowStageType.TESTING,
                order=5,
                entry_criteria={"development_complete": True},
                exit_criteria={"tests_passing": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-6",
                name="Review",
                description="Tasks under review",
                type=WorkflowStageType.REVIEW,
                order=6,
                entry_criteria={"testing_complete": True},
                exit_criteria={"review_approved": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-7",
                name="Done",
                description="Completed tasks",
                type=WorkflowStageType.DEPLOYMENT,
                order=7,
                entry_criteria={"review_approved": True},
                exit_criteria={}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-8",
                name="Sprint Review",
                description="Review of the completed sprint",
                type=WorkflowStageType.REVIEW,
                order=8,
                entry_criteria={"sprint_complete": True},
                exit_criteria={"sprint_reviewed": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-9",
                name="Sprint Retrospective",
                description="Retrospective of the completed sprint",
                type=WorkflowStageType.REVIEW,
                order=9,
                entry_criteria={"sprint_reviewed": True},
                exit_criteria={"retrospective_complete": True}
            )
        ]
        
        # Create the workflow template
        return ProjectWorkflow(
            id=template_id,
            name="Agile Workflow Template",
            description="Standard Agile workflow with sprints, backlog, and retrospectives",
            type=WorkflowType.AGILE,
            project_id="template",
            created_at=now,
            updated_at=now,
            stages=stages,
            metadata={
                "sprint_duration_days": 14,
                "recommended_team_size": "5-9",
                "container_integration": {
                    "enabled": True,
                    "event_triggers": [
                        {
                            "event_type": "container_deploy",
                            "action": "move_task_to_stage",
                            "target_stage": "Testing"
                        }
                    ]
                }
            },
            created_by="system"
        )
    
    def _create_waterfall_workflow_template(self) -> ProjectWorkflow:
        """
        Create a Waterfall workflow template.
        
        Returns:
            Waterfall workflow template
        """
        template_id = "template-waterfall"
        now = datetime.now()
        
        # Create stages
        stages = [
            WorkflowStage(
                id=f"{template_id}-stage-1",
                name="Requirements",
                description="Gathering and documenting requirements",
                type=WorkflowStageType.PLANNING,
                order=1,
                entry_criteria={},
                exit_criteria={"requirements_approved": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-2",
                name="Design",
                description="System and software design",
                type=WorkflowStageType.DESIGN,
                order=2,
                entry_criteria={"requirements_complete": True},
                exit_criteria={"design_approved": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-3",
                name="Implementation",
                description="Development and coding",
                type=WorkflowStageType.DEVELOPMENT,
                order=3,
                entry_criteria={"design_complete": True},
                exit_criteria={"implementation_complete": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-4",
                name="Verification",
                description="Testing and quality assurance",
                type=WorkflowStageType.TESTING,
                order=4,
                entry_criteria={"implementation_complete": True},
                exit_criteria={"verification_complete": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-5",
                name="Deployment",
                description="System deployment and release",
                type=WorkflowStageType.DEPLOYMENT,
                order=5,
                entry_criteria={"verification_complete": True},
                exit_criteria={"deployment_complete": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-6",
                name="Maintenance",
                description="System maintenance and support",
                type=WorkflowStageType.MAINTENANCE,
                order=6,
                entry_criteria={"deployment_complete": True},
                exit_criteria={}
            )
        ]
        
        # Create the workflow template
        return ProjectWorkflow(
            id=template_id,
            name="Waterfall Workflow Template",
            description="Traditional Waterfall workflow with sequential phases",
            type=WorkflowType.WATERFALL,
            project_id="template",
            created_at=now,
            updated_at=now,
            stages=stages,
            metadata={
                "phase_approval_required": True,
                "recommended_documentation_level": "high",
                "container_integration": {
                    "enabled": True,
                    "event_triggers": [
                        {
                            "event_type": "container_build",
                            "action": "update_task_status",
                            "status": "in_progress"
                        }
                    ]
                }
            },
            created_by="system"
        )
    
    def _create_kanban_workflow_template(self) -> ProjectWorkflow:
        """
        Create a Kanban workflow template.
        
        Returns:
            Kanban workflow template
        """
        template_id = "template-kanban"
        now = datetime.now()
        
        # Create stages
        stages = [
            WorkflowStage(
                id=f"{template_id}-stage-1",
                name="Backlog",
                description="Backlog of tasks to be worked on",
                type=WorkflowStageType.PLANNING,
                order=1,
                entry_criteria={},
                exit_criteria={}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-2",
                name="To Do",
                description="Tasks ready to be worked on",
                type=WorkflowStageType.PLANNING,
                order=2,
                entry_criteria={"prioritized": True},
                exit_criteria={}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-3",
                name="In Progress",
                description="Tasks currently being worked on",
                type=WorkflowStageType.DEVELOPMENT,
                order=3,
                entry_criteria={},
                exit_criteria={}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-4",
                name="Review",
                description="Tasks being reviewed",
                type=WorkflowStageType.REVIEW,
                order=4,
                entry_criteria={"development_complete": True},
                exit_criteria={"review_complete": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-5",
                name="Done",
                description="Completed tasks",
                type=WorkflowStageType.DEPLOYMENT,
                order=5,
                entry_criteria={"review_complete": True},
                exit_criteria={}
            )
        ]
        
        # Create the workflow template
        return ProjectWorkflow(
            id=template_id,
            name="Kanban Workflow Template",
            description="Kanban workflow with continuous flow",
            type=WorkflowType.KANBAN,
            project_id="template",
            created_at=now,
            updated_at=now,
            stages=stages,
            metadata={
                "wip_limits": {
                    "In Progress": 5,
                    "Review": 3
                },
                "continuous_flow": True,
                "container_integration": {
                    "enabled": True,
                    "event_triggers": [
                        {
                            "event_type": "container_test",
                            "action": "move_task_to_stage",
                            "target_stage": "Review"
                        }
                    ]
                }
            },
            created_by="system"
        )
    
    def _create_devops_workflow_template(self) -> ProjectWorkflow:
        """
        Create a DevOps workflow template.
        
        Returns:
            DevOps workflow template
        """
        template_id = "template-devops"
        now = datetime.now()
        
        # Create stages
        stages = [
            WorkflowStage(
                id=f"{template_id}-stage-1",
                name="Plan",
                description="Planning and requirements gathering",
                type=WorkflowStageType.PLANNING,
                order=1,
                entry_criteria={},
                exit_criteria={"plan_approved": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-2",
                name="Code",
                description="Development and coding",
                type=WorkflowStageType.DEVELOPMENT,
                order=2,
                entry_criteria={"plan_complete": True},
                exit_criteria={"code_complete": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-3",
                name="Build",
                description="Building and packaging",
                type=WorkflowStageType.DEVELOPMENT,
                order=3,
                entry_criteria={"code_complete": True},
                exit_criteria={"build_successful": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-4",
                name="Test",
                description="Automated testing",
                type=WorkflowStageType.TESTING,
                order=4,
                entry_criteria={"build_successful": True},
                exit_criteria={"tests_passing": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-5",
                name="Release",
                description="Release preparation",
                type=WorkflowStageType.DEPLOYMENT,
                order=5,
                entry_criteria={"tests_passing": True},
                exit_criteria={"release_approved": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-6",
                name="Deploy",
                description="Deployment to production",
                type=WorkflowStageType.DEPLOYMENT,
                order=6,
                entry_criteria={"release_approved": True},
                exit_criteria={"deployment_successful": True}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-7",
                name="Operate",
                description="Operation and monitoring",
                type=WorkflowStageType.MAINTENANCE,
                order=7,
                entry_criteria={"deployment_successful": True},
                exit_criteria={}
            ),
            WorkflowStage(
                id=f"{template_id}-stage-8",
                name="Monitor",
                description="Monitoring and feedback",
                type=WorkflowStageType.MAINTENANCE,
                order=8,
                entry_criteria={"deployment_successful": True},
                exit_criteria={}
            )
        ]
        
        # Create the workflow template
        return ProjectWorkflow(
            id=template_id,
            name="DevOps Workflow Template",
            description="DevOps workflow with continuous integration and deployment",
            type=WorkflowType.DEVOPS,
            project_id="template",
            created_at=now,
            updated_at=now,
            stages=stages,
            metadata={
                "ci_cd_enabled": True,
                "automated_testing": True,
                "container_integration": {
                    "enabled": True,
                    "event_triggers": [
                        {
                            "event_type": "container_build",
                            "action": "move_task_to_stage",
                            "target_stage": "Test"
                        },
                        {
                            "event_type": "container_deploy",
                            "action": "move_task_to_stage",
                            "target_stage": "Operate"
                        }
                    ]
                }
            },
            created_by="system"
        )
    
    def _initialize_default_adapters(self):
        """Initialize default workflow adapters."""
        # Add high task volume adapter
        high_task_adapter = WorkflowAdapter(
            id=str(uuid.uuid4()),
            name="High Task Volume Adapter",
            description="Adapts workflow when task volume is high by adding more parallel stages",
            trigger_condition={
                "type": "task_count",
                "operator": "greater_than",
                "value": 50
            },
            adaptation_action={
                "type": "add_parallel_stages",
                "stages": ["development"]
            },
            priority=10,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.adapters[high_task_adapter.id] = high_task_adapter
        
        # Add container resource constraint adapter
        resource_adapter = WorkflowAdapter(
            id=str(uuid.uuid4()),
            name="Resource Constraint Adapter",
            description="Adapts workflow when container resources are constrained",
            trigger_condition={
                "type": "container_metric",
                "metric": "resource_utilization",
                "operator": "greater_than",
                "value": 0.85
            },
            adaptation_action={
                "type": "prioritize_tasks",
                "criteria": "resource_efficiency"
            },
            priority=20,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.adapters[resource_adapter.id] = resource_adapter
        
        # Add deadline pressure adapter
        deadline_adapter = WorkflowAdapter(
            id=str(uuid.uuid4()),
            name="Deadline Pressure Adapter",
            description="Adapts workflow when project deadline is approaching",
            trigger_condition={
                "type": "time_to_deadline",
                "operator": "less_than",
                "value": 14  # days
            },
            adaptation_action={
                "type": "optimize_critical_path",
                "focus_areas": ["testing", "deployment"]
            },
            priority=30,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.adapters[deadline_adapter.id] = deadline_adapter
        
        logger.info(f"Initialized {len(self.adapters)} default workflow adapters")
    
    async def generate_workflow(self, project_id: str, project_name: str, 
                               workflow_type: WorkflowType, created_by: str,
                               project_metadata: Optional[Dict[str, Any]] = None) -> ProjectWorkflow:
        """
        Generate a new workflow for a project based on the specified workflow type.
        
        Args:
            project_id: ID of the project
            project_name: Name of the project
            workflow_type: Type of workflow to generate
            created_by: ID of the user creating the workflow
            project_metadata: Optional metadata about the project to inform workflow generation
            
        Returns:
            Generated project workflow
        """
        logger.info(f"Generating {workflow_type} workflow for project {project_id}")
        
        # Find the template for the specified workflow type
        template = None
        for template_id, template_workflow in self.template_workflows.items():
            if template_workflow.type == workflow_type:
                template = template_workflow
                break
        
        if not template:
            raise ValueError(f"No template found for workflow type {workflow_type}")
        
        # Create a new workflow based on the template
        now = datetime.now()
        workflow_id = str(uuid.uuid4())
        
        # Create a deep copy of the stages
        stages = []
        for template_stage in template.stages:
            # Generate a new ID for the stage
            stage_id = f"{workflow_id}-stage-{template_stage.order}"
            
            # Create a new stage based on the template stage
            stage = WorkflowStage(
                id=stage_id,
                name=template_stage.name,
                description=template_stage.description,
                type=template_stage.type,
                order=template_stage.order,
                entry_criteria=template_stage.entry_criteria.copy(),
                exit_criteria=template_stage.exit_criteria.copy(),
                tasks=[],  # Start with no tasks
                metadata=template_stage.metadata.copy() if template_stage.metadata else {}
            )
            stages.append(stage)
        
        # Create the new workflow
        workflow = ProjectWorkflow(
            id=workflow_id,
            name=f"{project_name} {template.name.replace('Template', 'Workflow')}",
            description=f"Workflow for {project_name} based on {template.name}",
            type=workflow_type,
            project_id=project_id,
            created_at=now,
            updated_at=now,
            stages=stages,
            metadata={
                "template_id": template.id,
                "adapted": False,
                "adaptation_history": [],
                "container_integration": template.metadata.get("container_integration", {})
            },
            version=1,
            is_active=True,
            created_by=created_by,
            adapted_from=template.id
        )
        
        # Store the workflow
        self.workflows[workflow.id] = workflow
        
        # If project metadata is provided, adapt the workflow based on it
        if project_metadata:
            workflow = await self.adapt_workflow_to_project(workflow.id, project_metadata)
        
        logger.info(f"Generated workflow {workflow.id} for project {project_id}")
        return workflow
    
    async def create_custom_workflow(self, project_id: str, project_name: str, 
                                    stages: List[WorkflowStage], created_by: str,
                                    metadata: Optional[Dict[str, Any]] = None) -> ProjectWorkflow:
        """
        Create a custom workflow with the specified stages.
        
        Args:
            project_id: ID of the project
            project_name: Name of the project
            stages: List of workflow stages
            created_by: ID of the user creating the workflow
            metadata: Optional metadata for the workflow
            
        Returns:
            Created custom workflow
        """
        logger.info(f"Creating custom workflow for project {project_id}")
        
        # Create a new workflow
        now = datetime.now()
        workflow_id = str(uuid.uuid4())
        
        # Ensure stages have unique IDs and correct order
        for i, stage in enumerate(stages):
            stage.id = f"{workflow_id}-stage-{i+1}"
            stage.order = i + 1
        
        # Create the workflow
        workflow = ProjectWorkflow(
            id=workflow_id,
            name=f"{project_name} Custom Workflow",
            description=f"Custom workflow for {project_name}",
            type=WorkflowType.CUSTOM,
            project_id=project_id,
            created_at=now,
            updated_at=now,
            stages=stages,
            metadata=metadata or {
                "custom": True,
                "adapted": False,
                "adaptation_history": [],
                "container_integration": {
                    "enabled": True,
                    "event_triggers": []
                }
            },
            version=1,
            is_active=True,
            created_by=created_by
        )
        
        # Store the workflow
        self.workflows[workflow.id] = workflow
        
        logger.info(f"Created custom workflow {workflow.id} for project {project_id}")
        return workflow
    
    async def get_workflow(self, workflow_id: str) -> ProjectWorkflow:
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: ID of the workflow to get
            
        Returns:
            Workflow with the specified ID
            
        Raises:
            ValueError: If no workflow with the specified ID exists
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"No workflow found with ID {workflow_id}")
        
        return self.workflows[workflow_id]
    
    async def get_project_workflows(self, project_id: str) -> List[ProjectWorkflow]:
        """
        Get all workflows for a project.
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of workflows for the project
        """
        return [
            workflow for workflow in self.workflows.values()
            if workflow.project_id == project_id
        ]
    
    async def get_active_project_workflow(self, project_id: str) -> Optional[ProjectWorkflow]:
        """
        Get the active workflow for a project.
        
        Args:
            project_id: ID of the project
            
        Returns:
            Active workflow for the project, or None if no active workflow exists
        """
        for workflow in self.workflows.values():
            if workflow.project_id == project_id and workflow.is_active:
                return workflow
        
        return None
    
    async def adapt_workflow_to_project(self, workflow_id: str, 
                                       project_metadata: Dict[str, Any]) -> ProjectWorkflow:
        """
        Adapt a workflow to better fit the project based on project metadata.
        
        Args:
            workflow_id: ID of the workflow to adapt
            project_metadata: Metadata about the project to inform adaptation
            
        Returns:
            Adapted workflow
        """
        logger.info(f"Adapting workflow {workflow_id} to project metadata")
        
        workflow = await self.get_workflow(workflow_id)
        now = datetime.now()
        
        # Create a new version of the workflow
        new_workflow_id = str(uuid.uuid4())
        
        # Create a deep copy of the stages
        new_stages = []
        for stage in workflow.stages:
            # Generate a new ID for the stage
            stage_id = f"{new_workflow_id}-stage-{stage.order}"
            
            # Create a new stage based on the original stage
            new_stage = WorkflowStage(
                id=stage_id,
                name=stage.name,
                description=stage.description,
                type=stage.type,
                order=stage.order,
                entry_criteria=stage.entry_criteria.copy(),
                exit_criteria=stage.exit_criteria.copy(),
                tasks=[],  # Start with no tasks
                metadata=stage.metadata.copy() if stage.metadata else {}
            )
            new_stages.append(new_stage)
        
        # Apply adaptations based on project metadata
        adapted_stages = await self._apply_project_adaptations(new_stages, project_metadata)
        
        # Create the new workflow
        new_workflow = ProjectWorkflow(
            id=new_workflow_id,
            name=workflow.name,
            description=f"{workflow.description} (Adapted)",
            type=workflow.type,
            project_id=workflow.project_id,
            created_at=now,
            updated_at=now,
            stages=adapted_stages,
            metadata={
                **workflow.metadata,
                "adapted": True,
                "adaptation_history": [
                    *workflow.metadata.get("adaptation_history", []),
                    {
                        "timestamp": now.isoformat(),
                        "reason": "project_metadata",
                        "metadata": project_metadata
                    }
                ]
            },
            version=workflow.version + 1,
            is_active=True,
            created_by=workflow.created_by,
            adapted_from=workflow.id
        )
        
        # Update the original workflow to be inactive
        workflow.is_active = False
        workflow.updated_at = now
        
        # Store the new workflow
        self.workflows[new_workflow.id] = new_workflow
        
        logger.info(f"Adapted workflow {workflow_id} to {new_workflow.id}")
        return new_workflow
    
    async def _apply_project_adaptations(self, stages: List[WorkflowStage], 
                                        project_metadata: Dict[str, Any]) -> List[WorkflowStage]:
        """
        Apply adaptations to workflow stages based on project metadata.
        
        Args:
            stages: Workflow stages to adapt
            project_metadata: Metadata about the project to inform adaptation
            
        Returns:
            Adapted workflow stages
        """
        # Apply adaptations based on team size
        if "team_size" in project_metadata:
            team_size = project_metadata["team_size"]
            if team_size < 3:
                # For small teams, simplify the workflow
                stages = self._simplify_workflow_for_small_team(stages)
            elif team_size > 10:
                # For large teams, add more parallel stages
                stages = self._expand_workflow_for_large_team(stages)
        
        # Apply adaptations based on project complexity
        if "complexity" in project_metadata:
            complexity = project_metadata["complexity"]
            if complexity == "high":
                # For complex projects, add more review stages
                stages = self._add_review_stages_for_complex_project(stages)
            elif complexity == "low":
                # For simple projects, simplify the workflow
                stages = self._simplify_workflow_for_simple_project(stages)
        
        # Apply adaptations based on project duration
        if "duration_months" in project_metadata:
            duration = project_metadata["duration_months"]
            if duration < 3:
                # For short projects, optimize for speed
                stages = self._optimize_workflow_for_speed(stages)
            elif duration > 12:
                # For long projects, optimize for maintainability
                stages = self._optimize_workflow_for_maintainability(stages)
        
        # Apply adaptations based on application type
        if "application_type" in project_metadata:
            app_type = project_metadata["application_type"]
            if app_type == "web":
                # For web applications, optimize for deployment frequency
                stages = self._optimize_workflow_for_web_application(stages)
            elif app_type == "mobile":
                # For mobile applications, add testing stages
                stages = self._optimize_workflow_for_mobile_application(stages)
            elif app_type == "desktop":
                # For desktop applications, add release stages
                stages = self._optimize_workflow_for_desktop_application(stages)
        
        # Ensure stages have correct order
        for i, stage in enumerate(stages):
            stage.order = i + 1
        
        return stages
    
    def _simplify_workflow_for_small_team(self, stages: List[WorkflowStage]) -> List[WorkflowStage]:
        """Simplify workflow for small teams."""
        # Remove redundant stages
        simplified_stages = []
        essential_stage_types = {
            WorkflowStageType.PLANNING,
            WorkflowStageType.DEVELOPMENT,
            WorkflowStageType.TESTING,
            WorkflowStageType.DEPLOYMENT
        }
        
        # Keep only essential stages and merge similar ones
        for stage in stages:
            if stage.type in essential_stage_types:
                # Check if we already have a stage of this type
                existing_stage = next((s for s in simplified_stages if s.type == stage.type), None)
                if existing_stage:
                    # Merge entry and exit criteria
                    existing_stage.entry_criteria.update(stage.entry_criteria)
                    existing_stage.exit_criteria.update(stage.exit_criteria)
                else:
                    simplified_stages.append(stage)
        
        return simplified_stages
    
    def _expand_workflow_for_large_team(self, stages: List[WorkflowStage]) -> List[WorkflowStage]:
        """Expand workflow for large teams."""
        expanded_stages = list(stages)
        
        # Add parallel development stages
        dev_stages = [s for s in stages if s.type == WorkflowStageType.DEVELOPMENT]
        if dev_stages:
            # Find the last development stage
            last_dev_stage = max(dev_stages, key=lambda s: s.order)
            last_dev_index = expanded_stages.index(last_dev_stage)
            
            # Add parallel development stages
            parallel_dev_stage = WorkflowStage(
                id=f"{last_dev_stage.id}-parallel",
                name=f"{last_dev_stage.name} (Parallel)",
                description=f"Parallel {last_dev_stage.description.lower()}",
                type=WorkflowStageType.DEVELOPMENT,
                order=last_dev_stage.order + 0.5,  # Will be fixed later
                entry_criteria=last_dev_stage.entry_criteria.copy(),
                exit_criteria=last_dev_stage.exit_criteria.copy(),
                tasks=[],
                metadata=last_dev_stage.metadata.copy() if last_dev_stage.metadata else {}
            )
            expanded_stages.insert(last_dev_index + 1, parallel_dev_stage)
        
        # Add more testing stages
        test_stages = [s for s in stages if s.type == WorkflowStageType.TESTING]
        if test_stages:
            # Find the last testing stage
            last_test_stage = max(test_stages, key=lambda s: s.order)
            last_test_index = expanded_stages.index(last_test_stage)
            
            # Add specialized testing stages
            integration_test_stage = WorkflowStage(
                id=f"{last_test_stage.id}-integration",
                name="Integration Testing",
                description="Testing integration between components",
                type=WorkflowStageType.TESTING,
                order=last_test_stage.order + 0.5,  # Will be fixed later
                entry_criteria=last_test_stage.entry_criteria.copy(),
                exit_criteria={"integration_tests_passing": True},
                tasks=[],
                metadata=last_test_stage.metadata.copy() if last_test_stage.metadata else {}
            )
            expanded_stages.insert(last_test_index + 1, integration_test_stage)
        
        return expanded_stages
    
    def _add_review_stages_for_complex_project(self, stages: List[WorkflowStage]) -> List[WorkflowStage]:
        """Add more review stages for complex projects."""
        enhanced_stages = list(stages)
        
        # Add code review stage after development
        dev_stages = [s for s in stages if s.type == WorkflowStageType.DEVELOPMENT]
        if dev_stages:
            # Find the last development stage
            last_dev_stage = max(dev_stages, key=lambda s: s.order)
            last_dev_index = enhanced_stages.index(last_dev_stage)
            
            # Add code review stage
            code_review_stage = WorkflowStage(
                id=f"{last_dev_stage.id}-code-review",
                name="Code Review",
                description="Peer review of code changes",
                type=WorkflowStageType.REVIEW,
                order=last_dev_stage.order + 0.5,  # Will be fixed later
                entry_criteria={"development_complete": True},
                exit_criteria={"code_review_approved": True},
                tasks=[],
                metadata={}
            )
            enhanced_stages.insert(last_dev_index + 1, code_review_stage)
        
        # Add design review stage before development
        design_stages = [s for s in stages if s.type == WorkflowStageType.DESIGN]
        if design_stages:
            # Find the last design stage
            last_design_stage = max(design_stages, key=lambda s: s.order)
            last_design_index = enhanced_stages.index(last_design_stage)
            
            # Add design review stage
            design_review_stage = WorkflowStage(
                id=f"{last_design_stage.id}-design-review",
                name="Design Review",
                description="Review of design artifacts",
                type=WorkflowStageType.REVIEW,
                order=last_design_stage.order + 0.5,  # Will be fixed later
                entry_criteria={"design_complete": True},
                exit_criteria={"design_review_approved": True},
                tasks=[],
                metadata={}
            )
            enhanced_stages.insert(last_design_index + 1, design_review_stage)
        
        return enhanced_stages
    
    def _simplify_workflow_for_simple_project(self, stages: List[WorkflowStage]) -> List[WorkflowStage]:
        """Simplify workflow for simple projects."""
        # Similar to small team simplification but even more streamlined
        return self._simplify_workflow_for_small_team(stages)
    
    def _optimize_workflow_for_speed(self, stages: List[WorkflowStage]) -> List[WorkflowStage]:
        """Optimize workflow for speed."""
        # Remove non-essential stages and simplify criteria
        optimized_stages = []
        essential_stage_types = {
            WorkflowStageType.PLANNING,
            WorkflowStageType.DEVELOPMENT,
            WorkflowStageType.TESTING,
            WorkflowStageType.DEPLOYMENT
        }
        
        for stage in stages:
            if stage.type in essential_stage_types:
                # Simplify entry and exit criteria
                stage.entry_criteria = {k: v for k, v in stage.entry_criteria.items() 
                                       if k.endswith("_complete") or k.endswith("_approved")}
                stage.exit_criteria = {k: v for k, v in stage.exit_criteria.items() 
                                      if k.endswith("_complete") or k.endswith("_approved")}
                optimized_stages.append(stage)
        
        return optimized_stages
    
    def _optimize_workflow_for_maintainability(self, stages: List[WorkflowStage]) -> List[WorkflowStage]:
        """Optimize workflow for maintainability."""
        enhanced_stages = list(stages)
        
        # Add documentation stage
        planning_stages = [s for s in stages if s.type == WorkflowStageType.PLANNING]
        if planning_stages:
            # Find the last planning stage
            last_planning_stage = max(planning_stages, key=lambda s: s.order)
            last_planning_index = enhanced_stages.index(last_planning_stage)
            
            # Add documentation stage
            documentation_stage = WorkflowStage(
                id=f"{last_planning_stage.id}-documentation",
                name="Documentation",
                description="Creating and updating project documentation",
                type=WorkflowStageType.PLANNING,
                order=last_planning_stage.order + 0.5,  # Will be fixed later
                entry_criteria={"planning_complete": True},
                exit_criteria={"documentation_complete": True},
                tasks=[],
                metadata={}
            )
            enhanced_stages.insert(last_planning_index + 1, documentation_stage)
        
        # Add maintenance planning stage
        deployment_stages = [s for s in stages if s.type == WorkflowStageType.DEPLOYMENT]
        if deployment_stages:
            # Find the last deployment stage
            last_deployment_stage = max(deployment_stages, key=lambda s: s.order)
            last_deployment_index = enhanced_stages.index(last_deployment_stage)
            
            # Add maintenance planning stage
            maintenance_planning_stage = WorkflowStage(
                id=f"{last_deployment_stage.id}-maintenance-planning",
                name="Maintenance Planning",
                description="Planning for long-term maintenance",
                type=WorkflowStageType.MAINTENANCE,
                order=last_deployment_stage.order + 0.5,  # Will be fixed later
                entry_criteria={"deployment_complete": True},
                exit_criteria={"maintenance_plan_approved": True},
                tasks=[],
                metadata={}
            )
            enhanced_stages.insert(last_deployment_index + 1, maintenance_planning_stage)
        
        return enhanced_stages
    
    def _optimize_workflow_for_web_application(self, stages: List[WorkflowStage]) -> List[WorkflowStage]:
        """Optimize workflow for web applications."""
        enhanced_stages = list(stages)
        
        # Add performance testing stage
        test_stages = [s for s in stages if s.type == WorkflowStageType.TESTING]
        if test_stages:
            # Find the last testing stage
            last_test_stage = max(test_stages, key=lambda s: s.order)
            last_test_index = enhanced_stages.index(last_test_stage)
            
            # Add performance testing stage
            perf_test_stage = WorkflowStage(
                id=f"{last_test_stage.id}-performance",
                name="Performance Testing",
                description="Testing application performance and scalability",
                type=WorkflowStageType.TESTING,
                order=last_test_stage.order + 0.5,  # Will be fixed later
                entry_criteria={"functional_tests_passing": True},
                exit_criteria={"performance_tests_passing": True},
                tasks=[],
                metadata={}
            )
            enhanced_stages.insert(last_test_index + 1, perf_test_stage)
        
        # Add continuous deployment stage
        deployment_stages = [s for s in stages if s.type == WorkflowStageType.DEPLOYMENT]
        if deployment_stages:
            # Find the last deployment stage
            last_deployment_stage = max(deployment_stages, key=lambda s: s.order)
            last_deployment_index = enhanced_stages.index(last_deployment_stage)
            
            # Add continuous deployment stage
            cd_stage = WorkflowStage(
                id=f"{last_deployment_stage.id}-continuous",
                name="Continuous Deployment",
                description="Automated deployment pipeline",
                type=WorkflowStageType.DEPLOYMENT,
                order=last_deployment_stage.order + 0.5,  # Will be fixed later
                entry_criteria={"tests_passing": True},
                exit_criteria={"deployment_automated": True},
                tasks=[],
                metadata={}
            )
            enhanced_stages.insert(last_deployment_index + 1, cd_stage)
        
        return enhanced_stages
    
    def _optimize_workflow_for_mobile_application(self, stages: List[WorkflowStage]) -> List[WorkflowStage]:
        """Optimize workflow for mobile applications."""
        enhanced_stages = list(stages)
        
        # Add UI/UX testing stage
        test_stages = [s for s in stages if s.type == WorkflowStageType.TESTING]
        if test_stages:
            # Find the last testing stage
            last_test_stage = max(test_stages, key=lambda s: s.order)
            last_test_index = enhanced_stages.index(last_test_stage)
            
            # Add UI/UX testing stage
            ui_test_stage = WorkflowStage(
                id=f"{last_test_stage.id}-ui-ux",
                name="UI/UX Testing",
                description="Testing user interface and experience",
                type=WorkflowStageType.TESTING,
                order=last_test_stage.order + 0.5,  # Will be fixed later
                entry_criteria={"functional_tests_passing": True},
                exit_criteria={"ui_ux_tests_passing": True},
                tasks=[],
                metadata={}
            )
            enhanced_stages.insert(last_test_index + 1, ui_test_stage)
        
        # Add app store submission stage
        deployment_stages = [s for s in stages if s.type == WorkflowStageType.DEPLOYMENT]
        if deployment_stages:
            # Find the last deployment stage
            last_deployment_stage = max(deployment_stages, key=lambda s: s.order)
            last_deployment_index = enhanced_stages.index(last_deployment_stage)
            
            # Add app store submission stage
            app_store_stage = WorkflowStage(
                id=f"{last_deployment_stage.id}-app-store",
                name="App Store Submission",
                description="Preparing and submitting to app stores",
                type=WorkflowStageType.DEPLOYMENT,
                order=last_deployment_stage.order + 0.5,  # Will be fixed later
                entry_criteria={"tests_passing": True},
                exit_criteria={"app_store_submission_complete": True},
                tasks=[],
                metadata={}
            )
            enhanced_stages.insert(last_deployment_index + 1, app_store_stage)
        
        return enhanced_stages
    
    def _optimize_workflow_for_desktop_application(self, stages: List[WorkflowStage]) -> List[WorkflowStage]:
        """Optimize workflow for desktop applications."""
        enhanced_stages = list(stages)
        
        # Add installer testing stage
        test_stages = [s for s in stages if s.type == WorkflowStageType.TESTING]
        if test_stages:
            # Find the last testing stage
            last_test_stage = max(test_stages, key=lambda s: s.order)
            last_test_index = enhanced_stages.index(last_test_stage)
            
            # Add installer testing stage
            installer_test_stage = WorkflowStage(
                id=f"{last_test_stage.id}-installer",
                name="Installer Testing",
                description="Testing application installation process",
                type=WorkflowStageType.TESTING,
                order=last_test_stage.order + 0.5,  # Will be fixed later
                entry_criteria={"functional_tests_passing": True},
                exit_criteria={"installer_tests_passing": True},
                tasks=[],
                metadata={}
            )
            enhanced_stages.insert(last_test_index + 1, installer_test_stage)
        
        # Add release packaging stage
        deployment_stages = [s for s in stages if s.type == WorkflowStageType.DEPLOYMENT]
        if deployment_stages:
            # Find the last deployment stage
            last_deployment_stage = max(deployment_stages, key=lambda s: s.order)
            last_deployment_index = enhanced_stages.index(last_deployment_stage)
            
            # Add release packaging stage
            packaging_stage = WorkflowStage(
                id=f"{last_deployment_stage.id}-packaging",
                name="Release Packaging",
                description="Creating installation packages for distribution",
                type=WorkflowStageType.DEPLOYMENT,
                order=last_deployment_stage.order + 0.5,  # Will be fixed later
                entry_criteria={"tests_passing": True},
                exit_criteria={"packaging_complete": True},
                tasks=[],
                metadata={}
            )
            enhanced_stages.insert(last_deployment_index + 1, packaging_stage)
        
        return enhanced_stages
    
    async def process_container_event(self, event_type: str, container_id: str, 
                                     project_id: str, event_data: Dict[str, Any]) -> None:
        """
        Process a container event and adapt the workflow accordingly.
        
        Args:
            event_type: Type of container event (e.g., 'container_build', 'container_deploy')
            container_id: ID of the container that generated the event
            project_id: ID of the project associated with the container
            event_data: Additional data about the event
        """
        logger.info(f"Processing container event {event_type} for project {project_id}")
        
        # Get the active workflow for the project
        workflow = await self.get_active_project_workflow(project_id)
        if not workflow:
            logger.warning(f"No active workflow found for project {project_id}")
            return
        
        # Check if the workflow has container integration enabled
        container_integration = workflow.metadata.get("container_integration", {})
        if not container_integration.get("enabled", False):
            logger.info(f"Container integration not enabled for workflow {workflow.id}")
            return
        
        # Process event triggers
        event_triggers = container_integration.get("event_triggers", [])
        for trigger in event_triggers:
            if trigger.get("event_type") == event_type:
                action = trigger.get("action")
                if action == "move_task_to_stage":
                    await self._move_tasks_to_stage(workflow.id, trigger.get("target_stage"), container_id, event_data)
                elif action == "update_task_status":
                    await self._update_tasks_status(workflow.id, trigger.get("status"), container_id, event_data)
                elif action == "create_task":
                    await self._create_task_from_event(workflow.id, container_id, event_type, event_data)
        
        # Check if the workflow needs to be adapted based on the event
        await self._check_for_workflow_adaptation(workflow.id, event_type, event_data)
    
    async def _move_tasks_to_stage(self, workflow_id: str, target_stage_name: str, 
                                  container_id: str, event_data: Dict[str, Any]) -> None:
        """
        Move tasks related to a container to a target stage.
        
        Args:
            workflow_id: ID of the workflow
            target_stage_name: Name of the target stage
            container_id: ID of the container
            event_data: Additional data about the event
        """
        workflow = await self.get_workflow(workflow_id)
        
        # Find the target stage
        target_stage = None
        for stage in workflow.stages:
            if stage.name == target_stage_name:
                target_stage = stage
                break
        
        if not target_stage:
            logger.warning(f"Target stage {target_stage_name} not found in workflow {workflow_id}")
            return
        
        # Find tasks related to the container
        tasks_to_move = []
        source_stages = []
        
        for stage in workflow.stages:
            for task in stage.tasks:
                if container_id in task.container_events:
                    tasks_to_move.append(task)
                    source_stages.append(stage)
        
        if not tasks_to_move:
            logger.info(f"No tasks found related to container {container_id}")
            return
        
        # Create a new version of the workflow with tasks moved
        now = datetime.now()
        new_workflow_id = str(uuid.uuid4())
        
        # Create a deep copy of the stages
        new_stages = []
        for stage in workflow.stages:
            # Generate a new ID for the stage
            stage_id = f"{new_workflow_id}-stage-{stage.order}"
            
            # Create a new stage based on the original stage
            new_stage = WorkflowStage(
                id=stage_id,
                name=stage.name,
                description=stage.description,
                type=stage.type,
                order=stage.order,
                entry_criteria=stage.entry_criteria.copy(),
                exit_criteria=stage.exit_criteria.copy(),
                tasks=[],  # Start with no tasks
                metadata=stage.metadata.copy() if stage.metadata else {}
            )
            
            # Copy tasks that are not being moved
            for task in stage.tasks:
                if task not in tasks_to_move:
                    new_task = WorkflowTask(
                        id=task.id,
                        name=task.name,
                        description=task.description,
                        status=task.status,
                        stage_id=new_stage.id,
                        assignee_id=task.assignee_id,
                        created_at=task.created_at,
                        updated_at=now,
                        due_date=task.due_date,
                        estimated_hours=task.estimated_hours,
                        actual_hours=task.actual_hours,
                        priority=task.priority,
                        dependencies=task.dependencies.copy(),
                        tags=task.tags.copy(),
                        container_events=task.container_events.copy(),
                        metadata=task.metadata.copy() if task.metadata else {}
                    )
                    new_stage.tasks.append(new_task)
            
            new_stages.append(new_stage)
        
        # Find the new target stage
        new_target_stage = None
        for stage in new_stages:
            if stage.name == target_stage_name:
                new_target_stage = stage
                break
        
        # Move tasks to the target stage
        for task in tasks_to_move:
            new_task = WorkflowTask(
                id=task.id,
                name=task.name,
                description=task.description,
                status=WorkflowTaskStatus.IN_PROGRESS,  # Update status to in progress
                stage_id=new_target_stage.id,
                assignee_id=task.assignee_id,
                created_at=task.created_at,
                updated_at=now,
                due_date=task.due_date,
                estimated_hours=task.estimated_hours,
                actual_hours=task.actual_hours,
                priority=task.priority,
                dependencies=task.dependencies.copy(),
                tags=task.tags.copy(),
                container_events=task.container_events.copy(),
                metadata={
                    **(task.metadata or {}),
                    "moved_by_container_event": {
                        "timestamp": now.isoformat(),
                        "container_id": container_id,
                        "event_data": event_data
                    }
                }
            )
            new_target_stage.tasks.append(new_task)
        
        # Create the new workflow
        new_workflow = ProjectWorkflow(
            id=new_workflow_id,
            name=workflow.name,
            description=workflow.description,
            type=workflow.type,
            project_id=workflow.project_id,
            created_at=workflow.created_at,
            updated_at=now,
            stages=new_stages,
            metadata={
                **workflow.metadata,
                "adaptation_history": [
                    *workflow.metadata.get("adaptation_history", []),
                    {
                        "timestamp": now.isoformat(),
                        "reason": "container_event",
                        "event_type": "move_tasks",
                        "container_id": container_id
                    }
                ]
            },
            version=workflow.version + 1,
            is_active=True,
            created_by=workflow.created_by,
            adapted_from=workflow.id
        )
        
        # Update the original workflow to be inactive
        workflow.is_active = False
        workflow.updated_at = now
        
        # Store the new workflow
        self.workflows[new_workflow.id] = new_workflow
        
        logger.info(f"Moved {len(tasks_to_move)} tasks to stage {target_stage_name} in workflow {new_workflow.id}")
    
    async def _update_tasks_status(self, workflow_id: str, new_status: str, 
                                  container_id: str, event_data: Dict[str, Any]) -> None:
        """
        Update the status of tasks related to a container.
        
        Args:
            workflow_id: ID of the workflow
            new_status: New status for the tasks
            container_id: ID of the container
            event_data: Additional data about the event
        """
        workflow = await self.get_workflow(workflow_id)
        now = datetime.now()
        
        # Validate the new status
        try:
            task_status = WorkflowTaskStatus(new_status)
        except ValueError:
            logger.warning(f"Invalid task status: {new_status}")
            return
        
        # Find tasks related to the container
        tasks_to_update = []
        
        for stage in workflow.stages:
            for task in stage.tasks:
                if container_id in task.container_events:
                    tasks_to_update.append((stage, task))
        
        if not tasks_to_update:
            logger.info(f"No tasks found related to container {container_id}")
            return
        
        # Create a new version of the workflow with updated tasks
        new_workflow_id = str(uuid.uuid4())
        
        # Create a deep copy of the stages
        new_stages = []
        for stage in workflow.stages:
            # Generate a new ID for the stage
            stage_id = f"{new_workflow_id}-stage-{stage.order}"
            
            # Create a new stage based on the original stage
            new_stage = WorkflowStage(
                id=stage_id,
                name=stage.name,
                description=stage.description,
                type=stage.type,
                order=stage.order,
                entry_criteria=stage.entry_criteria.copy(),
                exit_criteria=stage.exit_criteria.copy(),
                tasks=[],  # Start with no tasks
                metadata=stage.metadata.copy() if stage.metadata else {}
            )
            
            # Copy tasks with updated status if needed
            for task in stage.tasks:
                new_task = WorkflowTask(
                    id=task.id,
                    name=task.name,
                    description=task.description,
                    status=task_status if (stage, task) in tasks_to_update else task.status,
                    stage_id=new_stage.id,
                    assignee_id=task.assignee_id,
                    created_at=task.created_at,
                    updated_at=now if (stage, task) in tasks_to_update else task.updated_at,
                    due_date=task.due_date,
                    estimated_hours=task.estimated_hours,
                    actual_hours=task.actual_hours,
                    priority=task.priority,
                    dependencies=task.dependencies.copy(),
                    tags=task.tags.copy(),
                    container_events=task.container_events.copy(),
                    metadata={
                        **(task.metadata or {}),
                        "status_updated_by_container_event": {
                            "timestamp": now.isoformat(),
                            "container_id": container_id,
                            "event_data": event_data
                        } if (stage, task) in tasks_to_update else task.metadata.get("status_updated_by_container_event")
                    }
                )
                new_stage.tasks.append(new_task)
            
            new_stages.append(new_stage)
        
        # Create the new workflow
        new_workflow = ProjectWorkflow(
            id=new_workflow_id,
            name=workflow.name,
            description=workflow.description,
            type=workflow.type,
            project_id=workflow.project_id,
            created_at=workflow.created_at,
            updated_at=now,
            stages=new_stages,
            metadata={
                **workflow.metadata,
                "adaptation_history": [
                    *workflow.metadata.get("adaptation_history", []),
                    {
                        "timestamp": now.isoformat(),
                        "reason": "container_event",
                        "event_type": "update_task_status",
                        "container_id": container_id
                    }
                ]
            },
            version=workflow.version + 1,
            is_active=True,
            created_by=workflow.created_by,
            adapted_from=workflow.id
        )
        
        # Update the original workflow to be inactive
        workflow.is_active = False
        workflow.updated_at = now
        
        # Store the new workflow
        self.workflows[new_workflow.id] = new_workflow
        
        logger.info(f"Updated status of {len(tasks_to_update)} tasks to {new_status} in workflow {new_workflow.id}")
    
    async def _create_task_from_event(self, workflow_id: str, container_id: str, 
                                     event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Create a new task based on a container event.
        
        Args:
            workflow_id: ID of the workflow
            container_id: ID of the container
            event_type: Type of container event
            event_data: Additional data about the event
        """
        workflow = await self.get_workflow(workflow_id)
        now = datetime.now()
        
        # Determine the appropriate stage for the new task
        target_stage = None
        if event_type == "container_build":
            # Find a development stage
            for stage in workflow.stages:
                if stage.type == WorkflowStageType.DEVELOPMENT:
                    target_stage = stage
                    break
        elif event_type == "container_test":
            # Find a testing stage
            for stage in workflow.stages:
                if stage.type == WorkflowStageType.TESTING:
                    target_stage = stage
                    break
        elif event_type == "container_deploy":
            # Find a deployment stage
            for stage in workflow.stages:
                if stage.type == WorkflowStageType.DEPLOYMENT:
                    target_stage = stage
                    break
        
        if not target_stage:
            # Default to the first stage
            target_stage = workflow.stages[0] if workflow.stages else None
        
        if not target_stage:
            logger.warning(f"No suitable stage found for task creation in workflow {workflow_id}")
            return
        
        # Create a new task
        task_name = f"Container {event_type.replace('container_', '').capitalize()}"
        if "name" in event_data:
            task_name = f"{task_name}: {event_data['name']}"
        
        task_description = f"Task created from container event: {event_type}"
        if "description" in event_data:
            task_description = event_data["description"]
        
        new_task = WorkflowTask(
            id=str(uuid.uuid4()),
            name=task_name,
            description=task_description,
            status=WorkflowTaskStatus.TODO,
            stage_id=target_stage.id,
            assignee_id=None,  # No assignee initially
            created_at=now,
            updated_at=now,
            due_date=None,
            estimated_hours=None,
            actual_hours=None,
            priority=5,  # Medium priority
            dependencies=[],
            tags=["container", event_type],
            container_events=[container_id],
            metadata={
                "created_from_container_event": {
                    "timestamp": now.isoformat(),
                    "container_id": container_id,
                    "event_type": event_type,
                    "event_data": event_data
                }
            }
        )
        
        # Create a new version of the workflow with the new task
        new_workflow_id = str(uuid.uuid4())
        
        # Create a deep copy of the stages
        new_stages = []
        for stage in workflow.stages:
            # Generate a new ID for the stage
            stage_id = f"{new_workflow_id}-stage-{stage.order}"
            
            # Create a new stage based on the original stage
            new_stage = WorkflowStage(
                id=stage_id,
                name=stage.name,
                description=stage.description,
                type=stage.type,
                order=stage.order,
                entry_criteria=stage.entry_criteria.copy(),
                exit_criteria=stage.exit_criteria.copy(),
                tasks=[],  # Start with no tasks
                metadata=stage.metadata.copy() if stage.metadata else {}
            )
            
            # Copy existing tasks
            for task in stage.tasks:
                new_task_copy = WorkflowTask(
                    id=task.id,
                    name=task.name,
                    description=task.description,
                    status=task.status,
                    stage_id=new_stage.id,
                    assignee_id=task.assignee_id,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                    due_date=task.due_date,
                    estimated_hours=task.estimated_hours,
                    actual_hours=task.actual_hours,
                    priority=task.priority,
                    dependencies=task.dependencies.copy(),
                    tags=task.tags.copy(),
                    container_events=task.container_events.copy(),
                    metadata=task.metadata.copy() if task.metadata else {}
                )
                new_stage.tasks.append(new_task_copy)
            
            # Add the new task to the target stage
            if stage.name == target_stage.name:
                new_task.stage_id = new_stage.id
                new_stage.tasks.append(new_task)
            
            new_stages.append(new_stage)
        
        # Create the new workflow
        new_workflow = ProjectWorkflow(
            id=new_workflow_id,
            name=workflow.name,
            description=workflow.description,
            type=workflow.type,
            project_id=workflow.project_id,
            created_at=workflow.created_at,
            updated_at=now,
            stages=new_stages,
            metadata={
                **workflow.metadata,
                "adaptation_history": [
                    *workflow.metadata.get("adaptation_history", []),
                    {
                        "timestamp": now.isoformat(),
                        "reason": "container_event",
                        "event_type": "create_task",
                        "container_id": container_id
                    }
                ]
            },
            version=workflow.version + 1,
            is_active=True,
            created_by=workflow.created_by,
            adapted_from=workflow.id
        )
        
        # Update the original workflow to be inactive
        workflow.is_active = False
        workflow.updated_at = now
        
        # Store the new workflow
        self.workflows[new_workflow.id] = new_workflow
        
        logger.info(f"Created new task {new_task.id} from container event in workflow {new_workflow.id}")
    
    async def _check_for_workflow_adaptation(self, workflow_id: str, event_type: str, 
                                           event_data: Dict[str, Any]) -> None:
        """
        Check if the workflow needs to be adapted based on container events.
        
        Args:
            workflow_id: ID of the workflow
            event_type: Type of container event
            event_data: Additional data about the event
        """
        workflow = await self.get_workflow(workflow_id)
        
        # Check for adaptation triggers
        adaptation_needed = False
        adaptation_reason = ""
        
        # Check for high failure rate in container builds
        if event_type == "container_build" and event_data.get("status") == "failed":
            # Count recent build failures
            failure_count = 0
            for entry in workflow.metadata.get("adaptation_history", []):
                if (entry.get("reason") == "container_event" and 
                    entry.get("event_type") == "container_build" and 
                    entry.get("event_data", {}).get("status") == "failed"):
                    failure_count += 1
            
            if failure_count >= 3:  # Three failures trigger adaptation
                adaptation_needed = True
                adaptation_reason = "high_build_failure_rate"
        
        # Check for deployment frequency
        if event_type == "container_deploy" and event_data.get("status") == "success":
            # Count recent deployments
            deploy_count = 0
            recent_time = now = datetime.now() - timedelta(days=7)  # Last 7 days
            
            for entry in workflow.metadata.get("adaptation_history", []):
                if (entry.get("reason") == "container_event" and 
                    entry.get("event_type") == "container_deploy" and 
                    entry.get("event_data", {}).get("status") == "success"):
                    entry_time = datetime.fromisoformat(entry.get("timestamp"))
                    if entry_time > recent_time:
                        deploy_count += 1
            
            if deploy_count >= 10:  # High deployment frequency
                adaptation_needed = True
                adaptation_reason = "high_deployment_frequency"
        
        # If adaptation is needed, adapt the workflow
        if adaptation_needed:
            await self._adapt_workflow_based_on_events(workflow_id, adaptation_reason, event_data)
    
    async def _adapt_workflow_based_on_events(self, workflow_id: str, reason: str, 
                                            event_data: Dict[str, Any]) -> None:
        """
        Adapt the workflow based on container events.
        
        Args:
            workflow_id: ID of the workflow
            reason: Reason for adaptation
            event_data: Additional data about the event
        """
        workflow = await self.get_workflow(workflow_id)
        now = datetime.now()
        
        # Create a new version of the workflow
        new_workflow_id = str(uuid.uuid4())
        
        # Create a deep copy of the stages
        new_stages = []
        for stage in workflow.stages:
            # Generate a new ID for the stage
            stage_id = f"{new_workflow_id}-stage-{stage.order}"
            
            # Create a new stage based on the original stage
            new_stage = WorkflowStage(
                id=stage_id,
                name=stage.name,
                description=stage.description,
                type=stage.type,
                order=stage.order,
                entry_criteria=stage.entry_criteria.copy(),
                exit_criteria=stage.exit_criteria.copy(),
                tasks=[task for task in stage.tasks],  # Copy all tasks
                metadata=stage.metadata.copy() if stage.metadata else {}
            )
            new_stages.append(new_stage)
        
        # Apply adaptations based on the reason
        if reason == "high_build_failure_rate":
            # Add a code quality stage before development
            dev_stages = [s for s in new_stages if s.type == WorkflowStageType.DEVELOPMENT]
            if dev_stages:
                first_dev_stage = min(dev_stages, key=lambda s: s.order)
                first_dev_index = new_stages.index(first_dev_stage)
                
                # Add code quality stage
                code_quality_stage = WorkflowStage(
                    id=f"{new_workflow_id}-stage-code-quality",
                    name="Code Quality Check",
                    description="Static code analysis and quality checks",
                    type=WorkflowStageType.DEVELOPMENT,
                    order=first_dev_stage.order - 0.5,  # Will be fixed later
                    entry_criteria={"planning_complete": True},
                    exit_criteria={"code_quality_check_passed": True},
                    tasks=[],
                    metadata={}
                )
                new_stages.insert(first_dev_index, code_quality_stage)
        
        elif reason == "high_deployment_frequency":
            # Optimize for continuous deployment
            # Add automated testing stage
            test_stages = [s for s in new_stages if s.type == WorkflowStageType.TESTING]
            if test_stages:
                last_test_stage = max(test_stages, key=lambda s: s.order)
                last_test_index = new_stages.index(last_test_stage)
                
                # Add automated testing stage
                auto_test_stage = WorkflowStage(
                    id=f"{new_workflow_id}-stage-auto-test",
                    name="Automated Testing",
                    description="Fully automated test suite",
                    type=WorkflowStageType.TESTING,
                    order=last_test_stage.order + 0.5,  # Will be fixed later
                    entry_criteria={"code_complete": True},
                    exit_criteria={"automated_tests_passing": True},
                    tasks=[],
                    metadata={}
                )
                new_stages.insert(last_test_index + 1, auto_test_stage)
            
            # Add continuous deployment stage
            deploy_stages = [s for s in new_stages if s.type == WorkflowStageType.DEPLOYMENT]
            if deploy_stages:
                last_deploy_stage = max(deploy_stages, key=lambda s: s.order)
                last_deploy_index = new_stages.index(last_deploy_stage)
                
                # Add continuous deployment stage
                cd_stage = WorkflowStage(
                    id=f"{new_workflow_id}-stage-cd",
                    name="Continuous Deployment",
                    description="Automated deployment pipeline",
                    type=WorkflowStageType.DEPLOYMENT,
                    order=last_deploy_stage.order + 0.5,  # Will be fixed later
                    entry_criteria={"automated_tests_passing": True},
                    exit_criteria={"continuous_deployment_enabled": True},
                    tasks=[],
                    metadata={}
                )
                new_stages.insert(last_deploy_index + 1, cd_stage)
        
        # Ensure stages have correct order
        for i, stage in enumerate(new_stages):
            stage.order = i + 1
        
        # Create the new workflow
        new_workflow = ProjectWorkflow(
            id=new_workflow_id,
            name=workflow.name,
            description=f"{workflow.description} (Adapted for {reason.replace('_', ' ')})",
            type=workflow.type,
            project_id=workflow.project_id,
            created_at=workflow.created_at,
            updated_at=now,
            stages=new_stages,
            metadata={
                **workflow.metadata,
                "adapted": True,
                "adaptation_history": [
                    *workflow.metadata.get("adaptation_history", []),
                    {
                        "timestamp": now.isoformat(),
                        "reason": reason,
                        "event_data": event_data
                    }
                ]
            },
            version=workflow.version + 1,
            is_active=True,
            created_by=workflow.created_by,
            adapted_from=workflow.id
        )
        
        # Update the original workflow to be inactive
        workflow.is_active = False
        workflow.updated_at = now
        
        # Store the new workflow
        self.workflows[new_workflow.id] = new_workflow
        
        logger.info(f"Adapted workflow {workflow_id} to {new_workflow.id} due to {reason}")
