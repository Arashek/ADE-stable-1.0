import asyncio
import json
import logging
import websockets
import psutil
import GPUtil
from typing import Dict, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.layout import Layout
from rich.text import Text

console = Console()

@dataclass
class TrainingMetrics:
    """Container for training metrics."""
    loss: float = 0.0
    accuracy: float = 0.0
    learning_rate: float = 0.0
    epoch: int = 0
    step: int = 0
    gpu_utilization: Dict[str, float] = None
    memory_usage: float = 0.0

class TrainingMonitor:
    def __init__(self, websocket_url: str = "ws://localhost:8765", token: str = None):
        self.websocket_url = websocket_url
        self.token = token
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.active_sessions: Dict[str, TrainingMetrics] = {}
        self.callbacks: Dict[str, Callable] = {}
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        handler = logging.FileHandler(log_dir / "training_monitor.log")
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logging.getLogger(__name__).addHandler(handler)
        logging.getLogger(__name__).setLevel(logging.INFO)

    async def connect(self):
        """Connect to the WebSocket server."""
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            if self.token:
                await self._authenticate()
            console.print("[green]Connected to training monitor server[/green]")
        except Exception as e:
            console.print(f"[red]Failed to connect to server: {str(e)}[/red]")
            raise

    async def _authenticate(self):
        """Authenticate with the server."""
        await self.websocket.send(json.dumps({
            "type": "auth",
            "token": self.token
        }))
        response = await self.websocket.recv()
        data = json.loads(response)
        if data.get("type") != "auth_success":
            raise Exception("Authentication failed")

    async def subscribe_to_session(self, session_id: str):
        """Subscribe to updates from a specific training session."""
        await self.websocket.send(json.dumps({
            "type": "subscribe",
            "session_id": session_id
        }))
        self.active_sessions[session_id] = TrainingMetrics()

    async def send_control_command(self, session_id: str, command: str, params: dict = None):
        """Send a control command to a training session."""
        await self.websocket.send(json.dumps({
            "type": "control_command",
            "session_id": session_id,
            "command": command,
            "params": params or {}
        }))

    def register_callback(self, event_type: str, callback: Callable):
        """Register a callback for specific event types."""
        self.callbacks[event_type] = callback

    async def start_monitoring(self):
        """Start monitoring training sessions."""
        try:
            while True:
                message = await self.websocket.recv()
                await self._handle_message(json.loads(message))
        except websockets.exceptions.ConnectionClosed:
            console.print("[red]Connection to server lost[/red]")
        except Exception as e:
            console.print(f"[red]Error in monitoring: {str(e)}[/red]")

    async def _handle_message(self, data: dict):
        """Handle incoming WebSocket messages."""
        message_type = data.get("type")
        session_id = data.get("session_id")
        
        if message_type == "training_update":
            await self._handle_training_update(session_id, data.get("data", {}))
        elif message_type == "control_update":
            await self._handle_control_update(session_id, data)
        elif message_type == "error":
            console.print(f"[red]Error: {data.get('message')}[/red]")
        
        # Call registered callback if exists
        if message_type in self.callbacks:
            await self.callbacks[message_type](data)

    async def _handle_training_update(self, session_id: str, data: dict):
        """Handle training progress updates."""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = TrainingMetrics()
        
        metrics = self.active_sessions[session_id]
        metrics.loss = data.get("metrics", {}).get("loss", metrics.loss)
        metrics.accuracy = data.get("metrics", {}).get("accuracy", metrics.accuracy)
        metrics.learning_rate = data.get("metrics", {}).get("learning_rate", metrics.learning_rate)
        metrics.epoch = data.get("metrics", {}).get("epoch", metrics.epoch)
        metrics.step = data.get("metrics", {}).get("step", metrics.step)
        metrics.gpu_utilization = data.get("gpu_utilization", {})
        metrics.memory_usage = data.get("memory_usage", 0.0)

    async def _handle_control_update(self, session_id: str, data: dict):
        """Handle control command updates."""
        command = data.get("command")
        status = data.get("status")
        
        if command == "stop":
            console.print(f"[yellow]Training session {session_id} is stopping...[/yellow]")
        elif command == "pause":
            console.print(f"[yellow]Training session {session_id} is paused[/yellow]")
        elif command == "resume":
            console.print(f"[green]Training session {session_id} has resumed[/green]")

    def get_session_metrics(self, session_id: str) -> Optional[TrainingMetrics]:
        """Get current metrics for a training session."""
        return self.active_sessions.get(session_id)

    def get_system_metrics(self) -> dict:
        """Get current system metrics."""
        metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "gpu_metrics": {}
        }
        
        try:
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                metrics["gpu_metrics"][f"gpu_{gpu.id}"] = {
                    "load": gpu.load * 100,
                    "memory_used": gpu.memoryUsed,
                    "memory_total": gpu.memoryTotal
                }
        except Exception as e:
            logging.warning(f"Failed to get GPU metrics: {str(e)}")
        
        return metrics

    def display_metrics(self):
        """Display current training metrics in a formatted table."""
        table = Table(title="Training Metrics")
        table.add_column("Session ID")
        table.add_column("Loss")
        table.add_column("Accuracy")
        table.add_column("Epoch")
        table.add_column("GPU Usage")
        table.add_column("Memory Usage")
        
        for session_id, metrics in self.active_sessions.items():
            gpu_usage = ", ".join([
                f"GPU {gpu_id}: {util:.1f}%"
                for gpu_id, util in metrics.gpu_utilization.items()
            ])
            
            table.add_row(
                session_id,
                f"{metrics.loss:.4f}",
                f"{metrics.accuracy:.2%}",
                str(metrics.epoch),
                gpu_usage,
                f"{metrics.memory_usage:.1f}%"
            )
        
        console.print(table)

    async def close(self):
        """Close the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            console.print("[yellow]Disconnected from training monitor server[/yellow]")

async def main():
    """Example usage of the TrainingMonitor."""
    monitor = TrainingMonitor()
    
    try:
        await monitor.connect()
        
        # Subscribe to a training session
        session_id = "example_session"
        await monitor.subscribe_to_session(session_id)
        
        # Register callbacks
        monitor.register_callback("training_update", lambda data: monitor.display_metrics())
        
        # Start monitoring
        await monitor.start_monitoring()
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
    finally:
        await monitor.close()

if __name__ == "__main__":
    asyncio.run(main()) 