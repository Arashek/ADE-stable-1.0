from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional, AsyncGenerator
import asyncio
import json
from datetime import datetime
from dataclasses import dataclass, asdict
import pty
import os
import fcntl
import termios
import struct
import signal
from ..security.command_validator import CommandValidator
from ..monitoring.resource_monitor import resource_monitor
import psutil

@dataclass
class TerminalSession:
    id: str
    pid: int
    fd: int
    ws: WebSocket
    created_at: str
    last_activity: str
    process_metrics: Optional[Dict] = None

class TerminalManager:
    def __init__(self):
        self.active_sessions: Dict[str, TerminalSession] = {}
        self.command_validator = CommandValidator()
        self.buffer_size = 1024
        self.metrics_interval = 5  # seconds

    async def create_terminal(self, websocket: WebSocket, session_id: str) -> TerminalSession:
        """Create a new terminal session."""
        # Fork a new process for the terminal
        pid, fd = pty.fork()
        
        if pid == 0:  # Child process
            # Execute shell
            os.execvp("bash", ["bash"])
        else:  # Parent process
            # Make the terminal non-blocking
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            
            # Create and store session
            now = datetime.utcnow().isoformat()
            session = TerminalSession(
                id=session_id,
                pid=pid,
                fd=fd,
                ws=websocket,
                created_at=now,
                last_activity=now
            )
            self.active_sessions[session_id] = session
            
            # Start metrics collection for this session
            asyncio.create_task(self._collect_session_metrics(session))
            
            return session

    async def _collect_session_metrics(self, session: TerminalSession):
        """Collect metrics for a specific terminal session."""
        try:
            process = psutil.Process(session.pid)
            while session.id in self.active_sessions:
                try:
                    metrics = {
                        "cpu_percent": process.cpu_percent(),
                        "memory_percent": process.memory_percent(),
                        "threads": process.num_threads(),
                        "open_files": len(process.open_files()),
                        "connections": len(process.connections())
                    }
                    
                    session.process_metrics = metrics
                    
                    # Send metrics to client
                    await session.ws.send_json({
                        "type": "metrics",
                        "data": {
                            "session_id": session.id,
                            "process": metrics,
                            "system": resource_monitor.collect_metrics(len(self.active_sessions)).__dict__
                        }
                    })
                    
                except psutil.NoSuchProcess:
                    break
                except Exception as e:
                    await session.ws.send_json({
                        "type": "error",
                        "data": f"Failed to collect metrics: {str(e)}"
                    })
                
                await asyncio.sleep(self.metrics_interval)
                
        except Exception as e:
            await session.ws.send_json({
                "type": "error",
                "data": f"Metrics collection error: {str(e)}"
            })

    async def handle_terminal_input(self, session: TerminalSession, data: str) -> None:
        """Handle input from the client to the terminal."""
        try:
            # Validate command if it ends with newline (command execution)
            if data.endswith('\n'):
                command = data.strip()
                validation_result = self.command_validator.validate_command(command)
                if not validation_result.is_safe:
                    error_msg = f"Command validation failed: {validation_result.reason}"
                    await session.ws.send_text(json.dumps({
                        "type": "error",
                        "data": error_msg
                    }))
                    return

                # Sanitize command
                command = self.command_validator.sanitize_command(command)
                data = command + '\n'

            # Write to terminal
            os.write(session.fd, data.encode())
            session.last_activity = datetime.utcnow().isoformat()
            
        except Exception as e:
            await session.ws.send_text(json.dumps({
                "type": "error",
                "data": f"Failed to write to terminal: {str(e)}"
            }))

    async def read_terminal_output(self, session: TerminalSession) -> AsyncGenerator[str, None]:
        """Read output from the terminal."""
        while True:
            try:
                output = os.read(session.fd, self.buffer_size)
                if output:
                    yield output.decode()
                session.last_activity = datetime.utcnow().isoformat()
            except BlockingIOError:
                await asyncio.sleep(0.1)
            except Exception as e:
                yield json.dumps({
                    "type": "error",
                    "data": f"Failed to read from terminal: {str(e)}"
                })
                break

    async def resize_terminal(self, session: TerminalSession, rows: int, cols: int) -> None:
        """Resize the terminal."""
        try:
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(session.fd, termios.TIOCSWINSZ, winsize)
        except Exception as e:
            await session.ws.send_text(json.dumps({
                "type": "error",
                "data": f"Failed to resize terminal: {str(e)}"
            }))

    async def close_terminal(self, session_id: str) -> None:
        """Close a terminal session."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            try:
                # Send SIGTERM to the process group
                os.killpg(os.getpgid(session.pid), signal.SIGTERM)
            except:
                pass
            
            try:
                # Close the file descriptor
                os.close(session.fd)
            except:
                pass
            
            # Remove session from active sessions
            del self.active_sessions[session_id]

    def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get a terminal session by ID."""
        return self.active_sessions.get(session_id)

    def get_system_metrics(self) -> Dict:
        """Get current system metrics."""
        return resource_monitor.get_metrics_summary()

terminal_manager = TerminalManager() 