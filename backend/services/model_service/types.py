from typing import Dict, Optional
from pydantic import BaseModel, Field

class ModelRequest(BaseModel):
    """
    Request model for generation endpoints
    """
    prompt: str = Field(..., description="The prompt to generate from")
    task_type: str = Field(..., description="Type of task (code_generation, analysis, explanation)")
    model: Optional[str] = Field(None, description="Specific model to use")
    temperature: float = Field(0.7, description="Sampling temperature")
    max_tokens: int = Field(2000, description="Maximum tokens to generate")
    context: Optional[Dict] = Field(None, description="Additional context for generation")
    style_guide: Optional[Dict] = Field(None, description="Style guide for code generation")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "Generate a Python function to calculate Fibonacci numbers",
                "task_type": "code_generation",
                "temperature": 0.7,
                "max_tokens": 2000,
                "context": {
                    "language": "python",
                    "version": "3.9"
                }
            }
        }

class ModelResponse(BaseModel):
    """
    Response model for generation endpoints
    """
    id: str = Field(..., description="Unique identifier for the response")
    result: str = Field(..., description="Generated content")
    cached: bool = Field(False, description="Whether the response was cached")
    metadata: Optional[Dict] = Field(None, description="Additional metadata about the generation")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "result": "def fibonacci(n: int) -> int:\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                "cached": False,
                "metadata": {
                    "model": "gpt-4",
                    "tokens": 150,
                    "duration_ms": 500
                }
            }
        }
