from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ..base import BaseAgent

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    """Agent responsible for task planning and scheduling"""
    
    def __init__(
        self,
        agent_id: str,
        provider_registry: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id,
            role="planner",
            provider_registry=provider_registry,
            capabilities=[
                "task_planning",
                "schedule_management",
                "dependency_analysis",
                "resource_estimation",
                "timeline_creation",
                "risk_assessment"
            ],
            metadata=metadata
        )
        
        # Initialize planning-specific state
        self.plans: Dict[str, Dict[str, Any]] = {}
        self.schedules: Dict[str, Dict[str, Any]] = {}
        self.dependencies: Dict[str, Dict[str, List[str]]] = {}
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a planning task
        
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
            if task_type == "create_plan":
                return await self._create_plan(task)
            elif task_type == "create_schedule":
                return await self._create_schedule(task)
            elif task_type == "analyze_dependencies":
                return await self._analyze_dependencies(task)
            elif task_type == "estimate_resources":
                return await self._estimate_resources(task)
            elif task_type == "assess_risks":
                return await self._assess_risks(task)
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
        """Collaborate with another agent on a planning task
        
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
    
    async def _create_plan(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task plan
        
        Args:
            task: Plan creation task
            
        Returns:
            Plan creation result
        """
        plan_id = task.get("plan_id")
        if not plan_id:
            return {
                "success": False,
                "error": "Plan ID is required"
            }
        
        # Think about task planning
        thinking_result = await self.think(
            f"Create a plan for {task.get('name', 'unnamed task')} with requirements: {task.get('requirements', '')}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Create plan structure
        plan = {
            "id": plan_id,
            "name": task.get("name", "Unnamed Plan"),
            "description": task.get("description", ""),
            "requirements": task.get("requirements", ""),
            "tasks": thinking_result["final_decision"].get("tasks", []),
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "dependencies": [],
            "resources": [],
            "risks": []
        }
        
        self.plans[plan_id] = plan
        self.dependencies[plan_id] = {}
        
        return {
            "success": True,
            "plan": plan
        }
    
    async def _create_schedule(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task schedule
        
        Args:
            task: Schedule creation task
            
        Returns:
            Schedule creation result
        """
        plan_id = task.get("plan_id")
        if not plan_id or plan_id not in self.plans:
            return {
                "success": False,
                "error": "Valid plan ID is required"
            }
        
        # Think about scheduling
        thinking_result = await self.think(
            f"Create a schedule for plan {plan_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Create schedule structure
        schedule = {
            "id": f"schedule_{plan_id}",
            "plan_id": plan_id,
            "timeline": thinking_result["final_decision"].get("timeline", []),
            "milestones": thinking_result["final_decision"].get("milestones", []),
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resource_allocations": [],
            "dependencies": self.dependencies.get(plan_id, {})
        }
        
        self.schedules[schedule["id"]] = schedule
        
        # Update plan with schedule reference
        self.plans[plan_id]["schedule_id"] = schedule["id"]
        self.plans[plan_id]["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "schedule": schedule
        }
    
    async def _analyze_dependencies(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task dependencies
        
        Args:
            task: Dependency analysis task
            
        Returns:
            Dependency analysis result
        """
        plan_id = task.get("plan_id")
        task_id = task.get("task_id")
        
        if not plan_id or not task_id:
            return {
                "success": False,
                "error": "Plan ID and task ID are required"
            }
        
        if plan_id not in self.plans:
            return {
                "success": False,
                "error": f"Plan {plan_id} not found"
            }
        
        # Think about dependencies
        thinking_result = await self.think(
            f"Analyze dependencies for task {task_id} in plan {plan_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Update dependencies
        if plan_id in self.dependencies:
            self.dependencies[plan_id][task_id] = thinking_result["final_decision"].get("dependencies", [])
            
            # Update plan
            self.plans[plan_id]["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "dependencies": thinking_result["final_decision"]
        }
    
    async def _estimate_resources(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate task resources
        
        Args:
            task: Resource estimation task
            
        Returns:
            Resource estimation result
        """
        plan_id = task.get("plan_id")
        task_id = task.get("task_id")
        
        if not plan_id or not task_id:
            return {
                "success": False,
                "error": "Plan ID and task ID are required"
            }
        
        if plan_id not in self.plans:
            return {
                "success": False,
                "error": f"Plan {plan_id} not found"
            }
        
        # Think about resource estimation
        thinking_result = await self.think(
            f"Estimate resources for task {task_id} in plan {plan_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Update plan with resource estimates
        plan = self.plans[plan_id]
        for task in plan["tasks"]:
            if task["id"] == task_id:
                task["resource_estimate"] = thinking_result["final_decision"]
                break
        plan["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "resource_estimate": thinking_result["final_decision"]
        }
    
    async def _assess_risks(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Assess task risks
        
        Args:
            task: Risk assessment task
            
        Returns:
            Risk assessment result
        """
        plan_id = task.get("plan_id")
        
        if not plan_id:
            return {
                "success": False,
                "error": "Plan ID is required"
            }
        
        if plan_id not in self.plans:
            return {
                "success": False,
                "error": f"Plan {plan_id} not found"
            }
        
        # Think about risk assessment
        thinking_result = await self.think(
            f"Assess risks for plan {plan_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Update plan with risk assessment
        plan = self.plans[plan_id]
        plan["risks"] = thinking_result["final_decision"].get("risks", [])
        plan["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "risk_assessment": thinking_result["final_decision"]
        }
    
    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get plan details
        
        Args:
            plan_id: Plan ID
            
        Returns:
            Plan details if found, None otherwise
        """
        return self.plans.get(plan_id)
    
    def get_schedule(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Get schedule details
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            Schedule details if found, None otherwise
        """
        return self.schedules.get(schedule_id)
    
    def get_dependencies(self, plan_id: str) -> Dict[str, List[str]]:
        """Get dependencies for a plan
        
        Args:
            plan_id: Plan ID
            
        Returns:
            Dictionary of task dependencies
        """
        return self.dependencies.get(plan_id, {}) 