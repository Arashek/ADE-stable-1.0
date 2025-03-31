from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ..base import BaseAgent

logger = logging.getLogger(__name__)

class ProjectManagerAgent(BaseAgent):
    """Agent responsible for project management and coordination"""
    
    def __init__(
        self,
        agent_id: str,
        provider_registry: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id,
            role="project_manager",
            provider_registry=provider_registry,
            capabilities=[
                "project_planning",
                "task_decomposition",
                "resource_allocation",
                "progress_tracking",
                "risk_management",
                "team_coordination"
            ],
            metadata=metadata
        )
        
        # Initialize project-specific state
        self.active_projects: Dict[str, Dict[str, Any]] = {}
        self.team_members: Dict[str, List[str]] = {}
        self.task_queue: Dict[str, List[Dict[str, Any]]] = {}
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a project management task
        
        Args:
            task: Task description and parameters
            
        Returns:
            Task result
        """
        try:
            self.state.status = "busy"
            self.state.current_task = task.get("type", "unknown")
            self.state.last_active = datetime.now()
            
            task_type = task.get("type")
            if task_type == "create_project":
                return await self._create_project(task)
            elif task_type == "decompose_task":
                return await self._decompose_task(task)
            elif task_type == "allocate_resources":
                return await self._allocate_resources(task)
            elif task_type == "track_progress":
                return await self._track_progress(task)
            elif task_type == "manage_risk":
                return await self._manage_risk(task)
            else:
                return {
                    "success": False,
                    "error": f"Unknown task type: {task_type}"
                }
                
        except Exception as e:
            logger.error(f"Task processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            self.state.status = "idle"
            self.state.current_task = None
    
    async def collaborate(self, other_agent: BaseAgent, task: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with another agent on a project management task
        
        Args:
            other_agent: Agent to collaborate with
            task: Task to collaborate on
            
        Returns:
            Collaboration result
        """
        try:
            # Add collaboration context
            self.context_manager.add_context(
                session_id=self.session_id,
                context={
                    "collaboration": {
                        "partner_agent": other_agent.agent_id,
                        "partner_role": other_agent.role,
                        "task": task
                    }
                }
            )
            
            # Process the collaboration task
            result = await self.process_task(task)
            
            # Record collaboration in history
            self.context_manager.add_message(
                session_id=self.session_id,
                role="system",
                content=f"Collaborated with {other_agent.role} ({other_agent.agent_id}) on task: {task.get('type')}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Collaboration failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_project(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project
        
        Args:
            task: Project creation task
            
        Returns:
            Project creation result
        """
        project_id = task.get("project_id")
        if not project_id:
            return {
                "success": False,
                "error": "Project ID is required"
            }
        
        # Think about project requirements
        thinking_result = await self.think(
            f"Create a project plan for {task.get('name', 'unnamed project')} with requirements: {task.get('requirements', '')}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Create project structure
        project = {
            "id": project_id,
            "name": task.get("name", "Unnamed Project"),
            "description": task.get("description", ""),
            "requirements": task.get("requirements", ""),
            "plan": thinking_result["final_decision"],
            "status": "planning",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "team": [],
            "tasks": [],
            "risks": []
        }
        
        self.active_projects[project_id] = project
        self.team_members[project_id] = []
        self.task_queue[project_id] = []
        
        return {
            "success": True,
            "project": project
        }
    
    async def _decompose_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Decompose a task into subtasks
        
        Args:
            task: Task decomposition task
            
        Returns:
            Task decomposition result
        """
        project_id = task.get("project_id")
        parent_task = task.get("task")
        
        if not project_id or not parent_task:
            return {
                "success": False,
                "error": "Project ID and parent task are required"
            }
        
        # Think about task decomposition
        thinking_result = await self.think(
            f"Decompose task '{parent_task}' into subtasks for project {project_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Create subtasks
        subtasks = thinking_result["final_decision"].get("subtasks", [])
        
        # Add subtasks to project
        if project_id in self.active_projects:
            self.active_projects[project_id]["tasks"].extend(subtasks)
            self.task_queue[project_id].extend(subtasks)
            self.active_projects[project_id]["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "subtasks": subtasks
        }
    
    async def _allocate_resources(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Allocate resources to tasks
        
        Args:
            task: Resource allocation task
            
        Returns:
            Resource allocation result
        """
        project_id = task.get("project_id")
        task_id = task.get("task_id")
        resources = task.get("resources", [])
        
        if not project_id or not task_id or not resources:
            return {
                "success": False,
                "error": "Project ID, task ID, and resources are required"
            }
        
        # Think about resource allocation
        thinking_result = await self.think(
            f"Allocate resources {resources} to task {task_id} in project {project_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Update task with allocated resources
        if project_id in self.active_projects:
            for t in self.active_projects[project_id]["tasks"]:
                if t["id"] == task_id:
                    t["resources"] = resources
                    t["status"] = "allocated"
                    break
            self.active_projects[project_id]["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "allocation": thinking_result["final_decision"]
        }
    
    async def _track_progress(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Track project progress
        
        Args:
            task: Progress tracking task
            
        Returns:
            Progress tracking result
        """
        project_id = task.get("project_id")
        
        if not project_id:
            return {
                "success": False,
                "error": "Project ID is required"
            }
        
        if project_id not in self.active_projects:
            return {
                "success": False,
                "error": f"Project {project_id} not found"
            }
        
        project = self.active_projects[project_id]
        
        # Calculate progress metrics
        total_tasks = len(project["tasks"])
        completed_tasks = sum(1 for t in project["tasks"] if t["status"] == "completed")
        in_progress_tasks = sum(1 for t in project["tasks"] if t["status"] == "in_progress")
        
        progress = {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completion_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "status": project["status"],
            "updated_at": project["updated_at"]
        }
        
        return {
            "success": True,
            "progress": progress
        }
    
    async def _manage_risk(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Manage project risks
        
        Args:
            task: Risk management task
            
        Returns:
            Risk management result
        """
        project_id = task.get("project_id")
        risk = task.get("risk")
        
        if not project_id or not risk:
            return {
                "success": False,
                "error": "Project ID and risk description are required"
            }
        
        # Think about risk management
        thinking_result = await self.think(
            f"Manage risk '{risk}' for project {project_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Add risk to project
        if project_id in self.active_projects:
            self.active_projects[project_id]["risks"].append({
                "description": risk,
                "mitigation": thinking_result["final_decision"].get("mitigation", ""),
                "status": "identified",
                "created_at": datetime.now().isoformat()
            })
            self.active_projects[project_id]["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "risk_management": thinking_result["final_decision"]
        }
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project details
        
        Args:
            project_id: Project ID
            
        Returns:
            Project details if found, None otherwise
        """
        return self.active_projects.get(project_id)
    
    def get_team_members(self, project_id: str) -> List[str]:
        """Get team members for a project
        
        Args:
            project_id: Project ID
            
        Returns:
            List of team member IDs
        """
        return self.team_members.get(project_id, [])
    
    def get_task_queue(self, project_id: str) -> List[Dict[str, Any]]:
        """Get task queue for a project
        
        Args:
            project_id: Project ID
            
        Returns:
            List of tasks in the queue
        """
        return self.task_queue.get(project_id, []) 