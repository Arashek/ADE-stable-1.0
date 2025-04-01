"""
Test script for validating the metrics collection and monitoring setup.

This script tests the metrics collection functionality for the ADE platform,
focusing on agent tasks, collaboration patterns, and resource usage metrics.
"""

import os
import sys
import time
import logging
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('metrics_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the metrics module
from services.monitoring.metrics import (
    track_agent_task,
    track_collaboration_pattern,
    track_consensus_decision,
    track_conflict_resolution,
    update_resource_metrics,
    get_metrics
)

class MetricsTest:
    """Test class for metrics collection and monitoring."""
    
    def __init__(self):
        """Initialize the metrics test."""
        self.test_results = {}
    
    async def run_all_tests(self):
        """Run all metrics tests."""
        logger.info("Starting metrics tests")
        
        # Run tests
        await self.test_agent_task_metrics()
        await self.test_collaboration_pattern_metrics()
        await self.test_consensus_decision_metrics()
        await self.test_conflict_resolution_metrics()
        await self.test_resource_metrics()
        
        # Get and display all metrics
        all_metrics = get_metrics()
        logger.info("All metrics: %s", all_metrics)
        
        logger.info("Metrics tests completed")
    
    async def test_agent_task_metrics(self):
        """Test agent task metrics collection."""
        logger.info("Testing agent task metrics")
        
        # Test decorator
        @track_agent_task("validation", "code_review")
        async def test_validation_task():
            logger.info("Executing validation task")
            await asyncio.sleep(0.5)  # Simulate task execution
            return {"success": True, "validation_score": 0.85}
        
        # Execute task
        start_time = time.time()
        result = await test_validation_task()
        duration = time.time() - start_time
        
        self.test_results["agent_task_metrics"] = {
            "success": result.get("success", False),
            "duration": duration
        }
        
        logger.info("Agent task metrics test completed in %.2f seconds", duration)
    
    async def test_collaboration_pattern_metrics(self):
        """Test collaboration pattern metrics collection."""
        logger.info("Testing collaboration pattern metrics")
        
        # Test decorator
        @track_collaboration_pattern("sequential")
        async def test_sequential_pattern():
            logger.info("Executing sequential pattern")
            await asyncio.sleep(0.5)  # Simulate pattern execution
            return {"success": True, "steps_completed": 3}
        
        # Execute pattern
        start_time = time.time()
        result = await test_sequential_pattern()
        duration = time.time() - start_time
        
        self.test_results["collaboration_pattern_metrics"] = {
            "success": result.get("success", False),
            "duration": duration
        }
        
        logger.info("Collaboration pattern metrics test completed in %.2f seconds", duration)
    
    async def test_consensus_decision_metrics(self):
        """Test consensus decision metrics collection."""
        logger.info("Testing consensus decision metrics")
        
        # Test decorator
        @track_consensus_decision()
        async def test_consensus_decision():
            logger.info("Building consensus")
            await asyncio.sleep(0.5)  # Simulate consensus building
            return {
                "consensus_reached": True,
                "decision": "approve",
                "confidence": 0.8
            }
        
        # Execute consensus decision
        start_time = time.time()
        result = await test_consensus_decision()
        duration = time.time() - start_time
        
        self.test_results["consensus_decision_metrics"] = {
            "success": result.get("consensus_reached", False),
            "duration": duration
        }
        
        logger.info("Consensus decision metrics test completed in %.2f seconds", duration)
    
    async def test_conflict_resolution_metrics(self):
        """Test conflict resolution metrics collection."""
        logger.info("Testing conflict resolution metrics")
        
        # Test decorator
        @track_conflict_resolution("priority_based")
        async def test_conflict_resolution():
            logger.info("Resolving conflicts")
            await asyncio.sleep(0.5)  # Simulate conflict resolution
            return {
                "conflicts_resolved": True,
                "resolution_strategy": "priority_based",
                "changes_required": ["A", "B", "C"]
            }
        
        # Execute conflict resolution
        start_time = time.time()
        result = await test_conflict_resolution()
        duration = time.time() - start_time
        
        self.test_results["conflict_resolution_metrics"] = {
            "success": result.get("conflicts_resolved", False),
            "duration": duration
        }
        
        logger.info("Conflict resolution metrics test completed in %.2f seconds", duration)
    
    async def test_resource_metrics(self):
        """Test resource metrics collection."""
        logger.info("Testing resource metrics")
        
        # Update resource metrics
        start_time = time.time()
        
        # Update metrics multiple times to simulate monitoring
        for i in range(5):
            update_resource_metrics(
                memory_usage=100 + i * 10,  # Simulate increasing memory usage
                cpu_usage=20 + i * 5,       # Simulate increasing CPU usage
                service_name="test_service"
            )
            await asyncio.sleep(0.1)  # Small delay between updates
        
        duration = time.time() - start_time
        
        self.test_results["resource_metrics"] = {
            "success": True,
            "duration": duration
        }
        
        logger.info("Resource metrics test completed in %.2f seconds", duration)

async def main():
    """Main function to run the tests."""
    tester = MetricsTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
