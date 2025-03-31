import asyncio
import json
import logging
import uuid
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime
from .websocket_server import TrainingWebSocketServer, TrainingSession
from .training_monitor import TrainingMonitor
from .notifications import NotificationManager, NotificationConfig

logger = logging.getLogger(__name__)

class TrainingProcessManager:
    def __init__(self, config_path: str = "config/training_config.json"):
        self.config_path = config_path
        self.websocket_server = TrainingWebSocketServer()
        self.monitor = TrainingMonitor()
        self.notification_manager = NotificationManager()
        self.active_processes: Dict[str, asyncio.Task] = {}
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        handler = logging.FileHandler(log_dir / "process_manager.log")
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    async def start(self):
        """Start the training process manager."""
        try:
            # Start WebSocket server
            server_task = asyncio.create_task(self.websocket_server.start())
            
            # Connect monitor to server
            await self.monitor.connect()
            
            # Register callbacks
            self._register_callbacks()
            
            # Start monitoring
            monitor_task = asyncio.create_task(self.monitor.start_monitoring())
            
            # Wait for tasks
            await asyncio.gather(server_task, monitor_task)
            
        except Exception as e:
            logger.error(f"Error starting process manager: {str(e)}")
            raise

    def _register_callbacks(self):
        """Register callbacks for various events."""
        # Monitor callbacks
        self.monitor.register_callback("training_update", self._handle_training_update)
        self.monitor.register_callback("control_update", self._handle_control_update)
        
        # Notification callbacks
        self.notification_manager.register_callback("error", self._handle_error)
        self.notification_manager.register_callback("milestone", self._handle_milestone)

    async def start_training(self, model_name: str, hyperparameters: dict) -> str:
        """Start a new training process."""
        session_id = str(uuid.uuid4())
        
        try:
            # Create training session
            session = self.websocket_server.create_training_session(
                session_id, model_name, hyperparameters
            )
            
            # Subscribe monitor to session
            await self.monitor.subscribe_to_session(session_id)
            
            # Start training process
            process_task = asyncio.create_task(
                self._run_training_process(session_id, model_name, hyperparameters)
            )
            self.active_processes[session_id] = process_task
            
            # Notify start
            await self.notification_manager.notify(
                "info",
                f"Starting training for model {model_name}",
                {"session_id": session_id, "model": model_name}
            )
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting training: {str(e)}")
            await self.notification_manager.notify_error(session_id, e)
            raise

    async def _run_training_process(self, session_id: str, model_name: str, hyperparameters: dict):
        """Run the training process."""
        start_time = datetime.now()
        
        try:
            # TODO: Implement actual training process
            # This is a placeholder that simulates training
            for epoch in range(hyperparameters.get("num_epochs", 10)):
                # Simulate training progress
                metrics = {
                    "loss": 1.0 - (epoch * 0.1),
                    "accuracy": 0.0 + (epoch * 0.1),
                    "learning_rate": hyperparameters.get("learning_rate", 0.001)
                }
                
                # Update session
                await self._update_session(session_id, epoch, metrics)
                
                # Check milestones
                await self.notification_manager.check_milestones(session_id, metrics)
                
                # Simulate training time
                await asyncio.sleep(1)
            
            # Training completed
            duration = (datetime.now() - start_time).total_seconds()
            await self.notification_manager.notify_completion(session_id, metrics, duration)
            
        except Exception as e:
            logger.error(f"Error in training process: {str(e)}")
            await self.notification_manager.notify_error(session_id, e)
            raise
        finally:
            # Cleanup
            if session_id in self.active_processes:
                del self.active_processes[session_id]

    async def _update_session(self, session_id: str, epoch: int, metrics: dict):
        """Update training session with new metrics."""
        session = self.websocket_server.get_session(session_id)
        if not session:
            return
        
        session.metrics.update(metrics)
        session.metrics["epoch"] = epoch
        
        # Get system metrics
        system_metrics = self.monitor.get_system_metrics()
        session.gpu_utilization = system_metrics.get("gpu_metrics", {})
        
        # Send update through WebSocket
        await self.websocket_server._broadcast_to_session(session_id, {
            "type": "training_update",
            "session_id": session_id,
            "data": {
                "metrics": session.metrics,
                "gpu_utilization": session.gpu_utilization
            }
        })

    async def stop_training(self, session_id: str):
        """Stop a training process."""
        if session_id not in self.active_processes:
            return
        
        try:
            # Send stop command
            await self.monitor.send_control_command(session_id, "stop")
            
            # Cancel process
            self.active_processes[session_id].cancel()
            
            # Wait for process to finish
            try:
                await self.active_processes[session_id]
            except asyncio.CancelledError:
                pass
            
            # Cleanup
            del self.active_processes[session_id]
            
            # Notify
            await self.notification_manager.notify(
                "info",
                f"Training stopped for session {session_id}",
                {"session_id": session_id}
            )
            
        except Exception as e:
            logger.error(f"Error stopping training: {str(e)}")
            await self.notification_manager.notify_error(session_id, e)
            raise

    async def pause_training(self, session_id: str):
        """Pause a training process."""
        if session_id not in self.active_processes:
            return
        
        try:
            await self.monitor.send_control_command(session_id, "pause")
            await self.notification_manager.notify(
                "info",
                f"Training paused for session {session_id}",
                {"session_id": session_id}
            )
        except Exception as e:
            logger.error(f"Error pausing training: {str(e)}")
            await self.notification_manager.notify_error(session_id, e)
            raise

    async def resume_training(self, session_id: str):
        """Resume a paused training process."""
        if session_id not in self.active_processes:
            return
        
        try:
            await self.monitor.send_control_command(session_id, "resume")
            await self.notification_manager.notify(
                "info",
                f"Training resumed for session {session_id}",
                {"session_id": session_id}
            )
        except Exception as e:
            logger.error(f"Error resuming training: {str(e)}")
            await self.notification_manager.notify_error(session_id, e)
            raise

    async def update_hyperparameters(self, session_id: str, hyperparameters: dict):
        """Update hyperparameters during training."""
        if session_id not in self.active_processes:
            return
        
        try:
            await self.monitor.send_control_command(
                session_id,
                "update_hyperparameters",
                hyperparameters
            )
            await self.notification_manager.notify(
                "info",
                f"Updated hyperparameters for session {session_id}",
                {"session_id": session_id, "hyperparameters": hyperparameters}
            )
        except Exception as e:
            logger.error(f"Error updating hyperparameters: {str(e)}")
            await self.notification_manager.notify_error(session_id, e)
            raise

    async def _handle_training_update(self, data: dict):
        """Handle training update from monitor."""
        session_id = data.get("session_id")
        if not session_id:
            return
        
        metrics = data.get("data", {}).get("metrics", {})
        await self.notification_manager.check_milestones(session_id, metrics)

    async def _handle_control_update(self, data: dict):
        """Handle control update from monitor."""
        session_id = data.get("session_id")
        command = data.get("command")
        
        if not session_id:
            return
        
        if command == "stop":
            await self.notification_manager.notify(
                "warning",
                f"Training stopped for session {session_id}",
                {"session_id": session_id}
            )
        elif command == "pause":
            await self.notification_manager.notify(
                "warning",
                f"Training paused for session {session_id}",
                {"session_id": session_id}
            )
        elif command == "resume":
            await self.notification_manager.notify(
                "info",
                f"Training resumed for session {session_id}",
                {"session_id": session_id}
            )

    async def _handle_error(self, event_type: str, message: str, data: dict):
        """Handle error notifications."""
        session_id = data.get("session_id")
        if not session_id:
            return
        
        logger.error(f"Error in session {session_id}: {message}")
        # Additional error handling logic here

    async def _handle_milestone(self, event_type: str, message: str, data: dict):
        """Handle milestone notifications."""
        session_id = data.get("session_id")
        if not session_id:
            return
        
        logger.info(f"Milestone reached in session {session_id}: {message}")
        # Additional milestone handling logic here

    async def close(self):
        """Close all connections and cleanup."""
        # Stop all training processes
        for session_id in list(self.active_processes.keys()):
            await self.stop_training(session_id)
        
        # Close monitor connection
        await self.monitor.close()

async def main():
    """Example usage of the TrainingProcessManager."""
    manager = TrainingProcessManager()
    
    try:
        # Start the manager
        await manager.start()
        
        # Start a training process
        hyperparameters = {
            "num_epochs": 10,
            "learning_rate": 0.001,
            "batch_size": 32
        }
        
        session_id = await manager.start_training("test_model", hyperparameters)
        
        # Wait for a while
        await asyncio.sleep(5)
        
        # Pause training
        await manager.pause_training(session_id)
        
        # Wait some more
        await asyncio.sleep(2)
        
        # Resume training
        await manager.resume_training(session_id)
        
        # Wait for completion
        await asyncio.sleep(10)
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
    finally:
        await manager.close()

if __name__ == "__main__":
    asyncio.run(main()) 