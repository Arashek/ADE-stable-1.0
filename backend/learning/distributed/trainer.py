import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler
from typing import Dict, Any, List, Optional
import os
from pathlib import Path
import json
from datetime import datetime
from ...config.logging_config import logger

class DistributedTrainer:
    """Manages distributed training across multiple nodes"""
    
    def __init__(self, 
                 model: torch.nn.Module,
                 optimizer: torch.optim.Optimizer,
                 train_dataset: torch.utils.data.Dataset,
                 config: Dict[str, Any],
                 output_dir: str):
        self.model = model
        self.optimizer = optimizer
        self.train_dataset = train_dataset
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize distributed training
        self._init_distributed()
        
        # Initialize model parallelism if enabled
        if self.config.get('use_model_parallel', False):
            self._init_model_parallel()
            
        # Initialize pipeline parallelism if enabled
        if self.config.get('use_pipeline_parallel', False):
            self._init_pipeline_parallel()
            
        # Initialize gradient accumulation
        self.gradient_accumulation_steps = config.get('gradient_accumulation_steps', 1)
        self.current_step = 0
        
        # Initialize mixed precision training
        self.use_amp = config.get('use_amp', False)
        if self.use_amp:
            self.scaler = torch.cuda.amp.GradScaler()
            
        # Initialize gradient clipping
        self.grad_clip_value = config.get('grad_clip_value', None)
        
        # Initialize learning rate scheduler
        self.scheduler = self._create_scheduler()
        
    def _init_distributed(self):
        """Initialize distributed training"""
        try:
            # Get world size and rank
            self.world_size = int(os.environ.get('WORLD_SIZE', 1))
            self.rank = int(os.environ.get('RANK', 0))
            
            if self.world_size > 1:
                # Initialize process group
                dist.init_process_group(
                    backend='nccl' if torch.cuda.is_available() else 'gloo',
                    init_method='env://'
                )
                
                # Wrap model in DDP
                self.model = DDP(
                    self.model,
                    device_ids=[self.rank],
                    output_device=self.rank
                )
                
                # Create distributed sampler
                self.train_sampler = DistributedSampler(
                    self.train_dataset,
                    num_replicas=self.world_size,
                    rank=self.rank
                )
                
            else:
                self.train_sampler = None
                
        except Exception as e:
            logger.error(f"Error initializing distributed training: {str(e)}")
            raise
            
    def _init_model_parallel(self):
        """Initialize model parallelism"""
        try:
            # Get number of GPUs
            num_gpus = torch.cuda.device_count()
            
            # Split model across GPUs
            if num_gpus > 1:
                # Create model parallel wrapper
                self.model = torch.nn.parallel.DataParallel(
                    self.model,
                    device_ids=list(range(num_gpus))
                )
                
                # Move model to first GPU
                self.model = self.model.to(0)
                
                # Create optimizer for each GPU
                self.optimizers = []
                for i in range(num_gpus):
                    optimizer = torch.optim.Adam(
                        self.model.module.parameters(),
                        lr=self.config.get('learning_rate', 0.001)
                    )
                    self.optimizers.append(optimizer)
                    
                logger.info(f"Initialized model parallelism across {num_gpus} GPUs")
                
        except Exception as e:
            logger.error(f"Error initializing model parallelism: {str(e)}")
            raise
            
    def _init_pipeline_parallel(self):
        """Initialize pipeline parallelism"""
        try:
            # Get number of GPUs
            num_gpus = torch.cuda.device_count()
            
            # Split model into stages
            if num_gpus > 1:
                # Create pipeline stages
                self.stages = self._split_model_into_stages()
                
                # Create micro-batch scheduler
                self.micro_batch_size = self.config.get('micro_batch_size', 1)
                self.num_micro_batches = self.config.get('num_micro_batches', 4)
                
                # Create pipeline schedule
                self.schedule = self._create_pipeline_schedule()
                
                # Create stage optimizers
                self.stage_optimizers = []
                for stage in self.stages:
                    optimizer = torch.optim.Adam(
                        stage.parameters(),
                        lr=self.config.get('learning_rate', 0.001)
                    )
                    self.stage_optimizers.append(optimizer)
                    
                logger.info(f"Initialized pipeline parallelism across {num_gpus} GPUs")
                
        except Exception as e:
            logger.error(f"Error initializing pipeline parallelism: {str(e)}")
            raise
            
    def _split_model_into_stages(self) -> List[torch.nn.Module]:
        """Split model into pipeline stages"""
        try:
            # Get model layers
            layers = list(self.model.children())
            
            # Calculate layers per stage
            num_stages = torch.cuda.device_count()
            layers_per_stage = len(layers) // num_stages
            
            # Create stages
            stages = []
            for i in range(num_stages):
                start_idx = i * layers_per_stage
                end_idx = start_idx + layers_per_stage if i < num_stages - 1 else len(layers)
                stage = torch.nn.Sequential(*layers[start_idx:end_idx])
                stage = stage.to(i)  # Move stage to appropriate GPU
                stages.append(stage)
                
            return stages
            
        except Exception as e:
            logger.error(f"Error splitting model into stages: {str(e)}")
            raise
            
    def _create_pipeline_schedule(self) -> List[Dict[str, Any]]:
        """Create pipeline schedule"""
        try:
            schedule = []
            num_stages = len(self.stages)
            
            # Create forward schedule
            for micro_batch in range(self.num_micro_batches):
                for stage in range(num_stages):
                    schedule.append({
                        'micro_batch': micro_batch,
                        'stage': stage,
                        'type': 'forward'
                    })
                    
            # Create backward schedule
            for micro_batch in range(self.num_micro_batches - 1, -1, -1):
                for stage in range(num_stages - 1, -1, -1):
                    schedule.append({
                        'micro_batch': micro_batch,
                        'stage': stage,
                        'type': 'backward'
                    })
                    
            return schedule
            
        except Exception as e:
            logger.error(f"Error creating pipeline schedule: {str(e)}")
            raise
            
    def _create_scheduler(self) -> Optional[torch.optim.lr_scheduler._LRScheduler]:
        """Create learning rate scheduler"""
        try:
            scheduler_config = self.config.get('scheduler', {})
            scheduler_type = scheduler_config.get('type', 'cosine')
            
            if scheduler_type == 'cosine':
                return torch.optim.lr_scheduler.CosineAnnealingLR(
                    self.optimizer,
                    T_max=scheduler_config.get('T_max', 100),
                    eta_min=scheduler_config.get('eta_min', 0)
                )
            elif scheduler_type == 'step':
                return torch.optim.lr_scheduler.StepLR(
                    self.optimizer,
                    step_size=scheduler_config.get('step_size', 30),
                    gamma=scheduler_config.get('gamma', 0.1)
                )
            elif scheduler_type == 'reduce_on_plateau':
                return torch.optim.lr_scheduler.ReduceLROnPlateau(
                    self.optimizer,
                    mode=scheduler_config.get('mode', 'min'),
                    factor=scheduler_config.get('factor', 0.1),
                    patience=scheduler_config.get('patience', 10),
                    verbose=True
                )
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error creating scheduler: {str(e)}")
            return None
            
    def train(self, num_epochs: int, batch_size: int):
        """Train the model in a distributed manner"""
        try:
            # Create data loader
            train_loader = torch.utils.data.DataLoader(
                self.train_dataset,
                batch_size=batch_size,
                sampler=self.train_sampler,
                num_workers=4,
                pin_memory=True
            )
            
            # Training loop
            for epoch in range(num_epochs):
                if self.train_sampler:
                    self.train_sampler.set_epoch(epoch)
                    
                self.model.train()
                epoch_loss = 0
                num_batches = 0
                
                for batch_idx, (data, target) in enumerate(train_loader):
                    # Process batch based on parallelism type
                    if self.config.get('use_pipeline_parallel', False):
                        loss = self._process_batch_pipeline(data, target)
                    elif self.config.get('use_model_parallel', False):
                        loss = self._process_batch_model_parallel(data, target)
                    elif self.config.get('use_tensor_parallel', False):
                        loss = self._process_batch_tensor_parallel(data, target)
                    else:
                        loss = self._process_batch(data, target)
                        
                    # Update metrics
                    epoch_loss += loss.item() * self.gradient_accumulation_steps
                    num_batches += 1
                    
                    # Log progress
                    if batch_idx % self.config['log_interval'] == 0:
                        self._log_progress(epoch, batch_idx, loss.item() * self.gradient_accumulation_steps)
                        
                # Compute epoch metrics
                avg_loss = epoch_loss / num_batches
                
                # Synchronize metrics across processes
                if self.world_size > 1:
                    avg_loss = self._synchronize_metrics(avg_loss)
                    
                # Save checkpoint
                if self.rank == 0 and (epoch + 1) % self.config['checkpoint_frequency'] == 0:
                    self._save_checkpoint(epoch, avg_loss)
                    
        except Exception as e:
            logger.error(f"Error in distributed training: {str(e)}")
            raise
            
    def _process_batch_pipeline(self, data: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Process batch using pipeline parallelism"""
        try:
            # Split batch into micro-batches
            micro_batches = data.split(self.micro_batch_size)
            micro_targets = target.split(self.micro_batch_size)
            
            # Initialize pipeline buffers
            buffers = [None] * len(self.stages)
            losses = []
            
            # Execute pipeline schedule
            for step in self.schedule:
                micro_batch = step['micro_batch']
                stage = step['stage']
                
                if step['type'] == 'forward':
                    # Forward pass
                    if stage == 0:
                        input_data = micro_batches[micro_batch]
                    else:
                        input_data = buffers[stage - 1]
                        
                    output = self.stages[stage](input_data)
                    
                    if stage < len(self.stages) - 1:
                        buffers[stage] = output
                    else:
                        # Compute loss for last stage
                        loss = self._compute_loss(output, micro_targets[micro_batch])
                        losses.append(loss)
                        
                else:  # backward
                    # Backward pass
                    if stage == len(self.stages) - 1:
                        loss = losses[micro_batch]
                    else:
                        loss = buffers[stage + 1]
                        
                    loss.backward()
                    
                    # Update optimizer
                    if self.use_amp:
                        self.scaler.step(self.stage_optimizers[stage])
                    else:
                        self.stage_optimizers[stage].step()
                    self.stage_optimizers[stage].zero_grad()
                    
            # Average losses
            return sum(losses) / len(losses)
            
        except Exception as e:
            logger.error(f"Error processing batch with pipeline parallelism: {str(e)}")
            raise
            
    def _process_batch_model_parallel(self, data: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Process batch using model parallelism"""
        try:
            # Move data to device
            data = data.to(self.rank)
            target = target.to(self.rank)
            
            # Forward pass with mixed precision
            if self.use_amp:
                with torch.cuda.amp.autocast():
                    output = self.model(data)
                    loss = self._compute_loss(output, target)
            else:
                output = self.model(data)
                loss = self._compute_loss(output, target)
                
            return loss
            
        except Exception as e:
            logger.error(f"Error processing batch with model parallelism: {str(e)}")
            raise
            
    def _process_batch_tensor_parallel(self, data: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Process batch using tensor parallelism"""
        try:
            # Move data to device
            data = data.to(self.rank)
            target = target.to(self.rank)
            
            # Forward pass with mixed precision
            if self.use_amp:
                with torch.cuda.amp.autocast():
                    output = self.model(data)
                    loss = self._compute_loss(output, target)
            else:
                output = self.model(data)
                loss = self._compute_loss(output, target)
                
            return loss
            
        except Exception as e:
            logger.error(f"Error processing batch with tensor parallelism: {str(e)}")
            raise
            
    def _process_batch(self, data: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Process batch without parallelism"""
        try:
            # Move data to device
            data = data.to(self.rank)
            target = target.to(self.rank)
            
            # Forward pass with mixed precision
            if self.use_amp:
                with torch.cuda.amp.autocast():
                    output = self.model(data)
                    loss = self._compute_loss(output, target)
            else:
                output = self.model(data)
                loss = self._compute_loss(output, target)
                
            return loss
            
        except Exception as e:
            logger.error(f"Error processing batch without parallelism: {str(e)}")
            raise
            
    def _compute_loss(self, output: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Compute loss between output and target"""
        try:
            return torch.nn.functional.cross_entropy(output, target)
            
        except Exception as e:
            logger.error(f"Error computing loss: {str(e)}")
            raise
            
    def _log_progress(self, epoch: int, batch_idx: int, loss: float):
        """Log training progress"""
        try:
            if self.rank == 0:
                logger.info(
                    f'Train Epoch: {epoch} [{batch_idx * self.config["batch_size"]} '
                    f'({100. * batch_idx / len(self.train_dataset):.0f}%)]\t'
                    f'Loss: {loss:.6f}'
                )
                
        except Exception as e:
            logger.error(f"Error logging progress: {str(e)}")
            raise
            
    def _synchronize_metrics(self, metric: float) -> float:
        """Synchronize metrics across processes"""
        try:
            if self.world_size > 1:
                # Convert metric to tensor
                metric_tensor = torch.tensor(metric, device=self.rank)
                
                # All reduce
                dist.all_reduce(metric_tensor, op=dist.ReduceOp.SUM)
                
                # Average across processes
                return metric_tensor.item() / self.world_size
                
            return metric
            
        except Exception as e:
            logger.error(f"Error synchronizing metrics: {str(e)}")
            raise
            
    def _save_checkpoint(self, epoch: int, loss: float):
        """Save training checkpoint"""
        try:
            # Create checkpoint directory
            checkpoint_dir = self.output_dir / f"checkpoint_{epoch}"
            checkpoint_dir.mkdir(exist_ok=True)
            
            # Save model state
            model_state = self.model.module.state_dict() if isinstance(self.model, DDP) else self.model.state_dict()
            torch.save(model_state, checkpoint_dir / "model.pt")
            
            # Save optimizer state
            torch.save(self.optimizer.state_dict(), checkpoint_dir / "optimizer.pt")
            
            # Save scheduler state if available
            if self.scheduler is not None:
                torch.save(self.scheduler.state_dict(), checkpoint_dir / "scheduler.pt")
                
            # Save scaler state if using mixed precision
            if self.use_amp:
                torch.save(self.scaler.state_dict(), checkpoint_dir / "scaler.pt")
                
            # Save training state
            training_state = {
                'epoch': epoch,
                'loss': loss,
                'config': self.config,
                'timestamp': datetime.now().isoformat(),
                'gradient_accumulation_steps': self.gradient_accumulation_steps,
                'use_amp': self.use_amp,
                'grad_clip_value': self.grad_clip_value
            }
            with open(checkpoint_dir / "training_state.json", 'w') as f:
                json.dump(training_state, f, indent=2)
                
            logger.info(f"Saved checkpoint to {checkpoint_dir}")
            
        except Exception as e:
            logger.error(f"Error saving checkpoint: {str(e)}")
            raise
            
    def load_checkpoint(self, checkpoint_path: str):
        """Load training checkpoint"""
        try:
            checkpoint_dir = Path(checkpoint_path)
            
            # Load model state
            model_state = torch.load(checkpoint_dir / "model.pt")
            if isinstance(self.model, DDP):
                self.model.module.load_state_dict(model_state)
            else:
                self.model.load_state_dict(model_state)
                
            # Load optimizer state
            optimizer_state = torch.load(checkpoint_dir / "optimizer.pt")
            self.optimizer.load_state_dict(optimizer_state)
            
            # Load scheduler state if available
            if self.scheduler is not None and (checkpoint_dir / "scheduler.pt").exists():
                scheduler_state = torch.load(checkpoint_dir / "scheduler.pt")
                self.scheduler.load_state_dict(scheduler_state)
                
            # Load scaler state if using mixed precision
            if self.use_amp and (checkpoint_dir / "scaler.pt").exists():
                scaler_state = torch.load(checkpoint_dir / "scaler.pt")
                self.scaler.load_state_dict(scaler_state)
                
            # Load training state
            with open(checkpoint_dir / "training_state.json", 'r') as f:
                training_state = json.load(f)
                
            logger.info(f"Loaded checkpoint from {checkpoint_dir}")
            return training_state
            
        except Exception as e:
            logger.error(f"Error loading checkpoint: {str(e)}")
            raise
            
    def cleanup(self):
        """Cleanup distributed training resources"""
        try:
            if self.world_size > 1:
                dist.destroy_process_group()
                
        except Exception as e:
            logger.error(f"Error cleaning up distributed training: {str(e)}")
            raise 