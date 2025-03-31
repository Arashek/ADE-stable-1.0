import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from src.core.orchestrator import Orchestrator
from src.memory.memory_manager import MemoryManager
from src.database.mongodb import MongoDB
from src.auth.auth_manager import AuthManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_demo():
    """Initialize the demo environment with sample data"""
    try:
        # Initialize MongoDB connection
        mongodb = MongoDB("mongodb://localhost:27017/ade")
        await mongodb.connect()
        
        # Initialize memory manager
        memory_manager = MemoryManager(mongodb)
        await memory_manager.initialize()
        
        # Initialize orchestrator
        orchestrator = Orchestrator(memory_manager, mongodb)
        await orchestrator.initialize()
        
        # Initialize auth manager
        auth_manager = AuthManager(mongodb)
        await auth_manager.initialize()
        
        # Create sample users
        await create_sample_users(auth_manager)
        
        # Create sample providers
        await create_sample_providers(mongodb)
        
        # Create sample projects
        await create_sample_projects(orchestrator)
        
        logger.info("Demo environment initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize demo environment: {str(e)}")
        raise
    finally:
        await mongodb.disconnect()

async def create_sample_users(auth_manager):
    """Create sample users"""
    users = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "role": "admin",
            "created_at": datetime.now()
        },
        {
            "username": "developer",
            "email": "developer@example.com",
            "password": "dev123",
            "role": "developer",
            "created_at": datetime.now()
        }
    ]
    
    for user in users:
        await auth_manager.create_user(**user)

async def create_sample_providers(mongodb):
    """Create sample providers"""
    providers = [
        {
            "name": "OpenAI GPT-4",
            "type": "openai",
            "capabilities": ["code_generation", "code_review", "documentation"],
            "config": {
                "model": "gpt-4",
                "max_tokens": 4096
            }
        },
        {
            "name": "Anthropic Claude",
            "type": "anthropic",
            "capabilities": ["code_generation", "code_review", "documentation"],
            "config": {
                "model": "claude-3-opus-20240229",
                "max_tokens": 4096
            }
        },
        {
            "name": "Local LLM",
            "type": "local",
            "capabilities": ["code_generation", "code_review"],
            "config": {
                "model_path": "/models/local-llm",
                "max_tokens": 2048
            }
        }
    ]
    
    for provider in providers:
        await mongodb.insert_document("providers", provider)

async def create_sample_projects(orchestrator):
    """Create sample projects"""
    projects = [
        {
            "name": "Web Application",
            "description": "A modern web application built with React and FastAPI",
            "status": "active",
            "created_at": datetime.now(),
            "tasks": [
                {
                    "name": "Setup Project Structure",
                    "description": "Initialize project with basic structure",
                    "status": "completed",
                    "created_at": datetime.now(),
                    "completed_at": datetime.now()
                },
                {
                    "name": "Implement Authentication",
                    "description": "Add user authentication and authorization",
                    "status": "in_progress",
                    "created_at": datetime.now()
                }
            ]
        },
        {
            "name": "API Service",
            "description": "RESTful API service with microservices architecture",
            "status": "active",
            "created_at": datetime.now(),
            "tasks": [
                {
                    "name": "Design API Schema",
                    "description": "Design and document API endpoints",
                    "status": "completed",
                    "created_at": datetime.now(),
                    "completed_at": datetime.now()
                }
            ]
        }
    ]
    
    for project in projects:
        await orchestrator.create_project(**project)

if __name__ == "__main__":
    asyncio.run(init_demo()) 