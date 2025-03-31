import asyncio
import logging
import uuid
from typing import Dict, Optional, List, Any
from datetime import datetime
import docker
from docker.errors import DockerException
import psutil
import json
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TerminalSessionStatus(Enum):
    """Terminal session status"""
    CREATING = "creating"
    ACTIVE = "active"
    PAUSED = "paused"
    TERMINATED = "terminated"
    ERROR = "error"

@dataclass
class TerminalSession:
    """Represents a terminal session"""
    id: str
    user_id: str
    container_id: Optional[str]
    status: TerminalSessionStatus
    created_at: datetime
    last_active: datetime
    command_history: List[str]
    resource_usage: Dict[str, float]
    environment_vars: Dict[str, str]
    workspace_path: str
    max_memory: int
    max_cpu: float
    idle_timeout: int

class TerminalService:
    """Manages terminal sessions and container execution"""
    
    def __init__(
        self,
        docker_client: Optional[docker.DockerClient] = None,
        base_workspace_path: str = "/workspace",
        default_max_memory: int = 1024 * 1024 * 1024,  # 1GB
        default_max_cpu: float = 1.0,
        default_idle_timeout: int = 3600  # 1 hour
    ):
        """Initialize terminal service
        
        Args:
            docker_client: Docker client instance
            base_workspace_path: Base path for workspace directories
            default_max_memory: Default memory limit in bytes
            default_max_cpu: Default CPU limit (0.0-1.0)
            default_idle_timeout: Default idle timeout in seconds
        """
        self.docker_client = docker_client or docker.from_env()
        self.base_workspace_path = base_workspace_path
        self.default_max_memory = default_max_memory
        self.default_max_cpu = default_max_cpu
        self.default_idle_timeout = default_idle_timeout
        
        # Active sessions
        self.sessions: Dict[str, TerminalSession] = {}
        
        # Resource monitoring
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
        # Command restrictions
        self.command_whitelist = set()
        self.command_blacklist = set()
        self.load_command_restrictions()
        
    def load_command_restrictions(self):
        """Load command whitelist and blacklist from configuration"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config", "command_restrictions.json")
            with open(config_path, "r") as f:
                config = json.load(f)
                self.command_whitelist = set(config.get("whitelist", []))
                self.command_blacklist = set(config.get("blacklist", []))
        except Exception as e:
            logger.error(f"Failed to load command restrictions: {str(e)}")
            
    async def create_session(
        self,
        user_id: str,
        workspace_path: Optional[str] = None,
        max_memory: Optional[int] = None,
        max_cpu: Optional[float] = None,
        idle_timeout: Optional[int] = None,
        environment_vars: Optional[Dict[str, str]] = None
    ) -> TerminalSession:
        """Create a new terminal session
        
        Args:
            user_id: User ID
            workspace_path: Custom workspace path
            max_memory: Memory limit in bytes
            max_cpu: CPU limit (0.0-1.0)
            idle_timeout: Idle timeout in seconds
            environment_vars: Environment variables
            
        Returns:
            Created terminal session
        """
        try:
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Create workspace directory
            workspace_dir = workspace_path or os.path.join(
                self.base_workspace_path,
                user_id,
                session_id
            )
            os.makedirs(workspace_dir, exist_ok=True)
            
            # Create container
            container = self.docker_client.containers.run(
                "ubuntu:latest",
                command="/bin/bash",
                detach=True,
                tty=True,
                stdin_open=True,
                volumes={
                    workspace_dir: {
                        "bind": "/workspace",
                        "mode": "rw"
                    }
                },
                environment=environment_vars or {},
                mem_limit=max_memory or self.default_max_memory,
                cpu_period=100000,
                cpu_quota=int((max_cpu or self.default_max_cpu) * 100000),
                network_disabled=True,
                security_opt=["no-new-privileges"],
                cap_drop=["ALL"]
            )
            
            # Create session
            session = TerminalSession(
                id=session_id,
                user_id=user_id,
                container_id=container.id,
                status=TerminalSessionStatus.ACTIVE,
                created_at=datetime.utcnow(),
                last_active=datetime.utcnow(),
                command_history=[],
                resource_usage={},
                environment_vars=environment_vars or {},
                workspace_path=workspace_dir,
                max_memory=max_memory or self.default_max_memory,
                max_cpu=max_cpu or self.default_max_cpu,
                idle_timeout=idle_timeout or self.default_idle_timeout
            )
            
            # Store session
            self.sessions[session_id] = session
            
            # Start resource monitoring
            self.monitoring_tasks[session_id] = asyncio.create_task(
                self._monitor_session_resources(session_id)
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create terminal session: {str(e)}")
            raise
            
    async def execute_command(
        self,
        session_id: str,
        command: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Execute command in terminal session
        
        Args:
            session_id: Session ID
            command: Command to execute
            user_id: User ID
            
        Returns:
            Command execution result
        """
        try:
            # Get session
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")
                
            # Check permissions
            if session.user_id != user_id:
                raise PermissionError("User does not have permission to execute commands in this session")
                
            # Validate command
            if not self._validate_command(command):
                raise ValueError("Command is not allowed")
                
            # Get container
            container = self.docker_client.containers.get(session.container_id)
            
            # Execute command
            exec_result = container.exec_run(
                command,
                stdin=True,
                stdout=True,
                stderr=True,
                tty=True,
                stream=True
            )
            
            # Update session
            session.last_active = datetime.utcnow()
            session.command_history.append(command)
            
            # Log command
            self._log_command(session_id, command, user_id)
            
            return {
                "session_id": session_id,
                "command": command,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"Failed to execute command: {str(e)}")
            raise
            
    async def terminate_session(self, session_id: str, user_id: str) -> None:
        """Terminate terminal session
        
        Args:
            session_id: Session ID
            user_id: User ID
        """
        try:
            # Get session
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")
                
            # Check permissions
            if session.user_id != user_id:
                raise PermissionError("User does not have permission to terminate this session")
                
            # Stop monitoring
            if session_id in self.monitoring_tasks:
                self.monitoring_tasks[session_id].cancel()
                del self.monitoring_tasks[session_id]
                
            # Stop container
            container = self.docker_client.containers.get(session.container_id)
            container.stop()
            container.remove()
            
            # Update session
            session.status = TerminalSessionStatus.TERMINATED
            
            # Clean up
            del self.sessions[session_id]
            
        except Exception as e:
            logger.error(f"Failed to terminate session: {str(e)}")
            raise
            
    async def _monitor_session_resources(self, session_id: str) -> None:
        """Monitor session resource usage
        
        Args:
            session_id: Session ID
        """
        try:
            session = self.sessions[session_id]
            container = self.docker_client.containers.get(session.container_id)
            
            while True:
                # Get container stats
                stats = container.stats(stream=False)
                
                # Calculate CPU usage
                cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                           stats["precpu_stats"]["cpu_usage"]["total_usage"]
                system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                             stats["precpu_stats"]["system_cpu_usage"]
                cpu_usage = (cpu_delta / system_delta) * 100.0
                
                # Get memory usage
                memory_usage = stats["memory_stats"]["usage"]
                
                # Update session
                session.resource_usage = {
                    "cpu": cpu_usage,
                    "memory": memory_usage
                }
                
                # Check limits
                if memory_usage > session.max_memory:
                    logger.warning(f"Session {session_id} exceeded memory limit")
                    await self.terminate_session(session_id, session.user_id)
                    
                if cpu_usage > session.max_cpu * 100:
                    logger.warning(f"Session {session_id} exceeded CPU limit")
                    await self.terminate_session(session_id, session.user_id)
                    
                # Check idle timeout
                idle_time = (datetime.utcnow() - session.last_active).total_seconds()
                if idle_time > session.idle_timeout:
                    logger.warning(f"Session {session_id} timed out")
                    await self.terminate_session(session_id, session.user_id)
                    
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Failed to monitor session resources: {str(e)}")
            
    def _validate_command(self, command: str) -> bool:
        """Validate command against whitelist and blacklist
        
        Args:
            command: Command to validate
            
        Returns:
            Whether command is allowed
        """
        # Check blacklist first
        if any(cmd in command.lower() for cmd in self.command_blacklist):
            return False
            
        # If whitelist is empty, allow all non-blacklisted commands
        if not self.command_whitelist:
            return True
            
        # Check whitelist
        return any(cmd in command.lower() for cmd in self.command_whitelist)
        
    def _log_command(self, session_id: str, command: str, user_id: str) -> None:
        """Log command execution
        
        Args:
            session_id: Session ID
            command: Command executed
            user_id: User ID
        """
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id,
                "user_id": user_id,
                "command": command
            }
            
            log_path = os.path.join(
                os.path.dirname(__file__),
                "logs",
                "command_history.log"
            )
            
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            
            with open(log_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            logger.error(f"Failed to log command: {str(e)}") 