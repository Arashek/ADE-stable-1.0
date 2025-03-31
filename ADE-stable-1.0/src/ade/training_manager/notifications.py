import asyncio
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

@dataclass
class NotificationConfig:
    """Configuration for notification settings."""
    email_enabled: bool = False
    email_smtp_server: str = ""
    email_smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_recipients: List[str] = None
    slack_enabled: bool = False
    slack_webhook_url: str = ""
    slack_channel: str = ""
    console_enabled: bool = True
    log_file: str = "logs/notifications.log"

class NotificationManager:
    def __init__(self, config: Optional[NotificationConfig] = None):
        self.config = config or NotificationConfig()
        self._setup_logging()
        self.callbacks: Dict[str, List[Callable]] = {}
        self.milestone_thresholds = {
            "accuracy": [0.5, 0.7, 0.8, 0.9, 0.95],
            "loss": [0.5, 0.3, 0.2, 0.1, 0.05]
        }
        self.reached_milestones: Dict[str, set] = {}

    def _setup_logging(self):
        """Setup logging configuration."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        handler = logging.FileHandler(self.config.log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logging.getLogger(__name__).addHandler(handler)
        logging.getLogger(__name__).setLevel(logging.INFO)

    def register_callback(self, event_type: str, callback: Callable):
        """Register a callback for specific event types."""
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)

    async def notify(self, event_type: str, message: str, data: dict = None):
        """Send notification for an event."""
        # Log the notification
        logging.info(f"{event_type}: {message}")
        
        # Call registered callbacks
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    await callback(event_type, message, data)
                except Exception as e:
                    logging.error(f"Error in callback: {str(e)}")
        
        # Send notifications based on configuration
        if self.config.console_enabled:
            self._console_notify(event_type, message, data)
        
        if self.config.email_enabled:
            await self._email_notify(event_type, message, data)
        
        if self.config.slack_enabled:
            await self._slack_notify(event_type, message, data)

    def _console_notify(self, event_type: str, message: str, data: dict = None):
        """Display notification in console."""
        color = {
            "error": "red",
            "warning": "yellow",
            "success": "green",
            "info": "blue",
            "milestone": "cyan"
        }.get(event_type, "white")
        
        panel = Panel(
            f"[{color}]{message}[/{color}]",
            title=f"[bold]{event_type.upper()}[/bold]",
            border_style=color
        )
        
        if data:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Key")
            table.add_column("Value")
            
            for key, value in data.items():
                table.add_row(str(key), str(value))
            
            console.print(panel)
            console.print(table)
        else:
            console.print(panel)

    async def _email_notify(self, event_type: str, message: str, data: dict = None):
        """Send email notification."""
        if not self.config.email_recipients:
            return
        
        try:
            msg = MIMEMultipart()
            msg["Subject"] = f"Training {event_type}: {message}"
            msg["From"] = self.config.email_username
            msg["To"] = ", ".join(self.config.email_recipients)
            
            body = f"""
            Event Type: {event_type}
            Message: {message}
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            if data:
                body += "\nDetails:\n"
                for key, value in data.items():
                    body += f"{key}: {value}\n"
            
            msg.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(self.config.email_smtp_server, self.config.email_smtp_port) as server:
                server.starttls()
                server.login(self.config.email_username, self.config.email_password)
                server.send_message(msg)
            
            logging.info(f"Email notification sent for {event_type}")
        
        except Exception as e:
            logging.error(f"Failed to send email notification: {str(e)}")

    async def _slack_notify(self, event_type: str, message: str, data: dict = None):
        """Send Slack notification."""
        # TODO: Implement Slack notifications
        pass

    async def check_milestones(self, session_id: str, metrics: dict):
        """Check if any milestones have been reached."""
        if session_id not in self.reached_milestones:
            self.reached_milestones[session_id] = set()
        
        for metric, thresholds in self.milestone_thresholds.items():
            if metric in metrics:
                value = metrics[metric]
                for threshold in thresholds:
                    milestone_key = f"{metric}_{threshold}"
                    if (metric == "accuracy" and value >= threshold) or \
                       (metric == "loss" and value <= threshold):
                        if milestone_key not in self.reached_milestones[session_id]:
                            self.reached_milestones[session_id].add(milestone_key)
                            await self.notify(
                                "milestone",
                                f"Reached {metric} milestone: {threshold}",
                                {"session_id": session_id, "metric": metric, "value": value}
                            )

    async def notify_error(self, session_id: str, error: Exception, context: dict = None):
        """Send error notification with suggested fixes."""
        error_data = {
            "session_id": session_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggested_fixes": self._get_suggested_fixes(error)
        }
        
        if context:
            error_data.update(context)
        
        await self.notify("error", f"Training error in session {session_id}", error_data)

    def _get_suggested_fixes(self, error: Exception) -> List[str]:
        """Get suggested fixes for common errors."""
        error_type = type(error).__name__
        fixes = {
            "CUDAOutOfMemoryError": [
                "Reduce batch size",
                "Enable gradient checkpointing",
                "Use mixed precision training",
                "Free up GPU memory"
            ],
            "ValueError": [
                "Check input data format",
                "Verify hyperparameters",
                "Validate model configuration"
            ],
            "RuntimeError": [
                "Check model architecture",
                "Verify tensor shapes",
                "Inspect data pipeline"
            ]
        }
        
        return fixes.get(error_type, ["Check logs for more details"])

    async def notify_completion(self, session_id: str, metrics: dict, duration: float):
        """Send training completion notification."""
        completion_data = {
            "session_id": session_id,
            "final_metrics": metrics,
            "training_duration": f"{duration:.2f} seconds",
            "completion_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        await self.notify(
            "success",
            f"Training completed for session {session_id}",
            completion_data
        )

    async def notify_progress(self, session_id: str, epoch: int, total_epochs: int, metrics: dict):
        """Send training progress update."""
        progress = (epoch / total_epochs) * 100
        progress_data = {
            "session_id": session_id,
            "epoch": epoch,
            "total_epochs": total_epochs,
            "progress": f"{progress:.1f}%",
            "current_metrics": metrics
        }
        
        await self.notify(
            "info",
            f"Training progress update for session {session_id}",
            progress_data
        )

async def main():
    """Example usage of the NotificationManager."""
    config = NotificationConfig(
        email_enabled=True,
        email_smtp_server="smtp.gmail.com",
        email_username="your-email@gmail.com",
        email_password="your-app-password",
        email_recipients=["recipient@example.com"],
        console_enabled=True
    )
    
    manager = NotificationManager(config)
    
    # Example notifications
    await manager.notify(
        "info",
        "Starting training session",
        {"session_id": "test_session", "model": "transformer"}
    )
    
    await manager.notify(
        "milestone",
        "Reached accuracy milestone",
        {"session_id": "test_session", "accuracy": 0.95}
    )
    
    await manager.notify_error(
        "test_session",
        Exception("CUDA out of memory"),
        {"batch_size": 32, "gpu_memory": "8GB"}
    )

if __name__ == "__main__":
    asyncio.run(main()) 