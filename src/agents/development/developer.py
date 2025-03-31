from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ..base import BaseAgent
from ..components.solution_generator import MultiSolutionGenerator
from ..components.context_aware_fix import ContextAwareFixSystem
from ..components.safe_code_modifier import SafeCodeModifier
from ..components.version_control import VersionControlManager

logger = logging.getLogger(__name__)

class DeveloperAgent(BaseAgent):
    """Agent responsible for code implementation and development"""
    
    def __init__(
        self,
        agent_id: str,
        provider_registry: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id,
            role="developer",
            provider_registry=provider_registry,
            capabilities=[
                "code_implementation",
                "code_review",
                "bug_fixing",
                "refactoring",
                "testing",
                "documentation"
            ],
            metadata=metadata
        )
        
        # Initialize development-specific state
        self.implementations: Dict[str, Dict[str, Any]] = {}
        self.code_reviews: Dict[str, Dict[str, Any]] = {}
        self.bug_fixes: Dict[str, Dict[str, Any]] = {}
        
        # Initialize new components
        self.solution_generator = MultiSolutionGenerator(metadata.get("project_dir", ""))
        self.context_aware_fix = ContextAwareFixSystem(metadata.get("project_dir", ""))
        self.safe_code_modifier = SafeCodeModifier(metadata.get("project_dir", ""))
        self.version_control = VersionControlManager(metadata.get("project_dir", ""))
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a development task
        
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
            if task_type == "implement_feature":
                return await self._implement_feature(task)
            elif task_type == "review_code":
                return await self._review_code(task)
            elif task_type == "fix_bug":
                return await self.fix_bug(task)
            elif task_type == "refactor_code":
                return await self.refactor_code(task)
            elif task_type == "write_tests":
                return await self._write_tests(task)
            elif task_type == "write_documentation":
                return await self._write_documentation(task)
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
        """Collaborate with another agent on a development task
        
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
    
    async def _implement_feature(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a feature
        
        Args:
            task: Feature implementation task
            
        Returns:
            Implementation result
        """
        implementation_id = task.get("implementation_id")
        if not implementation_id:
            return {
                "success": False,
                "error": "Implementation ID is required"
            }
        
        # Think about feature implementation
        thinking_result = await self.think(
            f"Implement feature '{task.get('name', 'unnamed feature')}' with requirements: {task.get('requirements', '')}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Generate code for the feature
        code_result = await self.generate_code(
            requirements=task.get("requirements", ""),
            language=task.get("language", "python"),
            framework=task.get("framework")
        )
        
        if not code_result["success"]:
            return code_result
        
        # Create implementation structure
        implementation = {
            "id": implementation_id,
            "name": task.get("name", "Unnamed Implementation"),
            "description": task.get("description", ""),
            "requirements": task.get("requirements", ""),
            "code": code_result["code"],
            "documentation": code_result["documentation"],
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "tests": [],
            "reviews": []
        }
        
        self.implementations[implementation_id] = implementation
        
        return {
            "success": True,
            "implementation": implementation
        }
    
    async def _review_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Review code implementation
        
        Args:
            task: Code review task
            
        Returns:
            Review result
        """
        implementation_id = task.get("implementation_id")
        if not implementation_id or implementation_id not in self.implementations:
            return {
                "success": False,
                "error": "Valid implementation ID is required"
            }
        
        # Think about code review
        thinking_result = await self.think(
            f"Review implementation {implementation_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Create review structure
        review = {
            "id": f"review_{implementation_id}",
            "implementation_id": implementation_id,
            "issues": thinking_result["final_decision"].get("issues", []),
            "suggestions": thinking_result["final_decision"].get("suggestions", []),
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.code_reviews[review["id"]] = review
        
        # Update implementation with review reference
        self.implementations[implementation_id]["reviews"].append(review["id"])
        self.implementations[implementation_id]["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "review": review
        }
    
    async def fix_bug(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Fix a bug using the new components
        
        Args:
            task: Bug fix task containing error details and file path
            
        Returns:
            Fix result
        """
        error = task.get("error")
        file_path = task.get("file_path")
        
        if not error or not file_path:
            return {
                "success": False,
                "error": "Error description and file path are required"
            }
            
        try:
            # Generate multiple solution variants
            solution_variants = await self.solution_generator.generate_solutions(error, file_path)
            
            if not solution_variants:
                return {
                    "success": False,
                    "error": "No valid solutions generated"
                }
                
            # Get code context
            context = await self.context_aware_fix.get_context(file_path)
            
            # Score and rank solutions
            scored_solutions = await self.solution_generator._score_solutions(solution_variants, context)
            
            # Apply the best solution
            best_solution = scored_solutions[0]
            success = await self.safe_code_modifier.apply_changes([best_solution.fix])
            
            if not success:
                return {
                    "success": False,
                    "error": "Failed to apply fix"
                }
                
            # Create fix record
            fix_record = {
                "id": f"fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "error": error,
                "file_path": file_path,
                "solution": best_solution.fix,
                "scores": {
                    "effectiveness": best_solution.effectiveness_score,
                    "impact": best_solution.impact_score,
                    "complexity": best_solution.complexity_score,
                    "maintainability": best_solution.maintainability_score
                },
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            self.bug_fixes[fix_record["id"]] = fix_record
            
            return {
                "success": True,
                "fix": fix_record
            }
            
        except Exception as e:
            logger.error(f"Error fixing bug: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def refactor_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Refactor code using the new components
        
        Args:
            task: Refactoring task containing file path and refactoring goals
            
        Returns:
            Refactoring result
        """
        file_path = task.get("file_path")
        goals = task.get("goals", [])
        
        if not file_path:
            return {
                "success": False,
                "error": "File path is required"
            }
            
        try:
            # Get code context
            context = await self.context_aware_fix.get_context(file_path)
            
            # Generate refactoring solutions
            refactoring_solutions = []
            for goal in goals:
                solutions = await self.solution_generator.generate_solutions(
                    f"Refactor code to improve {goal}",
                    file_path
                )
                refactoring_solutions.extend(solutions)
                
            if not refactoring_solutions:
                return {
                    "success": False,
                    "error": "No valid refactoring solutions generated"
                }
                
            # Score and rank solutions
            scored_solutions = await self.solution_generator._score_solutions(
                refactoring_solutions,
                context
            )
            
            # Apply the best solutions
            applied_solutions = []
            for solution in scored_solutions[:3]:  # Apply top 3 solutions
                success = await self.safe_code_modifier.apply_changes([solution.fix])
                if success:
                    applied_solutions.append(solution)
                    
            if not applied_solutions:
                return {
                    "success": False,
                    "error": "Failed to apply any refactoring solutions"
                }
                
            # Create refactoring record
            refactoring_record = {
                "id": f"refactor_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "file_path": file_path,
                "goals": goals,
                "applied_solutions": [
                    {
                        "fix": solution.fix,
                        "scores": {
                            "effectiveness": solution.effectiveness_score,
                            "impact": solution.impact_score,
                            "complexity": solution.complexity_score,
                            "maintainability": solution.maintainability_score
                        }
                    }
                    for solution in applied_solutions
                ],
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            self.implementations[refactoring_record["id"]] = refactoring_record
            
            return {
                "success": True,
                "refactoring": refactoring_record
            }
            
        except Exception as e:
            logger.error(f"Error refactoring code: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _write_tests(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Write tests for implementation
        
        Args:
            task: Test writing task
            
        Returns:
            Test writing result
        """
        implementation_id = task.get("implementation_id")
        if not implementation_id or implementation_id not in self.implementations:
            return {
                "success": False,
                "error": "Valid implementation ID is required"
            }
        
        # Think about test cases
        thinking_result = await self.think(
            f"Write tests for implementation {implementation_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Generate test code
        test_result = await self.generate_code(
            requirements=f"Write tests for implementation {implementation_id}",
            language=self.implementations[implementation_id].get("language", "python"),
            framework=self.implementations[implementation_id].get("framework")
        )
        
        if not test_result["success"]:
            return test_result
        
        # Update implementation with tests
        implementation = self.implementations[implementation_id]
        implementation["tests"] = test_result["code"]
        implementation["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "tests": test_result["code"]
        }
    
    async def _write_documentation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Write documentation for implementation
        
        Args:
            task: Documentation writing task
            
        Returns:
            Documentation writing result
        """
        implementation_id = task.get("implementation_id")
        if not implementation_id or implementation_id not in self.implementations:
            return {
                "success": False,
                "error": "Valid implementation ID is required"
            }
        
        # Think about documentation
        thinking_result = await self.think(
            f"Write documentation for implementation {implementation_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Generate documentation
        doc_result = await self.generate_code(
            requirements=f"Write documentation for implementation {implementation_id}",
            language="markdown",
            framework=None
        )
        
        if not doc_result["success"]:
            return doc_result
        
        # Update implementation with documentation
        implementation = self.implementations[implementation_id]
        implementation["documentation"] = doc_result["code"]
        implementation["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "documentation": doc_result["code"]
        }
    
    def get_implementation(self, implementation_id: str) -> Optional[Dict[str, Any]]:
        """Get implementation details
        
        Args:
            implementation_id: Implementation ID
            
        Returns:
            Implementation details if found, None otherwise
        """
        return self.implementations.get(implementation_id)
    
    def get_code_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get code review details
        
        Args:
            review_id: Review ID
            
        Returns:
            Review details if found, None otherwise
        """
        return self.code_reviews.get(review_id)
    
    def get_bug_fix(self, fix_id: str) -> Optional[Dict[str, Any]]:
        """Get bug fix details
        
        Args:
            fix_id: Bug fix ID
            
        Returns:
            Bug fix details if found, None otherwise
        """
        return self.bug_fixes.get(fix_id) 