from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ..base import BaseAgent

logger = logging.getLogger(__name__)

class ReviewerAgent(BaseAgent):
    """Agent responsible for code review and quality assurance"""
    
    def __init__(
        self,
        agent_id: str,
        provider_registry: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id,
            role="reviewer",
            provider_registry=provider_registry,
            capabilities=[
                "code_review",
                "quality_assessment",
                "best_practices",
                "security_review",
                "performance_review",
                "documentation_review"
            ],
            metadata=metadata
        )
        
        # Initialize review-specific state
        self.reviews: Dict[str, Dict[str, Any]] = {}
        self.quality_metrics: Dict[str, Dict[str, Any]] = {}
        self.review_history: Dict[str, List[Dict[str, Any]]] = {}
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a review task
        
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
            if task_type == "review_code":
                return await self._review_code(task)
            elif task_type == "assess_quality":
                return await self._assess_quality(task)
            elif task_type == "check_best_practices":
                return await self._check_best_practices(task)
            elif task_type == "review_security":
                return await self._review_security(task)
            elif task_type == "review_performance":
                return await self._review_performance(task)
            elif task_type == "review_documentation":
                return await self._review_documentation(task)
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
        """Collaborate with another agent on a review task
        
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
    
    async def _review_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Review code implementation
        
        Args:
            task: Code review task
            
        Returns:
            Review result
        """
        review_id = task.get("review_id")
        code = task.get("code")
        language = task.get("language", "python")
        
        if not review_id or not code:
            return {
                "success": False,
                "error": "Review ID and code are required"
            }
        
        # Think about code review
        thinking_result = await self.think(
            f"Review code in {language} with ID {review_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Create review structure
        review = {
            "id": review_id,
            "code": code,
            "language": language,
            "issues": thinking_result["final_decision"].get("issues", []),
            "suggestions": thinking_result["final_decision"].get("suggestions", []),
            "complexity": thinking_result["final_decision"].get("complexity", {}),
            "maintainability": thinking_result["final_decision"].get("maintainability", {}),
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.reviews[review_id] = review
        
        # Add to review history
        if review_id not in self.review_history:
            self.review_history[review_id] = []
        self.review_history[review_id].append(review)
        
        return {
            "success": True,
            "review": review
        }
    
    async def _assess_quality(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Assess code quality
        
        Args:
            task: Quality assessment task
            
        Returns:
            Quality assessment result
        """
        review_id = task.get("review_id")
        if not review_id or review_id not in self.reviews:
            return {
                "success": False,
                "error": "Valid review ID is required"
            }
        
        # Think about quality assessment
        thinking_result = await self.think(
            f"Assess quality for review {review_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Create quality metrics
        metrics = {
            "id": f"metrics_{review_id}",
            "review_id": review_id,
            "code_quality": thinking_result["final_decision"].get("code_quality", {}),
            "test_coverage": thinking_result["final_decision"].get("test_coverage", {}),
            "documentation": thinking_result["final_decision"].get("documentation", {}),
            "maintainability": thinking_result["final_decision"].get("maintainability", {}),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.quality_metrics[metrics["id"]] = metrics
        
        # Update review with metrics
        self.reviews[review_id]["quality_metrics"] = metrics
        self.reviews[review_id]["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "quality_metrics": metrics
        }
    
    async def _check_best_practices(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Check code against best practices
        
        Args:
            task: Best practices check task
            
        Returns:
            Best practices check result
        """
        review_id = task.get("review_id")
        if not review_id or review_id not in self.reviews:
            return {
                "success": False,
                "error": "Valid review ID is required"
            }
        
        # Think about best practices
        thinking_result = await self.think(
            f"Check best practices for review {review_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Update review with best practices check
        review = self.reviews[review_id]
        review["best_practices"] = {
            "violations": thinking_result["final_decision"].get("violations", []),
            "recommendations": thinking_result["final_decision"].get("recommendations", []),
            "score": thinking_result["final_decision"].get("score", 0),
            "updated_at": datetime.now().isoformat()
        }
        review["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "best_practices": review["best_practices"]
        }
    
    async def _review_security(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Review code security
        
        Args:
            task: Security review task
            
        Returns:
            Security review result
        """
        review_id = task.get("review_id")
        if not review_id or review_id not in self.reviews:
            return {
                "success": False,
                "error": "Valid review ID is required"
            }
        
        # Think about security review
        thinking_result = await self.think(
            f"Review security for review {review_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Update review with security assessment
        review = self.reviews[review_id]
        review["security_review"] = {
            "vulnerabilities": thinking_result["final_decision"].get("vulnerabilities", []),
            "security_issues": thinking_result["final_decision"].get("security_issues", []),
            "recommendations": thinking_result["final_decision"].get("recommendations", []),
            "risk_level": thinking_result["final_decision"].get("risk_level", "medium"),
            "updated_at": datetime.now().isoformat()
        }
        review["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "security_review": review["security_review"]
        }
    
    async def _review_performance(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Review code performance
        
        Args:
            task: Performance review task
            
        Returns:
            Performance review result
        """
        review_id = task.get("review_id")
        if not review_id or review_id not in self.reviews:
            return {
                "success": False,
                "error": "Valid review ID is required"
            }
        
        # Think about performance review
        thinking_result = await self.think(
            f"Review performance for review {review_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Update review with performance assessment
        review = self.reviews[review_id]
        review["performance_review"] = {
            "bottlenecks": thinking_result["final_decision"].get("bottlenecks", []),
            "optimization_opportunities": thinking_result["final_decision"].get("optimization_opportunities", []),
            "benchmarks": thinking_result["final_decision"].get("benchmarks", {}),
            "recommendations": thinking_result["final_decision"].get("recommendations", []),
            "updated_at": datetime.now().isoformat()
        }
        review["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "performance_review": review["performance_review"]
        }
    
    async def _review_documentation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Review code documentation
        
        Args:
            task: Documentation review task
            
        Returns:
            Documentation review result
        """
        review_id = task.get("review_id")
        if not review_id or review_id not in self.reviews:
            return {
                "success": False,
                "error": "Valid review ID is required"
            }
        
        # Think about documentation review
        thinking_result = await self.think(
            f"Review documentation for review {review_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Update review with documentation assessment
        review = self.reviews[review_id]
        review["documentation_review"] = {
            "completeness": thinking_result["final_decision"].get("completeness", {}),
            "clarity": thinking_result["final_decision"].get("clarity", {}),
            "missing_docs": thinking_result["final_decision"].get("missing_docs", []),
            "improvements": thinking_result["final_decision"].get("improvements", []),
            "updated_at": datetime.now().isoformat()
        }
        review["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "documentation_review": review["documentation_review"]
        }
    
    def get_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get review details
        
        Args:
            review_id: Review ID
            
        Returns:
            Review details if found, None otherwise
        """
        return self.reviews.get(review_id)
    
    def get_quality_metrics(self, metrics_id: str) -> Optional[Dict[str, Any]]:
        """Get quality metrics details
        
        Args:
            metrics_id: Metrics ID
            
        Returns:
            Quality metrics details if found, None otherwise
        """
        return self.quality_metrics.get(metrics_id)
    
    def get_review_history(self, review_id: str) -> List[Dict[str, Any]]:
        """Get review history
        
        Args:
            review_id: Review ID
            
        Returns:
            List of review history entries
        """
        return self.review_history.get(review_id, []) 