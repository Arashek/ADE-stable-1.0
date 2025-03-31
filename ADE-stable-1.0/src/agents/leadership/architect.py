from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ..base import BaseAgent

logger = logging.getLogger(__name__)

class ArchitectAgent(BaseAgent):
    """Agent responsible for system architecture and design decisions"""
    
    def __init__(
        self,
        agent_id: str,
        provider_registry: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id,
            role="architect",
            provider_registry=provider_registry,
            capabilities=[
                "system_design",
                "architecture_planning",
                "technology_selection",
                "scalability_analysis",
                "security_design",
                "performance_optimization"
            ],
            metadata=metadata
        )
        
        # Initialize architecture-specific state
        self.designs: Dict[str, Dict[str, Any]] = {}
        self.technology_stack: Dict[str, List[str]] = {}
        self.constraints: Dict[str, List[str]] = {}
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process an architecture task
        
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
            if task_type == "create_design":
                return await self._create_design(task)
            elif task_type == "evaluate_technology":
                return await self._evaluate_technology(task)
            elif task_type == "analyze_scalability":
                return await self._analyze_scalability(task)
            elif task_type == "design_security":
                return await self._design_security(task)
            elif task_type == "optimize_performance":
                return await self._optimize_performance(task)
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
        """Collaborate with another agent on an architecture task
        
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
    
    async def _create_design(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a system design
        
        Args:
            task: Design creation task
            
        Returns:
            Design creation result
        """
        design_id = task.get("design_id")
        if not design_id:
            return {
                "success": False,
                "error": "Design ID is required"
            }
        
        # Think about system design
        thinking_result = await self.think(
            f"Create a system design for {task.get('name', 'unnamed system')} with requirements: {task.get('requirements', '')}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Create design structure
        design = {
            "id": design_id,
            "name": task.get("name", "Unnamed Design"),
            "description": task.get("description", ""),
            "requirements": task.get("requirements", ""),
            "architecture": thinking_result["final_decision"],
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "components": [],
            "interfaces": [],
            "constraints": []
        }
        
        self.designs[design_id] = design
        self.technology_stack[design_id] = []
        self.constraints[design_id] = []
        
        return {
            "success": True,
            "design": design
        }
    
    async def _evaluate_technology(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate technology options
        
        Args:
            task: Technology evaluation task
            
        Returns:
            Technology evaluation result
        """
        design_id = task.get("design_id")
        technology = task.get("technology")
        
        if not design_id or not technology:
            return {
                "success": False,
                "error": "Design ID and technology are required"
            }
        
        # Think about technology evaluation
        thinking_result = await self.think(
            f"Evaluate technology '{technology}' for design {design_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Add technology to stack
        if design_id in self.technology_stack:
            self.technology_stack[design_id].append({
                "name": technology,
                "evaluation": thinking_result["final_decision"],
                "status": "evaluated",
                "created_at": datetime.now().isoformat()
            })
            
            # Update design
            if design_id in self.designs:
                self.designs[design_id]["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "evaluation": thinking_result["final_decision"]
        }
    
    async def _analyze_scalability(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system scalability
        
        Args:
            task: Scalability analysis task
            
        Returns:
            Scalability analysis result
        """
        design_id = task.get("design_id")
        
        if not design_id:
            return {
                "success": False,
                "error": "Design ID is required"
            }
        
        if design_id not in self.designs:
            return {
                "success": False,
                "error": f"Design {design_id} not found"
            }
        
        # Think about scalability
        thinking_result = await self.think(
            f"Analyze scalability for design {design_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Update design with scalability analysis
        design = self.designs[design_id]
        design["scalability_analysis"] = thinking_result["final_decision"]
        design["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "analysis": thinking_result["final_decision"]
        }
    
    async def _design_security(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Design system security
        
        Args:
            task: Security design task
            
        Returns:
            Security design result
        """
        design_id = task.get("design_id")
        
        if not design_id:
            return {
                "success": False,
                "error": "Design ID is required"
            }
        
        if design_id not in self.designs:
            return {
                "success": False,
                "error": f"Design {design_id} not found"
            }
        
        # Think about security design
        thinking_result = await self.think(
            f"Design security for design {design_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Update design with security design
        design = self.designs[design_id]
        design["security_design"] = thinking_result["final_decision"]
        design["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "security_design": thinking_result["final_decision"]
        }
    
    async def _optimize_performance(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize system performance
        
        Args:
            task: Performance optimization task
            
        Returns:
            Performance optimization result
        """
        design_id = task.get("design_id")
        
        if not design_id:
            return {
                "success": False,
                "error": "Design ID is required"
            }
        
        if design_id not in self.designs:
            return {
                "success": False,
                "error": f"Design {design_id} not found"
            }
        
        # Think about performance optimization
        thinking_result = await self.think(
            f"Optimize performance for design {design_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Update design with performance optimization
        design = self.designs[design_id]
        design["performance_optimization"] = thinking_result["final_decision"]
        design["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "optimization": thinking_result["final_decision"]
        }
    
    def get_design(self, design_id: str) -> Optional[Dict[str, Any]]:
        """Get design details
        
        Args:
            design_id: Design ID
            
        Returns:
            Design details if found, None otherwise
        """
        return self.designs.get(design_id)
    
    def get_technology_stack(self, design_id: str) -> List[Dict[str, Any]]:
        """Get technology stack for a design
        
        Args:
            design_id: Design ID
            
        Returns:
            List of technologies in the stack
        """
        return self.technology_stack.get(design_id, [])
    
    def get_constraints(self, design_id: str) -> List[str]:
        """Get constraints for a design
        
        Args:
            design_id: Design ID
            
        Returns:
            List of constraints
        """
        return self.constraints.get(design_id, []) 