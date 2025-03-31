from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import numpy as np
from collections import defaultdict
import subprocess
import asyncio
import signal
import psutil
import shutil
import tempfile
import venv

from .llm_integration import LLMIntegration, LLMConfig
from .code_context_manager import CodeContextManager

logger = logging.getLogger(__name__)

@dataclass
class ToolExecution:
    command: str
    args: List[str]
    env: Dict[str, str]
    cwd: str
    timeout: float
    expected_output: Optional[str]
    expected_error: Optional[str]
    success_criteria: Dict[str, Any]
    created_at: datetime = datetime.now()
    metadata: Dict[str, Any] = None

@dataclass
class ExecutionResult:
    success: bool
    output: str
    error: str
    exit_code: int
    execution_time: float
    resource_usage: Dict[str, float]
    created_at: datetime = datetime.now()
    metadata: Dict[str, Any] = None

class ToolExecutor:
    def __init__(self, llm_config: LLMConfig, context_manager: CodeContextManager):
        self.llm = LLMIntegration(llm_config)
        self.context_manager = context_manager
        self.tool_patterns: Dict[str, List[Dict[str, Any]]] = self._load_patterns()
        self.recent_executions: Dict[str, List[ExecutionResult]] = defaultdict(list)
        self.active_processes: Dict[str, psutil.Process] = {}
        
    def _load_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load tool execution patterns from configuration"""
        patterns = defaultdict(list)
        try:
            pattern_file = Path("config/tool_patterns.json")
            if pattern_file.exists():
                with open(pattern_file) as f:
                    data = json.load(f)
                    for pattern_type, pattern_list in data.items():
                        patterns[pattern_type] = pattern_list
        except Exception as e:
            logger.error(f"Failed to load tool patterns: {e}")
        return patterns
        
    async def execute_tool(self, execution: ToolExecution) -> ExecutionResult:
        """Execute a tool or script"""
        try:
            # Create temporary directory if needed
            with tempfile.TemporaryDirectory() as temp_dir:
                # Set up environment
                env = self._setup_environment(execution.env, temp_dir)
                
                # Execute command
                process = await self._run_command(
                    execution.command,
                    execution.args,
                    env,
                    execution.cwd,
                    execution.timeout
                )
                
                # Collect results
                result = await self._collect_results(process)
                
                # Validate results
                self._validate_results(result, execution)
                
                # Store execution result
                self._store_execution_result(execution.command, result)
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to execute tool: {e}")
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                exit_code=1,
                execution_time=0.0,
                resource_usage={}
            )
            
    def _setup_environment(self, env: Dict[str, str], temp_dir: str) -> Dict[str, str]:
        """Set up execution environment"""
        try:
            # Create virtual environment if needed
            if "VIRTUAL_ENV" in env:
                venv_path = os.path.join(temp_dir, "venv")
                venv.create(venv_path, with_pip=True)
                env["VIRTUAL_ENV"] = venv_path
                
            # Set up PATH
            if "PATH" in env:
                env["PATH"] = f"{env.get('VIRTUAL_ENV', '')}/bin:{env['PATH']}"
                
            # Set up Python path if needed
            if "PYTHONPATH" in env:
                env["PYTHONPATH"] = f"{temp_dir}:{env['PYTHONPATH']}"
                
            return env
            
        except Exception as e:
            logger.error(f"Failed to set up environment: {e}")
            return env
            
    async def _run_command(self, command: str, args: List[str], env: Dict[str, str],
                          cwd: str, timeout: float) -> psutil.Process:
        """Run command and return process"""
        try:
            # Build command
            cmd = [command] + args
            
            # Create process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Store process
            self.active_processes[command] = process
            
            # Wait for completion with timeout
            try:
                await asyncio.wait_for(process.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                process.terminate()
                raise
                
            return process
            
        except Exception as e:
            logger.error(f"Failed to run command: {e}")
            raise
            
    async def _collect_results(self, process: psutil.Process) -> ExecutionResult:
        """Collect execution results"""
        try:
            # Get output and error
            stdout, stderr = await process.communicate()
            
            # Get resource usage
            usage = process.cpu_percent()
            memory = process.memory_percent()
            
            # Create result
            result = ExecutionResult(
                success=process.returncode == 0,
                output=stdout.decode() if stdout else "",
                error=stderr.decode() if stderr else "",
                exit_code=process.returncode,
                execution_time=process.cpu_times().user + process.cpu_times().system,
                resource_usage={
                    "cpu_percent": usage,
                    "memory_percent": memory
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to collect results: {e}")
            raise
            
    def _validate_results(self, result: ExecutionResult, execution: ToolExecution):
        """Validate execution results"""
        try:
            # Check expected output
            if execution.expected_output and execution.expected_output not in result.output:
                raise ValueError("Expected output not found")
                
            # Check expected error
            if execution.expected_error and execution.expected_error not in result.error:
                raise ValueError("Expected error not found")
                
            # Check success criteria
            for criterion, value in execution.success_criteria.items():
                if criterion == "exit_code" and result.exit_code != value:
                    raise ValueError(f"Exit code {result.exit_code} does not match expected {value}")
                elif criterion == "output_contains" and value not in result.output:
                    raise ValueError(f"Output does not contain expected text: {value}")
                elif criterion == "error_contains" and value not in result.error:
                    raise ValueError(f"Error does not contain expected text: {value}")
                    
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise
            
    def _store_execution_result(self, command: str, result: ExecutionResult):
        """Store execution result for future reference"""
        try:
            # Keep only the most recent 10 results
            self.recent_executions[command] = self.recent_executions.get(command, [])[:9]
            self.recent_executions[command].insert(0, result)
        except Exception as e:
            logger.error(f"Failed to store execution result: {e}")
            
    async def stop_process(self, command: str):
        """Stop a running process"""
        try:
            if command in self.active_processes:
                process = self.active_processes[command]
                process.terminate()
                await process.wait()
                del self.active_processes[command]
        except Exception as e:
            logger.error(f"Failed to stop process: {e}")
            
    async def cleanup(self):
        """Clean up resources"""
        try:
            # Stop all active processes
            for command in list(self.active_processes.keys()):
                await self.stop_process(command)
                
            # Clear recent executions
            self.recent_executions.clear()
            
        except Exception as e:
            logger.error(f"Failed to cleanup: {e}")
            
    def get_process_status(self, command: str) -> Optional[Dict[str, Any]]:
        """Get status of a running process"""
        try:
            if command in self.active_processes:
                process = self.active_processes[command]
                return {
                    "pid": process.pid,
                    "status": process.status(),
                    "cpu_percent": process.cpu_percent(),
                    "memory_percent": process.memory_percent(),
                    "create_time": datetime.fromtimestamp(process.create_time())
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get process status: {e}")
            return None 