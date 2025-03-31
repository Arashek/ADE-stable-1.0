import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib
import time

import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis
import numpy as np
import torch

from .config import Config
from ...core.memory.memory_manager import MemoryManager, MemoryType
from ...core.memory.agent_memory import AgentMemory
from ...core.learning.learning_manager import LearningManager
from .models import ModelFactory
from .monitoring import TrainingMonitor
from .training_strategies import TrainingStrategyManager, TrainingMetrics

logger = logging.getLogger(__name__)

class DistributedTrainer:
    """Handles distributed training of models and data collection from ADE interactions."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DistributedTrainer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config: Optional[Config] = None):
        if not hasattr(self, 'initialized'):
            self.config = config or Config()
            self.mongodb_client = AsyncIOMotorClient(self.config.mongodb_uri)
            self.redis_client = Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                password=self.config.redis_password,
                decode_responses=True
            )
            
            # Initialize databases
            self.db = self.mongodb_client[self.config.mongodb_database]
            self.interactions_collection = self.db['agent_interactions']
            self.models_collection = self.db['trained_models']
            
            # Create data directories
            self.data_dir = Path('data')
            self.models_dir = Path('models')
            self.data_dir.mkdir(exist_ok=True)
            self.models_dir.mkdir(exist_ok=True)
            
            # Initialize ADE memory infrastructure
            self.memory_manager = MemoryManager(
                mongo_uri=self.config.mongodb_uri,
                vector_store_path=str(self.data_dir / 'vector_store'),
                knowledge_graph_path=str(self.data_dir / 'knowledge_graph')
            )
            
            # Initialize learning manager
            self.learning_manager = LearningManager(None, self.config)
            
            # Initialize agent memory
            self.agent_memory = AgentMemory(
                agent_id="model_trainer",
                repository=self.memory_manager.repository
            )
            
            # Initialize models
            self.models = {
                'code_completion': ModelFactory.create_model(
                    'code_completion',
                    'code_completion_model',
                    self.config.model_config
                ),
                'performance_prediction': ModelFactory.create_model(
                    'performance_prediction',
                    'performance_prediction_model',
                    self.config.model_config
                )
            }
            
            # Initialize monitoring
            self.monitor = TrainingMonitor(output_dir=str(self.data_dir / 'monitoring'))
            
            # Initialize training strategies
            self.strategy_manager = TrainingStrategyManager(self.config.model_config)
            
            self.initialized = True
            
            # Start automatic training
            self._start_automatic_training()

    async def collect_interaction_data(self) -> List[Dict]:
        """Collect interaction data from MongoDB and memory system."""
        # Get data from MongoDB
        cursor = self.interactions_collection.find({})
        interactions = await cursor.to_list(length=None)
        
        # Get data from memory system
        memories = await self.memory_manager.retrieve_memories(
            memory_type=MemoryType.EXPERIENCE,
            tags=["interaction", "training_data"]
        )
        
        # Combine and deduplicate data
        memory_data = [
            {
                'timestamp': memory.created_at,
                'agent_id': memory.agent_id,
                'model_name': memory.metadata.get('model_name'),
                'prompt': memory.content.get('prompt'),
                'response': memory.content.get('response'),
                'feedback_score': memory.content.get('feedback_score'),
                'execution_time': memory.content.get('execution_time'),
                'memory_usage': memory.content.get('memory_usage'),
                'error_rate': memory.content.get('error_rate'),
                'success_rate': memory.content.get('success_rate')
            }
            for memory in memories
        ]
        
        # Combine and deduplicate based on content hash
        seen_hashes = set()
        combined_data = []
        
        for interaction in interactions + memory_data:
            content_hash = self._hash_content(interaction)
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                combined_data.append(interaction)
        
        return combined_data

    def _hash_content(self, interaction: Dict) -> str:
        """Generate a hash for interaction content."""
        content = f"{interaction.get('prompt', '')}{interaction.get('response', '')}"
        return hashlib.sha256(content.encode()).hexdigest()

    async def process_interactions(self, interactions: List[Dict]) -> pd.DataFrame:
        """Process interaction data into training format."""
        processed_data = []
        for interaction in interactions:
            processed_entry = {
                'timestamp': interaction.get('timestamp', datetime.now()),
                'agent_id': interaction.get('agent_id'),
                'model_name': interaction.get('model_name'),
                'prompt': interaction.get('prompt'),
                'response': interaction.get('response'),
                'feedback_score': interaction.get('feedback_score'),
                'execution_time': interaction.get('execution_time'),
                'memory_usage': interaction.get('memory_usage'),
                'error_rate': interaction.get('error_rate'),
                'success_rate': interaction.get('success_rate')
            }
            processed_data.append(processed_entry)
            
            # Store processed interaction in memory system
            await self.memory_manager.store_memory(
                content=processed_entry,
                memory_type=MemoryType.EXPERIENCE,
                metadata={'processed': True},
                tags=['interaction', 'training_data']
            )
        
        return pd.DataFrame(processed_data)

    async def train(self, model_name: Optional[str] = None):
        """Train or fine-tune models based on collected data."""
        try:
            start_time = time.time()
            
            # Collect interaction data
            logger.info("Collecting interaction data...")
            interactions = await self.collect_interaction_data()
            
            if not interactions:
                logger.warning("No interaction data found for training")
                return
            
            # Process data
            logger.info("Processing interaction data...")
            df = await self.process_interactions(interactions)
            
            # Save processed data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            df.to_csv(self.data_dir / f'processed_data_{timestamp}.csv', index=False)
            
            # Prepare training and validation data
            train_data, val_data = self.strategy_manager.prepare_training_data(df)
            
            # Train models
            metrics_history = []
            for model_type, model in self.models.items():
                logger.info(f"Training {model_type} model...")
                
                # Get training batch using curriculum learning
                batch_size = self.config.model_config.get('batch_size', 32)
                train_batch = self.strategy_manager.get_training_batch(train_data, batch_size)
                
                # Train model
                model.train(train_batch)
                
                # Generate predictions for metrics
                if model_type == 'code_completion':
                    test_prompts = val_data['prompt'].head(5).tolist()
                    predictions = [model.predict(prompt) for prompt in test_prompts]
                    accuracy = self._calculate_accuracy(predictions, val_data['response'].head(5).tolist())
                else:
                    predictions = model.predict(val_data)
                    accuracy = self._calculate_accuracy(predictions, val_data['feedback_score'])
                
                # Calculate metrics
                metrics = TrainingMetrics(
                    loss=0.0,  # TODO: Implement loss calculation
                    accuracy=accuracy,
                    validation_loss=0.0,  # TODO: Implement validation loss
                    validation_accuracy=accuracy,
                    learning_rate=self.config.model_config.get('learning_rate', 0.001),
                    epoch=len(metrics_history)
                )
                
                # Update training strategies
                self.strategy_manager.update_training_state(metrics)
                
                # Adapt to new task if needed
                if self._should_adapt_to_new_task(metrics):
                    model = self.strategy_manager.adapt_to_new_task(model, train_batch)
                
                # Update monitoring
                self.monitor.update_metrics(metrics.__dict__)
                metrics_history.append(metrics.__dict__)
                
                # Save model
                model.save(self.models_dir / f"{model_type}_{timestamp}.pkl")
            
            # Generate monitoring report
            self.monitor.generate_report(metrics_history, df)
            
            # Store metrics in MongoDB and memory system
            await self.models_collection.insert_many(metrics_history)
            for metrics in metrics_history:
                await self.memory_manager.store_memory(
                    content=metrics,
                    memory_type=MemoryType.METADATA,
                    tags=['training_metrics']
                )
            
            # Store training state
            training_state = self.strategy_manager.get_training_state()
            await self.memory_manager.store_memory(
                content=training_state,
                memory_type=MemoryType.METADATA,
                tags=['training_state']
            )
            
            logger.info(f"Training completed. Metrics stored in database.")
            
        except Exception as e:
            logger.error(f"Error during training: {e}", exc_info=True)
            raise

    def _should_adapt_to_new_task(self, metrics: TrainingMetrics) -> bool:
        """Determine if model should adapt to a new task."""
        return (
            metrics.accuracy < 0.5 or
            metrics.validation_loss > metrics.loss * 1.5
        )

    def _calculate_accuracy(self, predictions: List, targets: List) -> float:
        """Calculate accuracy between predictions and targets."""
        if not predictions or not targets:
            return 0.0
            
        if isinstance(predictions[0], str):
            # For code completion
            return sum(1 for p, t in zip(predictions, targets) if p.strip() == t.strip()) / len(predictions)
        else:
            # For performance prediction
            return 1 - np.mean(np.abs(np.array(predictions) - np.array(targets)))

    def _get_memory_usage(self) -> float:
        """Get current memory usage in bytes."""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss

    def _start_automatic_training(self):
        """Start automatic training process."""
        import asyncio
        import threading
        
        def run_async_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_forever()
        
        # Start async loop in a separate thread
        self.training_thread = threading.Thread(target=run_async_loop, daemon=True)
        self.training_thread.start()
        
        # Schedule periodic training
        asyncio.run_coroutine_threadsafe(
            self._schedule_training(),
            self.training_thread._loop
        )

    async def _schedule_training(self):
        """Schedule periodic training."""
        while True:
            try:
                await self.train()
                await asyncio.sleep(300)  # Train every 5 minutes
            except Exception as e:
                logger.error(f"Error in scheduled training: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    def cleanup(self):
        """Clean up resources."""
        self.mongodb_client.close()
        self.redis_client.close()
        if hasattr(self, 'training_thread'):
            self.training_thread.join(timeout=1) 