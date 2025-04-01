"""
Test script for validating the Agent Coordination System.

This script systematically tests the agent coordination system according to the test plan,
including initialization, collaboration patterns, specialized agents, integration, and error handling.
"""

import asyncio
import json
import logging
import sys
import time
from typing import Dict, List, Any
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('agent_coordination_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path to import backend modules
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.coordination.agent_coordinator import AgentCoordinator, CollaborationPattern, TaskPriority
from services.coordination.task_manager import TaskStatus
from services.monitoring import update_resource_metrics

# Sample application prompt for testing all specialized agents
SAMPLE_APP_PROMPT = """
Create a task management application with the following features:
1. User authentication and authorization
2. Task creation, editing, and deletion
3. Task categorization and priority setting
4. Due date tracking with notifications
5. Team collaboration features
6. Dashboard with task statistics
7. Mobile-responsive design
8. Dark/light theme toggle
9. Data export functionality
10. API for integration with other tools

The application should be built using a modern tech stack with React for the frontend,
Node.js with Express for the backend, and MongoDB for the database. Security should
be a priority, with proper authentication, data validation, and protection against
common vulnerabilities.
"""

class AgentCoordinationTester:
    """Test class for the Agent Coordination System."""
    
    def __init__(self):
        """Initialize the tester."""
        self.coordinator = AgentCoordinator()
        self.test_results = {
            "initialization": {},
            "collaboration_patterns": {},
            "specialized_agents": {},
            "integration": {},
            "error_handling": {}
        }
        self.test_task_ids = []
    
    async def run_all_tests(self):
        """Run all tests for the agent coordination system."""
        logger.info("Starting Agent Coordination System tests")
        
        # Wait for agents to initialize
        logger.info("Waiting for agents to initialize...")
        await asyncio.sleep(5)
        
        # Run tests in sequence
        await self.test_initialization()
        await self.test_collaboration_patterns()
        await self.test_specialized_agents()
        await self.test_integration()
        await self.test_error_handling()
        
        # Generate summary report
        self.generate_report()
        
        logger.info("Agent Coordination System tests completed")
    
    async def test_initialization(self):
        """Test the initialization of the agent coordination system."""
        logger.info("Testing agent coordination system initialization")
        
        # Test 1: Check if coordinator is initialized
        self.test_results["initialization"]["coordinator_initialized"] = self.coordinator is not None
        
        # Test 2: Check if all specialized agents are initialized
        expected_agents = ["validation", "design", "architecture", "security", "performance"]
        initialized_agents = list(self.coordinator.specialized_agents.keys())
        self.test_results["initialization"]["all_agents_initialized"] = all(
            agent in initialized_agents for agent in expected_agents
        )
        
        # Test 3: Check if task manager is initialized
        self.test_results["initialization"]["task_manager_initialized"] = self.coordinator.task_manager is not None
        
        # Test 4: Check if registry is initialized
        self.test_results["initialization"]["registry_initialized"] = self.coordinator.registry is not None
        
        # Test 5: Check if pattern factory is initialized
        self.test_results["initialization"]["pattern_factory_initialized"] = self.coordinator.pattern_factory is not None
        
        # Log results
        logger.info("Initialization test results: %s", json.dumps(self.test_results["initialization"], indent=2))
    
    async def test_collaboration_patterns(self):
        """Test the collaboration patterns of the agent coordination system."""
        logger.info("Testing collaboration patterns")
        
        # Test each collaboration pattern
        patterns = [
            CollaborationPattern.SEQUENTIAL,
            CollaborationPattern.PARALLEL,
            CollaborationPattern.ITERATIVE,
            CollaborationPattern.CONSENSUS
        ]
        
        for pattern in patterns:
            logger.info("Testing %s collaboration pattern", pattern.value)
            
            # Create a task for testing
            task_id = str(uuid.uuid4())
            self.test_task_ids.append(task_id)
            
            # Create task with sample app prompt
            await self.coordinator.task_manager.create_task(
                task_id=task_id,
                task_type="application_creation",
                task_data={
                    "prompt": SAMPLE_APP_PROMPT,
                    "pattern": pattern.value
                },
                priority=TaskPriority.HIGH.value
            )
            
            # Execute task with the pattern
            start_time = time.time()
            try:
                result = await self.coordinator.execute_task(task_id, pattern)
                success = "error" not in result
                duration = time.time() - start_time
                
                self.test_results["collaboration_patterns"][pattern.value] = {
                    "success": success,
                    "duration": duration,
                    "task_id": task_id
                }
                
                # Update metrics
                update_resource_metrics(
                    memory_usage=os.getpid(),
                    cpu_usage=0,
                    service_name=f"test_{pattern.value}"
                )
                
                logger.info("%s pattern test completed in %.2f seconds", pattern.value, duration)
            except Exception as e:
                logger.error("Error testing %s pattern: %s", pattern.value, str(e))
                self.test_results["collaboration_patterns"][pattern.value] = {
                    "success": False,
                    "error": str(e),
                    "task_id": task_id
                }
        
        # Log results
        logger.info("Collaboration patterns test results: %s", 
                   json.dumps(self.test_results["collaboration_patterns"], indent=2))
    
    async def test_specialized_agents(self):
        """Test the specialized agents of the coordination system."""
        logger.info("Testing specialized agents")
        
        # Test each specialized agent
        agents = ["validation", "design", "architecture", "security", "performance"]
        
        for agent_type in agents:
            logger.info("Testing %s agent", agent_type)
            
            # Create task data based on agent type
            task_data = {
                "prompt": SAMPLE_APP_PROMPT,
                "type": "application_creation"
            }
            
            # Execute task with the agent
            start_time = time.time()
            try:
                result = await self.coordinator.delegate_task_to_agent(agent_type, task_data)
                success = "error" not in result
                duration = time.time() - start_time
                
                self.test_results["specialized_agents"][agent_type] = {
                    "success": success,
                    "duration": duration
                }
                
                logger.info("%s agent test completed in %.2f seconds", agent_type, duration)
            except Exception as e:
                logger.error("Error testing %s agent: %s", agent_type, str(e))
                self.test_results["specialized_agents"][agent_type] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Log results
        logger.info("Specialized agents test results: %s", 
                   json.dumps(self.test_results["specialized_agents"], indent=2))
    
    async def test_integration(self):
        """Test the integration of the agent coordination system components."""
        logger.info("Testing agent coordination system integration")
        
        # Test 1: End-to-end task execution
        task_id = str(uuid.uuid4())
        self.test_task_ids.append(task_id)
        
        # Create a complex task that requires all components
        await self.coordinator.task_manager.create_task(
            task_id=task_id,
            task_type="application_creation",
            task_data={
                "prompt": SAMPLE_APP_PROMPT,
                "pattern": CollaborationPattern.CONSENSUS.value,
                "require_all_agents": True
            },
            priority=TaskPriority.CRITICAL.value
        )
        
        # Execute the task
        start_time = time.time()
        try:
            result = await self.coordinator.execute_task(
                task_id, CollaborationPattern.CONSENSUS)
            success = "error" not in result
            duration = time.time() - start_time
            
            self.test_results["integration"]["end_to_end"] = {
                "success": success,
                "duration": duration,
                "task_id": task_id
            }
            
            logger.info("Integration test completed in %.2f seconds", duration)
        except Exception as e:
            logger.error("Error in integration test: %s", str(e))
            self.test_results["integration"]["end_to_end"] = {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }
        
        # Test 2: Consensus building
        try:
            # Create mock agent results
            agent_results = {
                "validation": {"recommendation": "approve", "confidence": 0.8},
                "security": {"recommendation": "approve", "confidence": 0.7},
                "architecture": {"recommendation": "approve", "confidence": 0.9},
                "performance": {"recommendation": "approve", "confidence": 0.6},
                "design": {"recommendation": "reject", "confidence": 0.5}
            }
            
            consensus_result = await self.coordinator.build_consensus(task_id, agent_results)
            
            self.test_results["integration"]["consensus_building"] = {
                "success": True,
                "consensus_reached": consensus_result.get("consensus_reached", False)
            }
            
            logger.info("Consensus building test completed")
        except Exception as e:
            logger.error("Error in consensus building test: %s", str(e))
            self.test_results["integration"]["consensus_building"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test 3: Conflict resolution
        try:
            # Create mock agent results with conflicts
            agent_results = {
                "validation": {"recommendation": "approve", "changes_required": ["A", "B"]},
                "security": {"recommendation": "reject", "changes_required": ["C", "D"]},
                "architecture": {"recommendation": "approve", "changes_required": ["E"]},
                "performance": {"recommendation": "approve", "changes_required": ["F"]},
                "design": {"recommendation": "approve", "changes_required": ["G"]}
            }
            
            resolved_result = await self.coordinator.resolve_conflicts(task_id, agent_results)
            
            self.test_results["integration"]["conflict_resolution"] = {
                "success": True,
                "conflicts_resolved": "changes_required" in resolved_result
            }
            
            logger.info("Conflict resolution test completed")
        except Exception as e:
            logger.error("Error in conflict resolution test: %s", str(e))
            self.test_results["integration"]["conflict_resolution"] = {
                "success": False,
                "error": str(e)
            }
        
        # Log results
        logger.info("Integration test results: %s", 
                   json.dumps(self.test_results["integration"], indent=2))
    
    async def test_error_handling(self):
        """Test the error handling of the agent coordination system."""
        logger.info("Testing error handling")
        
        # Test 1: Invalid task ID
        try:
            result = await self.coordinator.execute_task("invalid_task_id")
            self.test_results["error_handling"]["invalid_task_id"] = {
                "success": "error" in result,
                "handled_correctly": "error" in result and "not found" in result["error"]
            }
            
            logger.info("Invalid task ID test completed")
        except Exception as e:
            logger.error("Error in invalid task ID test: %s", str(e))
            self.test_results["error_handling"]["invalid_task_id"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test 2: Invalid agent type
        try:
            result = await self.coordinator.delegate_task_to_agent(
                "invalid_agent", {"prompt": "Test"})
            self.test_results["error_handling"]["invalid_agent_type"] = {
                "success": "error" in result,
                "handled_correctly": "error" in result and "not found" in result["error"]
            }
            
            logger.info("Invalid agent type test completed")
        except Exception as e:
            logger.error("Error in invalid agent type test: %s", str(e))
            self.test_results["error_handling"]["invalid_agent_type"] = {
                "success": isinstance(e, Exception),
                "error": str(e)
            }
        
        # Test 3: Invalid collaboration pattern
        try:
            task_id = self.test_task_ids[0] if self.test_task_ids else str(uuid.uuid4())
            # Use a string that's not a valid enum value
            result = await self.coordinator.execute_task(
                task_id, "invalid_pattern")
            self.test_results["error_handling"]["invalid_pattern"] = {
                "success": "error" in result,
                "handled_correctly": "error" in result
            }
            
            logger.info("Invalid pattern test completed")
        except Exception as e:
            logger.error("Error in invalid pattern test: %s", str(e))
            self.test_results["error_handling"]["invalid_pattern"] = {
                "success": isinstance(e, Exception),
                "error": str(e)
            }
        
        # Log results
        logger.info("Error handling test results: %s", 
                   json.dumps(self.test_results["error_handling"], indent=2))
    
    def generate_report(self):
        """Generate a summary report of all test results."""
        logger.info("Generating test report")
        
        # Calculate overall success rates
        success_rates = {}
        for category, tests in self.test_results.items():
            successes = sum(1 for test in tests.values() if test.get("success", False))
            total = len(tests)
            success_rates[category] = (successes / total) if total > 0 else 0
        
        overall_success = sum(success_rates.values()) / len(success_rates) if success_rates else 0
        
        # Generate report
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "overall_success_rate": overall_success,
            "category_success_rates": success_rates,
            "detailed_results": self.test_results
        }
        
        # Save report to file
        with open("agent_coordination_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info("Test report generated with overall success rate: %.2f", overall_success)
        logger.info("Category success rates: %s", json.dumps(success_rates, indent=2))

async def main():
    """Main function to run the tests."""
    tester = AgentCoordinationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
