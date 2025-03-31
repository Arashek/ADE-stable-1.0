import asyncio
import json
import websockets
from typing import Dict, Set
import subprocess
import os
import pty
import termios
import fcntl
import struct
import signal
import logging

logger = logging.getLogger(__name__)

class TerminalHandler:
    def __init__(self):
        self.connections: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        self.processes: Dict[str, subprocess.Popen] = {}

    async def handle_connection(self, websocket: websockets.WebSocketServerProtocol, project_id: str):
        if project_id not in self.connections:
            self.connections[project_id] = set()
        self.connections[project_id].add(websocket)

        try:
            # Create a pseudo-terminal
            master_fd, slave_fd = pty.openpty()
            
            # Configure the terminal
            attrs = termios.tcgetattr(slave_fd)
            attrs[0] = attrs[0] & ~termios.IGNBRK & ~termios.BRKINT & ~termios.PARMRK & ~termios.ISTRIP & ~termios.INLCR & ~termios.IGNCR & ~termios.ICRNL & ~termios.IXON
            attrs[1] = attrs[1] & ~termios.OPOST
            attrs[2] = attrs[2] & ~termios.CSIZE & ~termios.PARENB
            attrs[3] = attrs[3] & ~termios.ECHO & ~termios.ECHONL & ~termios.ICANON & ~termios.ISIG & ~termios.IEXTEN
            termios.tcsetattr(slave_fd, termios.TCSANOW, attrs)

            # Start the shell process
            env = os.environ.copy()
            env['TERM'] = 'xterm-256color'
            env['COLORTERM'] = 'truecolor'
            
            process = subprocess.Popen(
                ['/bin/bash'],
                stdin=subprocess.PIPE,
                stdout=slave_fd,
                stderr=slave_fd,
                start_new_session=True,
                env=env
            )
            
            self.processes[project_id] = process

            # Set up non-blocking I/O
            fcntl.fcntl(master_fd, fcntl.F_SETFL, os.O_NONBLOCK)

            # Start tasks for reading and writing
            read_task = asyncio.create_task(self._read_from_terminal(master_fd, websocket))
            write_task = asyncio.create_task(self._write_to_terminal(websocket, process))

            # Wait for tasks to complete
            await asyncio.gather(read_task, write_task)

        except Exception as e:
            logger.error(f"Error in terminal connection: {str(e)}")
        finally:
            self._cleanup(project_id, websocket)

    async def _read_from_terminal(self, master_fd: int, websocket: websockets.WebSocketServerProtocol):
        try:
            while True:
                try:
                    data = os.read(master_fd, 1024)
                    if not data:
                        break
                    await websocket.send(data.decode())
                except BlockingIOError:
                    await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error reading from terminal: {str(e)}")

    async def _write_to_terminal(self, websocket: websockets.WebSocketServerProtocol, process: subprocess.Popen):
        try:
            async for message in websocket:
                if process.stdin:
                    process.stdin.write(message.encode())
        except Exception as e:
            logger.error(f"Error writing to terminal: {str(e)}")

    def _cleanup(self, project_id: str, websocket: websockets.WebSocketServerProtocol):
        if project_id in self.connections:
            self.connections[project_id].remove(websocket)
            if not self.connections[project_id]:
                del self.connections[project_id]
                if project_id in self.processes:
                    process = self.processes[project_id]
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    del self.processes[project_id]

    async def execute_command(self, project_id: str, command: str) -> dict:
        if project_id not in self.processes:
            return {"error": "No active terminal session"}
        
        process = self.processes[project_id]
        try:
            if process.stdin:
                process.stdin.write(f"{command}\n".encode())
            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)} 