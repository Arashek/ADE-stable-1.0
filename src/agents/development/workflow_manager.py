from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ..base import BaseAgent
from ...services.git_service import GitService
from ...services.code_review_service import CodeReviewService
from ...services.cicd_service import CICDService
from ...services.project_management_service import ProjectManagementService
from ...core.config import settings

logger = logging.getLogger(__name__)

class WorkflowManagerAgent(BaseAgent):
    """Agent responsible for managing development workflow operations"""
    
    def __init__(
        self,
        agent_id: str,
        provider_registry: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id,
            role="workflow_manager",
            provider_registry=provider_registry,
            capabilities=[
                "git_operations",
                "code_review",
                "cicd_pipeline",
                "project_management",
                "workflow_coordination",
                "status_monitoring"
            ],
            metadata=metadata
        )
        
        # Initialize services
        self.git_service = GitService(settings.GIT_REPO_PATH)
        self.code_review_service = CodeReviewService(settings.STORAGE_PATH)
        self.cicd_service = CICDService(settings.PIPELINE_CONFIG_PATH)
        self.project_service = ProjectManagementService(settings.STORAGE_PATH)
        
        # Initialize workflow state
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_status: Dict[str, Dict[str, Any]] = {}
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a development workflow task"""
        try:
            task_type = task.get("type")
            if task_type == "git_operation":
                return await self._handle_git_operation(task)
            elif task_type == "code_review":
                return await self._handle_code_review(task)
            elif task_type == "cicd_pipeline":
                return await self._handle_cicd_pipeline(task)
            elif task_type == "project_management":
                return await self._handle_project_management(task)
            else:
                return {"status": "error", "message": f"Unknown task type: {task_type}"}
        except Exception as e:
            logger.error(f"Error processing workflow task: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def _handle_git_operation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Git-related operations"""
        operation = task.get("operation")
        if operation == "clone":
            return self.git_service.clone_repository(
                url=task["url"],
                branch=task.get("branch")
            )
        elif operation == "commit":
            return self.git_service.commit_changes(
                message=task["message"],
                files=task.get("files")
            )
        elif operation == "push":
            return self.git_service.push_changes(
                remote=task.get("remote", "origin"),
                branch=task.get("branch", "main")
            )
        elif operation == "pull":
            return self.git_service.pull_changes(
                remote=task.get("remote", "origin"),
                branch=task.get("branch", "main")
            )
        elif operation == "branch":
            return self.git_service.create_branch(
                branch_name=task["branch_name"],
                source=task.get("source", "main")
            )
        else:
            return {"status": "error", "message": f"Unknown Git operation: {operation}"}
            
    async def _handle_code_review(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code review operations"""
        operation = task.get("operation")
        if operation == "create_pr":
            return self.code_review_service.create_pull_request(
                title=task["title"],
                description=task["description"],
                source_branch=task["source_branch"],
                target_branch=task["target_branch"],
                author=task["author"]
            )
        elif operation == "add_comment":
            return self.code_review_service.add_review_comment(
                pr_id=task["pr_id"],
                file_path=task["file_path"],
                line_number=task["line_number"],
                comment=task["comment"],
                reviewer=task["reviewer"]
            )
        elif operation == "update_status":
            return self.code_review_service.update_pr_status(
                pr_id=task["pr_id"],
                status=task["status"]
            )
        else:
            return {"status": "error", "message": f"Unknown code review operation: {operation}"}
            
    async def _handle_cicd_pipeline(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CI/CD pipeline operations"""
        operation = task.get("operation")
        if operation == "create_config":
            return self.cicd_service.create_pipeline_config(
                project_name=task["project_name"],
                config=task["config"]
            )
        elif operation == "execute":
            return self.cicd_service.execute_pipeline(
                project_name=task["project_name"],
                environment=task["environment"]
            )
        elif operation == "get_status":
            return self.cicd_service.get_pipeline_status(
                project_name=task["project_name"]
            )
        elif operation == "update_environment":
            return self.cicd_service.update_environment_config(
                project_name=task["project_name"],
                environment=task["environment"],
                config=task["config"]
            )
        else:
            return {"status": "error", "message": f"Unknown CI/CD operation: {operation}"}
            
    async def _handle_project_management(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project management operations"""
        operation = task.get("operation")
        if operation == "create_project":
            return self.project_service.create_project(
                name=task["name"],
                description=task["description"],
                owner=task["owner"]
            )
        elif operation == "create_task":
            return self.project_service.create_task(
                project_id=task["project_id"],
                title=task["title"],
                description=task["description"],
                assignee=task["assignee"],
                estimated_hours=task["estimated_hours"]
            )
        elif operation == "create_sprint":
            return self.project_service.create_sprint(
                project_id=task["project_id"],
                name=task["name"],
                start_date=task["start_date"],
                end_date=task["end_date"]
            )
        elif operation == "update_task_status":
            return self.project_service.update_task_status(
                project_id=task["project_id"],
                task_id=task["task_id"],
                status=task["status"]
            )
        elif operation == "log_time":
            return self.project_service.log_time(
                project_id=task["project_id"],
                task_id=task["task_id"],
                hours=task["hours"],
                description=task["description"],
                user=task["user"]
            )
        else:
            return {"status": "error", "message": f"Unknown project management operation: {operation}"}
            
    async def collaborate(self, other_agent: 'BaseAgent', task: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with other agents on workflow tasks"""
        try:
            # Get agent capabilities
            agent_capabilities = other_agent.capabilities
            
            # Determine collaboration strategy based on capabilities
            if "code_analysis" in agent_capabilities:
                # Collaborate on code review tasks
                return await self._collaborate_on_code_review(other_agent, task)
            elif "resource_optimization" in agent_capabilities:
                # Collaborate on CI/CD pipeline tasks
                return await self._collaborate_on_cicd(other_agent, task)
            elif "task_planning" in agent_capabilities:
                # Collaborate on project management tasks
                return await self._collaborate_on_project_management(other_agent, task)
            else:
                return {"status": "error", "message": "No compatible collaboration capabilities found"}
        except Exception as e:
            logger.error(f"Error in agent collaboration: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def _collaborate_on_code_review(self, other_agent: 'BaseAgent', task: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with code analysis agent on code review"""
        # Get code analysis from other agent
        analysis_result = await other_agent.process_task({
            "type": "code_analysis",
            "code": task.get("code"),
            "context": task.get("context")
        })
        
        # Use analysis result in code review
        if analysis_result["status"] == "success":
            return await self._handle_code_review({
                "operation": "add_comment",
                "pr_id": task["pr_id"],
                "file_path": task["file_path"],
                "line_number": task["line_number"],
                "comment": analysis_result["analysis"],
                "reviewer": self.agent_id
            })
        return analysis_result
        
    async def _collaborate_on_cicd(self, other_agent: 'BaseAgent', task: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with resource optimization agent on CI/CD"""
        # Get resource optimization suggestions
        optimization_result = await other_agent.process_task({
            "type": "resource_optimization",
            "pipeline_config": task.get("config"),
            "context": task.get("context")
        })
        
        # Apply optimizations to pipeline
        if optimization_result["status"] == "success":
            return await self._handle_cicd_pipeline({
                "operation": "update_environment",
                "project_name": task["project_name"],
                "environment": task["environment"],
                "config": optimization_result["optimized_config"]
            })
        return optimization_result
        
    async def _collaborate_on_project_management(self, other_agent: 'BaseAgent', task: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with task planning agent on project management"""
        # Get task planning suggestions
        planning_result = await other_agent.process_task({
            "type": "task_planning",
            "project_id": task.get("project_id"),
            "context": task.get("context")
        })
        
        # Apply planning suggestions
        if planning_result["status"] == "success":
            return await self._handle_project_management({
                "operation": "create_task",
                "project_id": task["project_id"],
                "title": planning_result["task_title"],
                "description": planning_result["task_description"],
                "assignee": planning_result["assignee"],
                "estimated_hours": planning_result["estimated_hours"]
            })
        return planning_result 