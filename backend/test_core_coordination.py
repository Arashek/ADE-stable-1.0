"""
Simplified test for the core Agent Coordination System.

This script focuses on testing just the essential components of the agent coordination system
without relying on monitoring or other non-essential dependencies that have been temporarily disabled.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('core_coordination_test.log')
    ]
)
logger = logging.getLogger("core_coordination_test")

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import core coordination components
from services.coordination.agent_coordinator import AgentCoordinator, CollaborationPattern, TaskPriority
from services.coordination.task_manager import TaskManager, TaskStatus
from services.coordination.agent_registry import AgentRegistry, AgentStatus
from services.agents.specialized.validation_agent import ValidationAgent
from services.agents.specialized.design_agent import DesignAgent
from services.agents.specialized.architecture_agent import ArchitectureAgent
from services.agents.specialized.security_agent import SecurityAgent
from services.agents.specialized.performance_agent import PerformanceAgent

async def test_core_coordination():
    """Test the core functionality of the agent coordination system."""
    logger.info("Starting core coordination test")
    
    # Initialize the agent coordinator
    coordinator = AgentCoordinator()
    logger.info("Agent coordinator initialized")
    
    # Get the agent registry
    registry = coordinator.registry
    
    # Register specialized agents
    try:
        agents = [
            ValidationAgent(),
            DesignAgent(),
            ArchitectureAgent(),
            SecurityAgent(),
            PerformanceAgent()
        ]
        
        for agent in agents:
            registry.register_agent(agent)
            logger.info(f"Registered agent: {agent.agent_id} ({agent.__class__.__name__})")
        
        # Verify agents were registered
        all_agents = registry.get_all_agents()
        logger.info(f"Total registered agents: {len(all_agents)}")
        for agent in all_agents:
            logger.info(f"Agent: {agent.agent_id}, Status: {agent.status}")
        
        # Create a simple test task
        task_data = {
            "type": "test_task",
            "description": "Test task for core coordination system",
            "priority": TaskPriority.MEDIUM.value,
            "collaboration_pattern": CollaborationPattern.SEQUENTIAL.value,
            "agent_sequence": [agent.agent_id for agent in all_agents]
        }
        
        # Submit the task
        task_id = coordinator.create_task(task_data)
        logger.info(f"Created task with ID: {task_id}")
        
        # Get task status
        task = coordinator.get_task(task_id)
        logger.info(f"Task status: {task['status']}")
        
        # Core coordination test successful
        logger.info("Core coordination test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error in core coordination test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    """Run the core coordination test."""
    success = await test_core_coordination()
    if success:
        logger.info("✅ Core agent coordination system is working!")
    else:
        logger.error("❌ Core agent coordination system test failed")

if __name__ == "__main__":
    asyncio.run(main())
