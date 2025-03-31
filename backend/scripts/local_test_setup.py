#!/usr/bin/env python
"""
Local Testing Setup for ADE Platform

This script sets up the local environment for testing the ADE platform,
including the consensus mechanism and agent coordination system.
"""

import os
import sys
import argparse
import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('local_test.log')
    ]
)
logger = logging.getLogger("local_test_setup")

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
try:
    from backend.services.coordination.agent_coordinator import AgentCoordinator
    from backend.services.coordination.agent_registry import AgentRegistry, AgentRegistryManager
    from backend.services.coordination.agent_interface import AgentInterface, AgentInterfaceFactory
    from backend.services.coordination.consensus_mechanism import ConsensusMechanism, ConflictDetector
    from backend.services.agents.specialized.validation_agent import ValidationAgent
    from backend.services.agents.specialized.design_agent import DesignAgent
    from backend.services.agents.specialized.architecture_agent import ArchitectureAgent
    from backend.services.agents.specialized.security_agent import SecurityAgent
    from backend.services.agents.specialized.performance_agent import PerformanceAgent
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.error("Make sure you're running this script from the project root directory")
    sys.exit(1)


class LocalTestSetup:
    """
    Setup and manage local testing environment for ADE platform.
    """
    
    def __init__(self):
        """Initialize the local test setup."""
        self.coordinator = None
        self.registry = None
        self.registry_manager = None
        self.specialized_agents = {}
        self.processes = []
        self.test_data_dir = Path(__file__).parent.parent / "tests" / "test_data"
        self.test_data_dir.mkdir(exist_ok=True, parents=True)
    
    async def setup_coordinator(self):
        """Set up the agent coordinator and registry."""
        logger.info("Setting up agent coordinator and registry")
        
        # Initialize coordinator
        self.coordinator = AgentCoordinator()
        
        # Get registry instance
        self.registry = self.coordinator.registry
        self.registry_manager = self.coordinator.registry_manager
        
        logger.info("Agent coordinator and registry set up successfully")
    
    async def setup_specialized_agents(self):
        """Set up specialized agents for testing."""
        logger.info("Setting up specialized agents")
        
        # Create agent instances
        self.specialized_agents = {
            "validation": ValidationAgent(),
            "design": DesignAgent(),
            "architecture": ArchitectureAgent(),
            "security": SecurityAgent(),
            "performance": PerformanceAgent()
        }
        
        # Register agents with the registry
        for agent_type, agent in self.specialized_agents.items():
            agent_id = f"{agent_type}-1"
            agent_interface = AgentInterfaceFactory.create_interface(
                agent_id=agent_id,
                agent_type=agent_type
            )
            
            # Get agent capabilities
            capabilities = agent.get_capabilities() if hasattr(agent, "get_capabilities") else []
            
            # Register agent
            success = await self.registry.register_agent(
                agent_id=agent_id,
                agent_type=agent_type,
                capabilities=capabilities,
                interface=agent_interface
            )
            
            if success:
                logger.info(f"Registered agent {agent_id} of type {agent_type}")
            else:
                logger.warning(f"Failed to register agent {agent_id}")
        
        logger.info("Specialized agents set up successfully")
    
    async def generate_test_data(self):
        """Generate test data for local testing."""
        logger.info("Generating test data for local testing")
        
        # Generate test conflicts
        conflicts_data = [
            {
                "attribute": "authentication.method",
                "values": {
                    "security": "oauth2",
                    "architecture": "jwt"
                },
                "selected_value": "oauth2",
                "selected_agent": "security",
                "confidence": 0.85
            },
            {
                "attribute": "database.encryption.enabled",
                "values": {
                    "security": True,
                    "performance": False
                },
                "selected_value": True,
                "selected_agent": "security",
                "confidence": 0.92
            },
            {
                "attribute": "ui.framework",
                "values": {
                    "design": "react",
                    "architecture": "angular"
                },
                "selected_value": "react",
                "selected_agent": "design",
                "confidence": 0.78
            }
        ]
        
        # Generate test consensus decisions
        consensus_decisions_data = [
            {
                "id": "decision_12345678",
                "key": "database_type",
                "description": "Choose database type for the application",
                "options": ["postgresql", "mongodb", "mysql"],
                "selected_option": "postgresql",
                "votes": [
                    {
                        "agent": "security",
                        "agent_id": "security-1",
                        "option": "postgresql",
                        "confidence": 0.8,
                        "reasoning": "PostgreSQL has better security features"
                    },
                    {
                        "agent": "architecture",
                        "agent_id": "architecture-1",
                        "option": "postgresql",
                        "confidence": 0.9,
                        "reasoning": "PostgreSQL is better for complex data models"
                    },
                    {
                        "agent": "design",
                        "agent_id": "design-1",
                        "option": "mongodb",
                        "confidence": 0.7,
                        "reasoning": "MongoDB is more flexible for UI data"
                    }
                ],
                "confidence": 0.85,
                "status": "resolved"
            },
            {
                "id": "decision_87654321",
                "key": "frontend_framework",
                "description": "Choose frontend framework for the application",
                "options": ["react", "vue", "angular"],
                "status": "in_progress",
                "votes": [
                    {
                        "agent": "design",
                        "agent_id": "design-1",
                        "option": "react",
                        "confidence": 0.9,
                        "reasoning": "React has better component reusability"
                    },
                    {
                        "agent": "performance",
                        "agent_id": "performance-1",
                        "option": "vue",
                        "confidence": 0.75,
                        "reasoning": "Vue has better performance for this use case"
                    }
                ]
            }
        ]
        
        # Save test data to files
        with open(self.test_data_dir / "conflicts.json", "w") as f:
            json.dump(conflicts_data, f, indent=2)
        
        with open(self.test_data_dir / "consensus_decisions.json", "w") as f:
            json.dump(consensus_decisions_data, f, indent=2)
        
        logger.info(f"Test data saved to {self.test_data_dir}")
    
    async def run_consensus_test(self):
        """Run a test of the consensus mechanism."""
        logger.info("Running consensus mechanism test")
        
        # Create a test decision point
        decision_point = {
            "id": f"test_decision_{int(time.time())}",
            "key": "api_versioning",
            "description": "Choose API versioning strategy",
            "options": ["url-path", "query-param", "header", "content-negotiation"]
        }
        
        # Get agent interfaces
        agent_interfaces = {}
        for agent_type in ["security", "architecture", "design"]:
            agent_ids = await self.registry.get_agents_by_type(agent_type)
            if agent_ids:
                agent_interface = await self.registry.get_agent_interface(agent_ids[0])
                if agent_interface:
                    agent_interfaces[agent_type] = agent_interface
        
        # Run consensus building
        consensus_result = await self.coordinator.consensus_mechanism.build_consensus(
            decision_point=decision_point,
            agent_interfaces=agent_interfaces,
            context={"task_type": "api_design"},
            threshold=0.7
        )
        
        logger.info(f"Consensus result: {consensus_result}")
        
        # Save result to test data
        with open(self.test_data_dir / "consensus_test_result.json", "w") as f:
            json.dump(consensus_result, f, indent=2)
        
        return consensus_result
    
    async def run_conflict_resolution_test(self):
        """Run a test of the conflict resolution mechanism."""
        logger.info("Running conflict resolution test")
        
        # Create a test conflict
        conflict = {
            "attribute": "security.cors.allowed_origins",
            "values": {
                "security": ["https://example.com"],
                "architecture": ["*"]
            }
        }
        
        # Create agent recommendations
        agent_recommendations = {
            "security": {
                "agent_type": "security",
                "result": {
                    "security": {
                        "cors": {
                            "allowed_origins": ["https://example.com"]
                        }
                    }
                }
            },
            "architecture": {
                "agent_type": "architecture",
                "result": {
                    "security": {
                        "cors": {
                            "allowed_origins": ["*"]
                        }
                    }
                }
            }
        }
        
        # Run conflict resolution
        resolution = await self.coordinator.consensus_mechanism.resolve_conflict(
            conflict=conflict,
            agent_recommendations=agent_recommendations,
            strategy="hybrid",
            context={"task_type": "security_configuration"}
        )
        
        logger.info(f"Conflict resolution result: {resolution}")
        
        # Save result to test data
        with open(self.test_data_dir / "conflict_resolution_test_result.json", "w") as f:
            json.dump(resolution, f, indent=2)
        
        return resolution
    
    def start_backend_server(self):
        """Start the backend server for local testing."""
        logger.info("Starting backend server")
        
        # Start the backend server
        backend_dir = Path(__file__).parent.parent
        cmd = [sys.executable, str(backend_dir / "main.py")]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(backend_dir),
                env={**os.environ, "TESTING": "1"},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(process)
            
            # Wait a bit for the server to start
            time.sleep(2)
            
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                logger.error(f"Backend server failed to start: {stderr}")
                return False
            
            logger.info("Backend server started successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to start backend server: {e}")
            return False
    
    def start_frontend_dev_server(self):
        """Start the frontend development server for local testing."""
        logger.info("Starting frontend development server")
        
        # Start the frontend server
        frontend_dir = Path(__file__).parent.parent.parent / "frontend"
        
        if not frontend_dir.exists():
            logger.error(f"Frontend directory not found: {frontend_dir}")
            return False
        
        cmd = ["npm", "run", "dev"]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(frontend_dir),
                env={**os.environ, "BROWSER": "none"},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(process)
            
            # Wait a bit for the server to start
            time.sleep(5)
            
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                logger.error(f"Frontend server failed to start: {stderr}")
                return False
            
            logger.info("Frontend development server started successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to start frontend server: {e}")
            return False
    
    def cleanup(self):
        """Clean up processes and resources."""
        logger.info("Cleaning up processes and resources")
        
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        logger.info("Cleanup completed")


async def main():
    """Main function to run the local test setup."""
    parser = argparse.ArgumentParser(description="Local Testing Setup for ADE Platform")
    parser.add_argument("--backend-only", action="store_true", help="Start only the backend server")
    parser.add_argument("--frontend-only", action="store_true", help="Start only the frontend server")
    parser.add_argument("--test-only", action="store_true", help="Run tests without starting servers")
    parser.add_argument("--generate-data", action="store_true", help="Generate test data only")
    args = parser.parse_args()
    
    setup = LocalTestSetup()
    
    try:
        # Set up coordinator and agents
        await setup.setup_coordinator()
        await setup.setup_specialized_agents()
        
        # Generate test data if requested
        if args.generate_data:
            await setup.generate_test_data()
            return
        
        # Run tests if requested
        if args.test_only:
            await setup.run_consensus_test()
            await setup.run_conflict_resolution_test()
            return
        
        # Start servers
        if not args.frontend_only:
            setup.start_backend_server()
        
        if not args.backend_only:
            setup.start_frontend_dev_server()
        
        # Keep the script running
        logger.info("Local test environment is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shutting down...")
    except Exception as e:
        logger.error(f"Error in local test setup: {e}")
    finally:
        setup.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
