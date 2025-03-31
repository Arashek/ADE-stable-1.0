from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, Dict
import time
import psutil
import logging
import json
from datetime import datetime
from src.core.models.tool_executor import ToolExecutor, ToolExecution
from src.core.models.llm_integration import LLMConfig
from src.core.models.code_context_manager import CodeContextManager
from src.core.security.command_validator import CommandValidator, ValidationResult, CommandCategory
from src.core.security.rate_limiter import RateLimiter
from src.core.logging.execution_logger import ExecutionLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["ai"])

# Security
api_key_header = APIKeyHeader(name="X-API-Key")
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
command_validator = CommandValidator()

class ExecutionRequest(BaseModel):
    command: str
    timeout: Optional[float] = 30.0
    env: Optional[Dict[str, str]] = None

class ExecutionResponse(BaseModel):
    stdout: str
    stderr: str
    exitCode: int
    executionTime: float
    resourceUsage: dict
    timestamp: str
    commandHash: str
    validation: Optional[Dict[str, str]] = None

# Initialize components
tool_executor = ToolExecutor(
    llm_config=LLMConfig(
        model="gpt-4",
        temperature=0.7,
        max_tokens=2000,
    ),
    context_manager=CodeContextManager()
)

execution_logger = ExecutionLogger()

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if not api_key or api_key != "your-secure-api-key":  # Replace with secure key management
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return api_key

async def check_rate_limit(request: Request):
    client_ip = request.client.host
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )
    return client_ip

@router.post("/execute", response_model=ExecutionResponse)
async def execute_command(
    request: Request,
    execution_request: ExecutionRequest,
    api_key: str = Depends(verify_api_key),
    client_ip: str = Depends(check_rate_limit)
):
    try:
        # Log request
        logger.info(f"Received execution request from {client_ip}")
        logger.debug(f"Command: {execution_request.command}")
        logger.debug(f"Environment: {execution_request.env}")

        # Validate command
        validation_result = command_validator.validate_command(execution_request.command)
        if not validation_result.is_safe:
            error_msg = f"Command validation failed: {validation_result.reason}"
            logger.warning(f"{error_msg} (Category: {validation_result.category.value})")
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )

        # Sanitize command
        sanitized_command = command_validator.sanitize_command(execution_request.command)
        if sanitized_command != execution_request.command:
            logger.info(f"Command sanitized: {execution_request.command} -> {sanitized_command}")

        # Create tool execution
        execution = ToolExecution(
            command=sanitized_command,
            args=[],  # Command is passed as a single string
            env=execution_request.env or {},
            cwd=".",  # Use current working directory
            timeout=execution_request.timeout,
            expected_output=None,
            expected_error=None,
            success_criteria={}
        )

        # Start timing and resource monitoring
        start_time = time.time()
        start_cpu = psutil.cpu_percent()
        start_memory = psutil.Process().memory_percent()

        # Execute the command
        result = await tool_executor.execute_tool(execution)

        # Calculate metrics
        execution_time = time.time() - start_time
        cpu_usage = psutil.cpu_percent() - start_cpu
        memory_usage = psutil.Process().memory_percent() - start_memory

        # Prepare response
        response = ExecutionResponse(
            stdout=result.output,
            stderr=result.error,
            exitCode=result.exit_code,
            executionTime=execution_time,
            resourceUsage={
                "cpu": cpu_usage,
                "memory": memory_usage
            },
            timestamp=datetime.utcnow().isoformat(),
            commandHash=command_validator.hash_command(sanitized_command),
            validation={
                "category": validation_result.category.value,
                "reason": validation_result.reason,
                "matched_pattern": validation_result.matched_pattern
            }
        )

        # Log execution results
        execution_logger.log_execution(
            command=sanitized_command,
            result=response.dict(),
            client_ip=client_ip,
            api_key=api_key
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        # Log error
        logger.error(f"Command execution failed: {str(e)}", exc_info=True)
        execution_logger.log_error(
            command=execution_request.command,
            error=str(e),
            client_ip=client_ip,
            api_key=api_key
        )
        raise HTTPException(
            status_code=500,
            detail=f"Command execution failed: {str(e)}"
        ) 