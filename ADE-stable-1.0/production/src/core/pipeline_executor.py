import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import json
import yaml
import subprocess
import signal
import time
import docker
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from threading import Thread, Event, Lock

from .pipeline_config import PipelineConfig, BuildStage, ServiceConfig
from .pipeline_monitor import PipelineMonitor
from .pipeline_logger import PipelineLogger

logger = logging.getLogger(__name__)

@dataclass
class ExecutionState:
    """State of pipeline execution"""
    pipeline_name: str
    start_time: str
    status: str
    completed_stages: List[str] = field(default_factory=list)
    failed_stages: List[str] = field(default_factory=list)
    current_stage: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

class PipelineExecutor:
    """Executes pipeline stages and manages their lifecycle"""
    
    def __init__(self, working_dir: str = "workspace"):
        """Initialize the pipeline executor
        
        Args:
            working_dir: Directory for pipeline execution
        """
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {str(e)}")
            self.docker_client = None
            
        # Initialize components
        self.monitor = PipelineMonitor()
        self.logger = PipelineLogger()
        
        # Execution state
        self.state: Optional[ExecutionState] = None
        self.stop_event = Event()
        self.state_lock = Lock()
        
    def execute_pipeline(self, config: PipelineConfig) -> bool:
        """Execute a complete pipeline
        
        Args:
            config: Pipeline configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Initialize execution state
            self.state = ExecutionState(
                pipeline_name=config.name,
                start_time=datetime.now().isoformat(),
                status="running"
            )
            
            # Create pipeline workspace
            pipeline_dir = self.working_dir / config.name
            pipeline_dir.mkdir(parents=True, exist_ok=True)
            
            # Execute build stages
            for stage in config.build_stages:
                if self.stop_event.is_set():
                    self._update_state("stopped")
                    return False
                    
                if not self._execute_stage(stage, pipeline_dir):
                    self._update_state("failed", error=f"Stage {stage.name} failed")
                    return False
                    
                self._update_state(completed_stages=[stage.name])
                
            # Deploy services
            if not self._deploy_services(config.services):
                self._update_state("failed", error="Service deployment failed")
                return False
                
            self._update_state("completed")
            return True
            
        except Exception as e:
            self._update_state("failed", error=str(e))
            logger.error(f"Pipeline execution failed: {str(e)}")
            return False
            
    def _execute_stage(self, stage: BuildStage, pipeline_dir: Path) -> bool:
        """Execute a single build stage
        
        Args:
            stage: Build stage configuration
            pipeline_dir: Pipeline workspace directory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create stage workspace
            stage_dir = pipeline_dir / stage.name
            stage_dir.mkdir(parents=True, exist_ok=True)
            
            # Start monitoring
            self.monitor.start_monitoring(self.state.pipeline_name, stage.name)
            self.logger.start_logging(self.state.pipeline_name, stage.name)
            
            # Update state
            self._update_state(current_stage=stage.name)
            
            # Execute commands
            for attempt in range(stage.retries + 1):
                if self.stop_event.is_set():
                    return False
                    
                if self._execute_commands(stage.commands, stage_dir, stage.environment, stage.timeout):
                    break
                    
                if attempt < stage.retries:
                    self.logger.log("warning", f"Stage {stage.name} failed, retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return False
                    
            # Build Docker image if specified
            if stage.dockerfile:
                if not self._build_docker_image(stage.dockerfile, stage_dir):
                    return False
                    
            # Stop monitoring
            self.monitor.stop_monitoring(self.state.pipeline_name, stage.name)
            self.logger.save_logs()
            
            return True
            
        except Exception as e:
            self.logger.log("error", f"Stage execution failed: {str(e)}")
            return False
            
    def _execute_commands(self, commands: List[str], working_dir: Path, 
                         environment: Dict[str, str], timeout: int) -> bool:
        """Execute shell commands
        
        Args:
            commands: List of commands to execute
            working_dir: Working directory for commands
            environment: Environment variables
            timeout: Command timeout in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            for cmd in commands:
                if self.stop_event.is_set():
                    return False
                    
                self.logger.log("info", f"Executing command: {cmd}")
                
                # Prepare environment
                env = environment.copy()
                env.update({
                    "PATH": f"{working_dir}/bin:{env.get('PATH', '')}",
                    "PWD": str(working_dir)
                })
                
                # Execute command
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    cwd=working_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Monitor process
                start_time = time.time()
                while process.poll() is None:
                    if time.time() - start_time > timeout:
                        process.terminate()
                        self.logger.log("error", f"Command timed out after {timeout}s")
                        return False
                        
                    if self.stop_event.is_set():
                        process.terminate()
                        return False
                        
                    time.sleep(0.1)
                    
                # Check result
                if process.returncode != 0:
                    stdout, stderr = process.communicate()
                    self.logger.log("error", f"Command failed: {stderr}")
                    return False
                    
                stdout, stderr = process.communicate()
                if stdout:
                    self.logger.log("info", stdout)
                if stderr:
                    self.logger.log("warning", stderr)
                    
            return True
            
        except Exception as e:
            self.logger.log("error", f"Command execution failed: {str(e)}")
            return False
            
    def _build_docker_image(self, dockerfile: str, context_dir: Path) -> bool:
        """Build a Docker image
        
        Args:
            dockerfile: Path to Dockerfile
            context_dir: Build context directory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.docker_client:
                self.logger.log("error", "Docker client not available")
                return False
                
            self.logger.log("info", f"Building Docker image from {dockerfile}")
            
            # Build image
            image, build_logs = self.docker_client.images.build(
                path=str(context_dir),
                dockerfile=dockerfile,
                tag=f"{self.state.pipeline_name}-{self.state.current_stage}",
                decode=True
            )
            
            # Log build output
            for log in build_logs:
                if "stream" in log:
                    self.logger.log("info", log["stream"].strip())
                elif "error" in log:
                    self.logger.log("error", log["error"])
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.log("error", f"Docker build failed: {str(e)}")
            return False
            
    def _deploy_services(self, services: List[ServiceConfig]) -> bool:
        """Deploy pipeline services
        
        Args:
            services: List of service configurations
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.docker_client:
                self.logger.log("error", "Docker client not available")
                return False
                
            # Deploy services in dependency order
            deployed = set()
            while len(deployed) < len(services):
                for service in services:
                    if service.name in deployed:
                        continue
                        
                    # Check dependencies
                    if not all(dep in deployed for dep in service.depends_on):
                        continue
                        
                    # Deploy service
                    if not self._deploy_service(service):
                        return False
                        
                    deployed.add(service.name)
                    
            return True
            
        except Exception as e:
            self.logger.log("error", f"Service deployment failed: {str(e)}")
            return False
            
    def _deploy_service(self, service: ServiceConfig) -> bool:
        """Deploy a single service
        
        Args:
            service: Service configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.log("info", f"Deploying service: {service.name}")
            
            # Prepare container configuration
            container_config = {
                "image": service.image,
                "name": f"{self.state.pipeline_name}-{service.name}",
                "environment": service.environment,
                "ports": {f"{port['container']}/tcp": port['host'] for port in service.ports},
                "volumes": {volume["host"]: volume["container"] for volume in service.volumes},
                "mem_limit": service.resources.get("memory", "1g"),
                "cpu_count": service.resources.get("cpu", 1),
                "healthcheck": service.health_check,
                "detach": True
            }
            
            # Create and start container
            container = self.docker_client.containers.create(**container_config)
            container.start()
            
            # Wait for health check
            if not self._wait_for_health_check(container, service.health_check):
                container.remove(force=True)
                return False
                
            return True
            
        except Exception as e:
            self.logger.log("error", f"Service deployment failed: {str(e)}")
            return False
            
    def _wait_for_health_check(self, container, health_check: Dict) -> bool:
        """Wait for container health check
        
        Args:
            container: Docker container
            health_check: Health check configuration
            
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            timeout = health_check.get("timeout", 30)
            interval = health_check.get("interval", 5)
            retries = health_check.get("retries", 3)
            
            for _ in range(retries):
                if self.stop_event.is_set():
                    return False
                    
                result = container.exec_run(health_check["test"])
                if result.exit_code == 0:
                    return True
                    
                time.sleep(interval)
                
            return False
            
        except Exception as e:
            self.logger.log("error", f"Health check failed: {str(e)}")
            return False
            
    def stop_execution(self) -> bool:
        """Stop pipeline execution
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.stop_event.set()
            
            if self.state and self.state.current_stage:
                self.logger.log("info", f"Stopping pipeline execution at stage: {self.state.current_stage}")
                
            self._update_state("stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop pipeline execution: {str(e)}")
            return False
            
    def get_execution_state(self) -> Optional[ExecutionState]:
        """Get current execution state
        
        Returns:
            Optional[ExecutionState]: Current execution state if available
        """
        with self.state_lock:
            return self.state
            
    def _update_state(self, status: Optional[str] = None, 
                     completed_stages: Optional[List[str]] = None,
                     failed_stages: Optional[List[str]] = None,
                     current_stage: Optional[str] = None,
                     error: Optional[str] = None) -> None:
        """Update execution state
        
        Args:
            status: New status
            completed_stages: List of completed stages
            failed_stages: List of failed stages
            current_stage: Current stage name
            error: Error message
        """
        with self.state_lock:
            if status:
                self.state.status = status
            if completed_stages:
                self.state.completed_stages.extend(completed_stages)
            if failed_stages:
                self.state.failed_stages.extend(failed_stages)
            if current_stage:
                self.state.current_stage = current_stage
            if error:
                self.state.error = error
                
            # Save state to file
            state_file = self.working_dir / self.state.pipeline_name / "state.json"
            with open(state_file, 'w') as f:
                json.dump(self.state.__dict__, f, indent=4) 