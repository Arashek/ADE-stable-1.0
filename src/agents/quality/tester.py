from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ..base import BaseAgent

logger = logging.getLogger(__name__)

class TesterAgent(BaseAgent):
    """Agent responsible for testing and quality assurance"""
    
    def __init__(
        self,
        agent_id: str,
        provider_registry: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id,
            role="tester",
            provider_registry=provider_registry,
            capabilities=[
                "test_planning",
                "test_execution",
                "bug_reporting",
                "test_automation",
                "performance_testing",
                "security_testing"
            ],
            metadata=metadata
        )
        
        # Initialize testing-specific state
        self.test_plans: Dict[str, Dict[str, Any]] = {}
        self.test_results: Dict[str, Dict[str, Any]] = {}
        self.bug_reports: Dict[str, Dict[str, Any]] = {}
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a testing task
        
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
            if task_type == "create_test_plan":
                return await self._create_test_plan(task)
            elif task_type == "execute_tests":
                return await self._execute_tests(task)
            elif task_type == "report_bug":
                return await self._report_bug(task)
            elif task_type == "automate_tests":
                return await self._automate_tests(task)
            elif task_type == "test_performance":
                return await self._test_performance(task)
            elif task_type == "test_security":
                return await self._test_security(task)
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
        """Collaborate with another agent on a testing task
        
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
    
    async def _create_test_plan(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a test plan
        
        Args:
            task: Test plan creation task
            
        Returns:
            Test plan creation result
        """
        plan_id = task.get("plan_id")
        if not plan_id:
            return {
                "success": False,
                "error": "Plan ID is required"
            }
        
        # Think about test planning
        thinking_result = await self.think(
            f"Create a test plan for {task.get('name', 'unnamed feature')} with requirements: {task.get('requirements', '')}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Create test plan structure
        test_plan = {
            "id": plan_id,
            "name": task.get("name", "Unnamed Test Plan"),
            "description": task.get("description", ""),
            "requirements": task.get("requirements", ""),
            "test_cases": thinking_result["final_decision"].get("test_cases", []),
            "test_scenarios": thinking_result["final_decision"].get("test_scenarios", []),
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "coverage_targets": {},
            "dependencies": []
        }
        
        self.test_plans[plan_id] = test_plan
        
        return {
            "success": True,
            "test_plan": test_plan
        }
    
    async def _execute_tests(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test cases
        
        Args:
            task: Test execution task
            
        Returns:
            Test execution result
        """
        plan_id = task.get("plan_id")
        if not plan_id or plan_id not in self.test_plans:
            return {
                "success": False,
                "error": "Valid plan ID is required"
            }
        
        # Think about test execution
        thinking_result = await self.think(
            f"Execute tests for plan {plan_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Create test result structure
        test_result = {
            "id": f"result_{plan_id}",
            "plan_id": plan_id,
            "execution_time": datetime.now().isoformat(),
            "results": thinking_result["final_decision"].get("results", []),
            "summary": thinking_result["final_decision"].get("summary", {}),
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.test_results[test_result["id"]] = test_result
        
        # Update test plan with result reference
        self.test_plans[plan_id]["last_result_id"] = test_result["id"]
        self.test_plans[plan_id]["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "test_result": test_result
        }
    
    async def _report_bug(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Report a bug
        
        Args:
            task: Bug reporting task
            
        Returns:
            Bug reporting result
        """
        plan_id = task.get("plan_id")
        bug_description = task.get("bug_description")
        
        if not plan_id or not bug_description:
            return {
                "success": False,
                "error": "Plan ID and bug description are required"
            }
        
        if plan_id not in self.test_plans:
            return {
                "success": False,
                "error": f"Plan {plan_id} not found"
            }
        
        # Think about bug reporting
        thinking_result = await self.think(
            f"Report bug '{bug_description}' for plan {plan_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Create bug report structure
        bug_report = {
            "id": f"bug_{plan_id}",
            "plan_id": plan_id,
            "description": bug_description,
            "severity": thinking_result["final_decision"].get("severity", "medium"),
            "priority": thinking_result["final_decision"].get("priority", "normal"),
            "steps_to_reproduce": thinking_result["final_decision"].get("steps", []),
            "expected_behavior": thinking_result["final_decision"].get("expected", ""),
            "actual_behavior": thinking_result["final_decision"].get("actual", ""),
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.bug_reports[bug_report["id"]] = bug_report
        
        return {
            "success": True,
            "bug_report": bug_report
        }
    
    async def _automate_tests(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Automate test cases
        
        Args:
            task: Test automation task
            
        Returns:
            Test automation result
        """
        plan_id = task.get("plan_id")
        if not plan_id or plan_id not in self.test_plans:
            return {
                "success": False,
                "error": "Valid plan ID is required"
            }
        
        # Think about test automation
        thinking_result = await self.think(
            f"Automate tests for plan {plan_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Generate automated test code
        test_result = await self.generate_code(
            requirements=f"Automate tests for plan {plan_id}",
            language=task.get("language", "python"),
            framework=task.get("framework", "pytest")
        )
        
        if not test_result["success"]:
            return test_result
        
        # Update test plan with automated tests
        test_plan = self.test_plans[plan_id]
        test_plan["automated_tests"] = test_result["code"]
        test_plan["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "automated_tests": test_result["code"]
        }
    
    async def _test_performance(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Test system performance
        
        Args:
            task: Performance testing task
            
        Returns:
            Performance testing result
        """
        plan_id = task.get("plan_id")
        if not plan_id or plan_id not in self.test_plans:
            return {
                "success": False,
                "error": "Valid plan ID is required"
            }
        
        # Think about performance testing
        thinking_result = await self.think(
            f"Test performance for plan {plan_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Create performance test result
        performance_result = {
            "id": f"perf_{plan_id}",
            "plan_id": plan_id,
            "metrics": thinking_result["final_decision"].get("metrics", {}),
            "benchmarks": thinking_result["final_decision"].get("benchmarks", []),
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.test_results[performance_result["id"]] = performance_result
        
        # Update test plan with performance results
        test_plan = self.test_plans[plan_id]
        test_plan["performance_results"] = performance_result
        test_plan["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "performance_result": performance_result
        }
    
    async def _test_security(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Test system security
        
        Args:
            task: Security testing task
            
        Returns:
            Security testing result
        """
        plan_id = task.get("plan_id")
        if not plan_id or plan_id not in self.test_plans:
            return {
                "success": False,
                "error": "Valid plan ID is required"
            }
        
        # Think about security testing
        thinking_result = await self.think(
            f"Test security for plan {plan_id}"
        )
        
        if not thinking_result["success"]:
            return thinking_result
        
        # Create security test result
        security_result = {
            "id": f"sec_{plan_id}",
            "plan_id": plan_id,
            "vulnerabilities": thinking_result["final_decision"].get("vulnerabilities", []),
            "security_issues": thinking_result["final_decision"].get("issues", []),
            "recommendations": thinking_result["final_decision"].get("recommendations", []),
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.test_results[security_result["id"]] = security_result
        
        # Update test plan with security results
        test_plan = self.test_plans[plan_id]
        test_plan["security_results"] = security_result
        test_plan["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "security_result": security_result
        }
    
    def get_test_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get test plan details
        
        Args:
            plan_id: Plan ID
            
        Returns:
            Test plan details if found, None otherwise
        """
        return self.test_plans.get(plan_id)
    
    def get_test_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Get test result details
        
        Args:
            result_id: Result ID
            
        Returns:
            Test result details if found, None otherwise
        """
        return self.test_results.get(result_id)
    
    def get_bug_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get bug report details
        
        Args:
            report_id: Report ID
            
        Returns:
            Bug report details if found, None otherwise
        """
        return self.bug_reports.get(report_id) 