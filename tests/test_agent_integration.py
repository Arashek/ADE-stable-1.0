"""
End-to-End Integration Tests for ADE Agent Coordination System.

This script tests the complete workflow of agent interactions, task allocation,
caching, and prompt processing to ensure all components work together correctly.
"""

import sys
import os
import unittest
import asyncio
import json
import time
from typing import Dict, Any, List

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.agent_coordinator import AgentCoordinator
from backend.services.task_allocator import TaskAllocator, SimpleRoundRobinAllocator, PriorityBasedAllocator, WorkloadBalancingAllocator
from backend.services.agent_cache import AgentCache
from backend.core.models.task import Task
from backend.core.models.agent import Agent

# Mock services and dependencies
class MockAgent(Agent):
    def __init__(self, agent_id: str, name: str, capabilities: List[str], specialization: str = None):
        super().__init__(agent_id=agent_id, name=name)
        self.capabilities = capabilities
        self.specialization = specialization
        self.tasks_processed = 0
        self.processing_time_ms = 0
        self.failure_rate = 0.0
        self.busy = False

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock implementation of task processing"""
        self.tasks_processed += 1
        self.busy = True
        
        # Simulate processing time based on task complexity
        complexity = task_data.get('complexity', 1)
        processing_time = 0.1 * complexity
        await asyncio.sleep(processing_time)
        
        self.processing_time_ms += int(processing_time * 1000)
        self.busy = False
        
        return {
            'agent_id': self.agent_id,
            'task_id': task_data.get('task_id'),
            'result': f"Processed by {self.name}: {task_data.get('prompt', '')}",
            'status': 'completed',
            'processing_time_ms': int(processing_time * 1000)
        }

class TestAgentIntegration(unittest.TestCase):
    """End-to-end tests for the ADE Agent Coordination System"""
    
    def setUp(self):
        """Set up the test environment with agents, coordinator, and related services"""
        # Initialize the agent cache
        self.agent_cache = AgentCache()
        
        # Initialize different task allocators for testing
        self.round_robin_allocator = SimpleRoundRobinAllocator()
        self.priority_allocator = PriorityBasedAllocator()
        self.workload_allocator = WorkloadBalancingAllocator()
        
        # Create mock agents with different capabilities
        self.code_agent = MockAgent(
            agent_id="agent-001", 
            name="Code Generator",
            capabilities=["code_generation", "code_review", "refactoring"],
            specialization="code_generation"
        )
        
        self.design_agent = MockAgent(
            agent_id="agent-002", 
            name="Design Expert",
            capabilities=["ui_design", "ux_review", "wireframing"],
            specialization="ui_design"
        )
        
        self.requirements_agent = MockAgent(
            agent_id="agent-003", 
            name="Requirements Analyst",
            capabilities=["requirements_analysis", "user_stories", "acceptance_criteria"],
            specialization="requirements_analysis"
        )
        
        self.testing_agent = MockAgent(
            agent_id="agent-004", 
            name="Test Engineer",
            capabilities=["test_generation", "test_execution", "bug_reporting"],
            specialization="test_generation"
        )
        
        # Create the agent coordinator with the round robin allocator initially
        self.coordinator = AgentCoordinator(task_allocator=self.round_robin_allocator, agent_cache=self.agent_cache)
        
        # Register all agents with the coordinator
        self.coordinator.register_agent(self.code_agent)
        self.coordinator.register_agent(self.design_agent)
        self.coordinator.register_agent(self.requirements_agent)
        self.coordinator.register_agent(self.testing_agent)

    async def async_test_basic_task_allocation(self):
        """Test basic task allocation to ensure tasks are assigned to appropriate agents"""
        # Create a code generation task
        code_task = {
            "task_id": "task-001",
            "type": "code_generation",
            "prompt": "Create a function to calculate fibonacci sequence",
            "complexity": 2,
            "priority": 1
        }
        
        # Create a design task
        design_task = {
            "task_id": "task-002",
            "type": "ui_design",
            "prompt": "Design a login page for a web application",
            "complexity": 3,
            "priority": 2
        }
        
        # Process tasks through the coordinator
        code_result = await self.coordinator.start_task(code_task)
        design_result = await self.coordinator.start_task(design_task)
        
        # Verify each task was processed by the appropriate agent
        self.assertEqual(code_result['agent_id'], self.code_agent.agent_id)
        self.assertEqual(design_result['agent_id'], self.design_agent.agent_id)
        
        # Verify task results contain expected information
        self.assertEqual(code_result['task_id'], "task-001")
        self.assertEqual(design_result['task_id'], "task-002")
        self.assertEqual(code_result['status'], "completed")
        self.assertEqual(design_result['status'], "completed")

    async def async_test_caching_mechanism(self):
        """Test that the caching mechanism works for identical tasks"""
        # Create a task that will be executed twice
        repeat_task = {
            "task_id": "task-003",
            "type": "requirements_analysis",
            "prompt": "Analyze requirements for a contact management system",
            "complexity": 2,
            "priority": 1,
            "cache_key": "requirements-contact-system"  # Explicit cache key for testing
        }
        
        # Process the task the first time
        start_time = time.time()
        first_result = await self.coordinator.start_task(repeat_task)
        first_execution_time = time.time() - start_time
        
        # Process the same task again
        start_time = time.time()
        repeat_task["task_id"] = "task-003-repeat"  # Change task ID but keep the same cache key
        second_result = await self.coordinator.start_task(repeat_task)
        second_execution_time = time.time() - start_time
        
        # Verify the second execution was faster due to caching
        self.assertLess(second_execution_time, first_execution_time * 0.5)
        
        # Verify both results have the same content
        self.assertEqual(first_result['result'], second_result['result'])
        
        # Verify the cache hit is recorded
        self.assertIn("cache_hit", second_result)
        self.assertTrue(second_result["cache_hit"])

    async def async_test_priority_based_allocation(self):
        """Test that high-priority tasks are processed before low-priority tasks"""
        # Switch to priority-based allocator
        self.coordinator.task_allocator = self.priority_allocator
        
        # Create tasks with different priorities
        high_priority_task = {
            "task_id": "task-004",
            "type": "code_review",
            "prompt": "Review authentication code for security issues",
            "complexity": 3,
            "priority": 10  # High priority
        }
        
        medium_priority_task = {
            "task_id": "task-005",
            "type": "code_review",
            "prompt": "Review form validation code",
            "complexity": 2,
            "priority": 5  # Medium priority
        }
        
        low_priority_task = {
            "task_id": "task-006",
            "type": "code_review",
            "prompt": "Review code style compliance",
            "complexity": 1,
            "priority": 1  # Low priority
        }
        
        # Queue all tasks at once
        tasks = [medium_priority_task, low_priority_task, high_priority_task]
        task_futures = []
        
        for task in tasks:
            task_future = asyncio.create_task(self.coordinator.start_task(task))
            task_futures.append((task['task_id'], task_future))
        
        # Wait for all tasks to complete
        results = {}
        for task_id, future in task_futures:
            results[task_id] = await future
        
        # Verify tasks were executed in priority order
        self.assertLess(
            results["task-004"]["processing_order"], 
            results["task-005"]["processing_order"]
        )
        self.assertLess(
            results["task-005"]["processing_order"], 
            results["task-006"]["processing_order"]
        )

    async def async_test_workload_balancing(self):
        """Test that the workload is balanced across agents"""
        # Switch to workload balancing allocator
        self.coordinator.task_allocator = self.workload_allocator
        
        # Reset agent metrics
        for agent in self.coordinator.agents.values():
            agent.tasks_processed = 0
            agent.processing_time_ms = 0
        
        # Create multiple similar tasks
        tasks = []
        for i in range(20):
            task = {
                "task_id": f"task-{100+i}",
                "type": "code_generation" if i % 2 == 0 else "test_generation",
                "prompt": f"Generate code for task {i}",
                "complexity": 1 + (i % 3),
                "priority": 1
            }
            tasks.append(task)
        
        # Execute all tasks
        for task in tasks:
            await self.coordinator.start_task(task)
        
        # Check that workload is reasonably balanced
        code_agent_tasks = self.code_agent.tasks_processed
        test_agent_tasks = self.testing_agent.tasks_processed
        
        # Difference should not be more than 30% of the total
        self.assertLess(abs(code_agent_tasks - test_agent_tasks), 6)
        
        # Verify the coordinator has metrics for all agents
        for agent_id, metrics in self.coordinator.agent_metrics.items():
            self.assertIn("tasks_processed", metrics)
            self.assertIn("average_processing_time", metrics)

    async def async_test_error_handling(self):
        """Test error handling in the agent coordination system"""
        # Create a task that will cause an error
        error_task = {
            "task_id": "task-error",
            "type": "invalid_type",  # This type doesn't match any agent
            "prompt": "This will cause an error",
            "complexity": 1,
            "priority": 1
        }
        
        # Process the task and expect an error
        try:
            result = await self.coordinator.start_task(error_task)
            self.assertEqual(result['status'], "error")
            self.assertIn("error_message", result)
        except Exception as e:
            self.fail(f"Error handling failed: {str(e)}")
        
        # Verify the error is logged
        self.assertIn("task-error", self.coordinator.task_errors)

    async def async_test_dynamic_strategy_optimization(self):
        """Test that the allocation strategy is optimized based on workload"""
        # Initially use simple round robin
        self.coordinator.task_allocator = self.round_robin_allocator
        
        # Create a series of tasks with varying complexity and priority
        tasks = []
        for i in range(30):
            task = {
                "task_id": f"task-opt-{i}",
                "type": "code_generation" if i % 3 == 0 else "ui_design" if i % 3 == 1 else "test_generation",
                "prompt": f"Task {i} with varying complexity",
                "complexity": 1 + (i % 5),
                "priority": 1 + (i % 3)
            }
            tasks.append(task)
        
        # Process first batch of tasks
        for i in range(15):
            await self.coordinator.start_task(tasks[i])
        
        # Optimize the allocation strategy
        original_strategy = type(self.coordinator.task_allocator).__name__
        self.coordinator.optimize_allocation_strategy()
        new_strategy = type(self.coordinator.task_allocator).__name__
        
        # Execute remaining tasks with new strategy
        for i in range(15, 30):
            await self.coordinator.start_task(tasks[i])
        
        # Verify the strategy was changed after optimization
        self.assertNotEqual(original_strategy, new_strategy, 
                         "Allocation strategy should have been optimized based on workload")
        
        # Verify all tasks were completed
        self.assertEqual(len(self.coordinator.completed_tasks), 30)

    def test_all(self):
        """Run all async tests"""
        asyncio.run(self.run_all_tests())
        
    async def run_all_tests(self):
        """Helper method to run all async test methods"""
        await self.async_test_basic_task_allocation()
        await self.async_test_caching_mechanism()
        await self.async_test_priority_based_allocation()
        await self.async_test_workload_balancing()
        await self.async_test_error_handling()
        await self.async_test_dynamic_strategy_optimization()
        

if __name__ == '__main__':
    unittest.main()
