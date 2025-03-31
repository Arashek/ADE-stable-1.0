"""API dependencies."""
from fastapi import Depends
from pydantic import BaseModel, Field
from typing import Dict, Any
from src.core.orchestrator import Orchestrator
from src.storage.document.connection import MongoDBConnection
from src.storage.document.repositories.task import TaskRepository

class Config:
    """Application configuration"""
    def __init__(self):
        # Load configuration from environment variables or config files
        # For now, we'll use hardcoded values
        self.providers = {
            "openai": {
                "enabled": True,
                "api_key": "placeholder-api-key",
                "model": "gpt-4"
            },
            "anthropic": {
                "enabled": True,
                "api_key": "placeholder-api-key",
                "model": "claude-3-opus-20240229"
            },
            "google": {
                "enabled": True,
                "api_key": "placeholder-api-key",
                "model": "gemini-pro"
            }
        }
        self.database = {
            "mongodb_uri": "mongodb://localhost:27017",
            "database_name": "ade"
        }

def get_config():
    """Get application configuration"""
    return Config()

def get_db_connector(config: Config = Depends(get_config)):
    """Get database connector"""
    return MongoDBConnection(
        connection_string=config.database["mongodb_uri"],
        database_name=config.database["database_name"]
    )

def get_task_repository(db_connector: MongoDBConnection = Depends(get_db_connector)):
    """Get task repository"""
    return TaskRepository(db_connector)

def get_orchestrator(
    config: Config = Depends(get_config),
    task_repository: TaskRepository = Depends(get_task_repository)
):
    """Get orchestrator instance"""
    return Orchestrator(config.__dict__, task_repository) 