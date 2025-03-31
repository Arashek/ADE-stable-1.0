import asyncio
import logging
import psutil
import torch
from typing import Dict, Any, Optional
from datetime import datetime
from .client import TrainingChatClient

logger = logging.getLogger(__name__)

class ChatTrainer:
    def __init__(
        self,
        training_id: str,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        train_loader: Any,
        val_loader: Optional[Any] = None,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        server_url: str = "ws://localhost:8000"
    ):
        self.training_id = training_id
        self.model = model
        self.optimizer = optimizer
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.chat_client = TrainingChatClient(server_url)
        
        # Training state
        self.epoch = 0
        self.step = 0
        self.best_metric = float("-inf")
        self.is_paused = False
        self.should_stop = False
        
        # Register control handlers
        self.chat_client.register_handler("control", self._handle_control)
        
    async def start(self):
        """Start the training process with chat integration"""
        try:
            # Connect to chat server
            await self.chat_client.connect(self.training_id)
            await self.chat_client.update_status("initializing")
            
            # Move model to device
            self.model.to(self.device)
            
            # Training loop
            while not self.should_stop:
                if not self.is_paused:
                    await self._train_epoch()
                    if self.val_loader:
                        await self._validate()
                        
                # Report resources
                await self._report_resources()
                
                # Wait a bit to prevent overwhelming the server
                await asyncio.sleep(1)
                
            await self.chat_client.update_status("completed")
            
        except Exception as e:
            logger.error(f"Training error: {str(e)}")
            await self.chat_client.update_status("failed")
            raise
            
        finally:
            await self.chat_client.close()
            
    async def _train_epoch(self):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        
        await self.chat_client.update_status(f"training_epoch_{self.epoch}")
        
        for batch_idx, batch in enumerate(self.train_loader):
            if self.should_stop:
                break
                
            while self.is_paused:
                await asyncio.sleep(1)
                
            # Training step
            loss = await self._train_step(batch)
            total_loss += loss
            
            # Update metrics
            if batch_idx % 10 == 0:  # Report every 10 batches
                metrics = {
                    "epoch": self.epoch,
                    "step": self.step,
                    "loss": loss,
                    "avg_loss": total_loss / (batch_idx + 1)
                }
                await self.chat_client.update_metrics(metrics)
                
            self.step += 1
            
        self.epoch += 1
        
    async def _train_step(self, batch: Any) -> float:
        """Perform a single training step"""
        # Move batch to device
        batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                for k, v in batch.items()}
        
        # Forward pass
        outputs = self.model(**batch)
        loss = outputs.loss
        
        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
        
    async def _validate(self):
        """Run validation"""
        self.model.eval()
        total_loss = 0
        
        await self.chat_client.update_status(f"validating_epoch_{self.epoch}")
        
        with torch.no_grad():
            for batch in self.val_loader:
                batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                        for k, v in batch.items()}
                outputs = self.model(**batch)
                total_loss += outputs.loss.item()
                
        avg_loss = total_loss / len(self.val_loader)
        
        # Update metrics
        metrics = {
            "epoch": self.epoch,
            "val_loss": avg_loss
        }
        await self.chat_client.update_metrics(metrics)
        
        # Save checkpoint if best metric
        if avg_loss < self.best_metric:
            self.best_metric = avg_loss
            await self._save_checkpoint()
            
    async def _save_checkpoint(self):
        """Save a model checkpoint"""
        checkpoint = {
            "epoch": self.epoch,
            "step": self.step,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "best_metric": self.best_metric,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save checkpoint to disk
        checkpoint_path = f"checkpoints/{self.training_id}/epoch_{self.epoch}.pt"
        torch.save(checkpoint, checkpoint_path)
        
        # Report checkpoint
        await self.chat_client.report_checkpoint({
            "path": checkpoint_path,
            "epoch": self.epoch,
            "step": self.step,
            "metric": self.best_metric
        })
        
    async def _report_resources(self):
        """Report resource utilization"""
        resources = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "gpu_utilization": self._get_gpu_utilization(),
            "gpu_memory": self._get_gpu_memory()
        }
        await self.chat_client.report_resources(resources)
        
    def _get_gpu_utilization(self) -> Dict[str, float]:
        """Get GPU utilization"""
        if torch.cuda.is_available():
            return {
                f"gpu_{i}": torch.cuda.utilization(i)
                for i in range(torch.cuda.device_count())
            }
        return {}
        
    def _get_gpu_memory(self) -> Dict[str, float]:
        """Get GPU memory usage"""
        if torch.cuda.is_available():
            return {
                f"gpu_{i}": {
                    "allocated": torch.cuda.memory_allocated(i) / 1024**3,  # GB
                    "cached": torch.cuda.memory_reserved(i) / 1024**3  # GB
                }
                for i in range(torch.cuda.device_count())
            }
        return {}
        
    async def _handle_control(self, data: Dict[str, Any]):
        """Handle control commands from chat"""
        command = data.get("command", {})
        command_type = command.get("type")
        
        if command_type == "pause":
            self.is_paused = True
            await self.chat_client.update_status("paused")
            
        elif command_type == "resume":
            self.is_paused = False
            await self.chat_client.update_status("training")
            
        elif command_type == "stop":
            self.should_stop = True
            await self.chat_client.update_status("stopping")
            
        elif command_type == "update_hyperparameters":
            hyperparameters = command.get("hyperparameters", {})
            await self._update_hyperparameters(hyperparameters)
            
    async def _update_hyperparameters(self, hyperparameters: Dict[str, Any]):
        """Update training hyperparameters"""
        for param_group in self.optimizer.param_groups:
            for key, value in hyperparameters.items():
                if hasattr(param_group, key):
                    setattr(param_group, key, value)
                    
        await self.chat_client.update_metrics({
            "hyperparameters": hyperparameters
        }) 