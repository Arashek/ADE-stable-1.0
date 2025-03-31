import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Dict, Any

# Determine the root directory
ROOT_DIR = Path(__file__).parent.parent.parent

# Load environment variables
load_dotenv(ROOT_DIR / ".env")

class ModelConfig(BaseModel):
    """Configuration for AI models"""
    openai_api_key: str = Field(default=os.getenv("OPENAI_API_KEY", ""))
    anthropic_api_key: str = Field(default=os.getenv("ANTHROPIC_API_KEY", ""))
    deepseek_api_key: str = Field(default=os.getenv("DEEPSEEK_API_KEY", ""))
    groq_api_key: str = Field(default=os.getenv("GROQ_API_KEY", ""))
    model_selection_strategy: str = Field(default=os.getenv("MODEL_SELECTION_STRATEGY", "balanced"))
    
    # Model-specific configurations
    temperature: float = Field(default=float(os.getenv("TEMPERATURE", "0.7")))
    max_tokens: int = Field(default=int(os.getenv("MAX_TOKENS", "1000")))
    top_p: float = Field(default=float(os.getenv("TOP_P", "0.9")))
    
    # Code Understanding Models
    code_understanding: Dict[str, Any] = Field(default_factory=lambda: {
        "models": {
            "primary": "codellama/CodeLlama-34b-Instruct-hf",
            "secondary": "bigcode/starcoder2-33b",
            "tertiary": "deepseek-ai/deepseek-coder-33b-instruct"
        },
        "temperature": 0.2,
        "max_tokens": 2000,
        "context_window": 8192,
        "specialized_config": {
            "ast_parsing": True,
            "code_structure_analysis": True,
            "dependency_analysis": True
        }
    })
    
    # General Understanding Models
    general_understanding: Dict[str, Any] = Field(default_factory=lambda: {
        "models": {
            "primary": "anthropic/claude-3-sonnet-20240229",
            "secondary": "gpt-4-turbo-preview",
            "tertiary": "google/palm-2"
        },
        "temperature": 0.3,
        "max_tokens": 4000,
        "context_window": 16384,
        "specialized_config": {
            "multilingual": True,
            "multimodal": True,
            "context_retention": True
        }
    })
    
    # Tool Use Models
    tool_use: Dict[str, Any] = Field(default_factory=lambda: {
        "models": {
            "primary": "anthropic/claude-3-sonnet-20240229",
            "secondary": "gpt-4-turbo-preview",
            "tertiary": "deepseek-ai/deepseek-coder-33b-instruct"
        },
        "temperature": 0.1,
        "max_tokens": 2000,
        "specialized_config": {
            "api_interaction": True,
            "tool_selection": True,
            "parameter_validation": True,
            "error_handling": True
        }
    })
    
    # Planning Models
    planning: Dict[str, Any] = Field(default_factory=lambda: {
        "models": {
            "primary": "anthropic/claude-3-sonnet-20240229",
            "secondary": "gpt-4-turbo-preview",
            "tertiary": "google/palm-2"
        },
        "temperature": 0.2,
        "max_tokens": 2000,
        "specialized_config": {
            "task_decomposition": True,
            "dependency_planning": True,
            "resource_optimization": True,
            "parallel_execution": True
        }
    })
    
    # Code Generation Models
    code_generation: Dict[str, Any] = Field(default_factory=lambda: {
        "models": {
            "primary": "bigcode/starcoder2-33b",
            "secondary": "codellama/CodeLlama-34b-Instruct-hf",
            "tertiary": "deepseek-ai/deepseek-coder-33b-instruct"
        },
        "temperature": 0.3,
        "max_tokens": 4000,
        "specialized_config": {
            "code_quality": True,
            "style_consistency": True,
            "documentation": True,
            "testing": True
        }
    })
    
    # AST Parser Configuration
    ast_parser: Dict[str, Any] = Field(default_factory=lambda: {
        "model": "custom-ast-parser",
        "features": {
            "syntax_analysis": True,
            "semantic_analysis": True,
            "type_inference": True,
            "control_flow": True,
            "data_flow": True
        },
        "supported_languages": [
            "python", "javascript", "typescript", "java", "cpp", "go", "rust"
        ]
    })
    
    # Tool Registry Configuration
    tool_registry: Dict[str, Any] = Field(default_factory=lambda: {
        "categories": {
            "code_analysis": True,
            "testing": True,
            "documentation": True,
            "deployment": True,
            "monitoring": True
        },
        "validation": {
            "parameter_checking": True,
            "type_safety": True,
            "security_scanning": True
        }
    })
    
    # Performance Optimization
    optimization: Dict[str, Any] = Field(default_factory=lambda: {
        "caching": {
            "model_cache": True,
            "response_cache": True,
            "ast_cache": True
        },
        "parallelization": {
            "model_parallel": True,
            "task_parallel": True,
            "tool_parallel": True
        },
        "resource_management": {
            "gpu_optimization": True,
            "memory_optimization": True,
            "token_optimization": True
        }
    })

class DatabaseConfig(BaseModel):
    """Configuration for databases"""
    mongodb_uri: str = Field(default=os.getenv("MONGODB_URI", "mongodb://localhost:27017/ade"))
    redis_uri: str = Field(default=os.getenv("REDIS_URI", "redis://localhost:6379/0"))
    vector_db_path: Path = Field(default=ROOT_DIR / "data" / "vector")
    
class EnvironmentConfig(BaseModel):
    """Configuration for containerized environments"""
    default_docker_image: str = Field(default=os.getenv("DEFAULT_DOCKER_IMAGE", "python:3.10-slim"))
    container_workspace_dir: str = Field(default="/workspace")
    resource_limits: dict = Field(default={"cpu": "1", "memory": "2g"})
    
class AppConfig(BaseModel):
    """Main application configuration"""
    environment: str = Field(default=os.getenv("ENVIRONMENT", "development"))
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))
    data_dir: Path = Field(default=ROOT_DIR / "data")
    models: ModelConfig = Field(default_factory=ModelConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    environment_config: EnvironmentConfig = Field(default_factory=EnvironmentConfig)

# Create global config instances
config = AppConfig()
settings = config  # Alias for compatibility

__all__ = ['config', 'settings', 'ModelConfig', 'DatabaseConfig', 'EnvironmentConfig', 'AppConfig']