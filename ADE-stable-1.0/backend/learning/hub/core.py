from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
from ...config.logging_config import logger
from .models import LearningModel, Dataset, TrainingSession
from .analytics import AnalyticsEngine
from .data_collector import DataCollector
from .model_trainer import ModelTrainer
from .knowledge_base import KnowledgeBase

class LearningHub:
    """Core learning hub that orchestrates all learning activities"""
    
    def __init__(self):
        self.models: Dict[str, LearningModel] = {}
        self.datasets: Dict[str, Dataset] = {}
        self.training_sessions: Dict[str, TrainingSession] = {}
        self.analytics = AnalyticsEngine()
        self.data_collector = DataCollector()
        self.model_trainer = ModelTrainer()
        self.knowledge_base = KnowledgeBase()
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    async def initialize(self):
        """Initialize the learning hub"""
        try:
            # Load existing models and datasets
            await self._load_existing_data()
            
            # Start background tasks
            asyncio.create_task(self._collect_anonymous_data())
            asyncio.create_task(self._update_knowledge_base())
            
            logger.info("Learning hub initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing learning hub: {str(e)}")
            raise
            
    async def _load_existing_data(self):
        """Load existing models and datasets"""
        try:
            # Load models
            models_dir = Path("data/models")
            if models_dir.exists():
                for model_file in models_dir.glob("*.json"):
                    with open(model_file, 'r') as f:
                        model_data = json.load(f)
                        self.models[model_data["id"]] = LearningModel(**model_data)
                        
            # Load datasets
            datasets_dir = Path("data/datasets")
            if datasets_dir.exists():
                for dataset_file in datasets_dir.glob("*.json"):
                    with open(dataset_file, 'r') as f:
                        dataset_data = json.load(f)
                        self.datasets[dataset_data["id"]] = Dataset(**dataset_data)
                        
        except Exception as e:
            logger.error(f"Error loading existing data: {str(e)}")
            raise
            
    async def _collect_anonymous_data(self):
        """Collect anonymous usage data"""
        while True:
            try:
                # Collect data from all active instances
                data = await self.data_collector.collect_anonymous_data()
                
                # Process and store the data
                await self._process_collected_data(data)
                
                # Wait before next collection
                await asyncio.sleep(3600)  # Collect every hour
                
            except Exception as e:
                logger.error(f"Error collecting anonymous data: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
                
    async def _process_collected_data(self, data: List[Dict[str, Any]]):
        """Process collected anonymous data"""
        try:
            # Aggregate data
            aggregated_data = self.analytics.aggregate_data(data)
            
            # Update datasets
            for dataset_id, new_data in aggregated_data.items():
                if dataset_id in self.datasets:
                    await self.datasets[dataset_id].update(new_data)
                else:
                    self.datasets[dataset_id] = Dataset(
                        id=dataset_id,
                        data=new_data,
                        metadata={"source": "anonymous_collection"}
                    )
                    
            # Trigger model updates if needed
            await self._check_model_updates()
            
        except Exception as e:
            logger.error(f"Error processing collected data: {str(e)}")
            
    async def _check_model_updates(self):
        """Check if models need updating based on new data"""
        try:
            for model_id, model in self.models.items():
                if model.needs_update():
                    await self._update_model(model_id)
                    
        except Exception as e:
            logger.error(f"Error checking model updates: {str(e)}")
            
    async def _update_model(self, model_id: str):
        """Update a specific model"""
        try:
            model = self.models[model_id]
            
            # Get relevant dataset
            dataset = self.datasets.get(model.dataset_id)
            if not dataset:
                return
                
            # Train model with new data
            updated_model = await self.model_trainer.train(
                model=model,
                dataset=dataset
            )
            
            # Update model in storage
            self.models[model_id] = updated_model
            await self._save_model(model_id)
            
        except Exception as e:
            logger.error(f"Error updating model {model_id}: {str(e)}")
            
    async def _update_knowledge_base(self):
        """Update the knowledge base with new information"""
        while True:
            try:
                # Get new knowledge from models and datasets
                new_knowledge = await self.knowledge_base.extract_new_knowledge(
                    models=self.models,
                    datasets=self.datasets
                )
                
                # Update knowledge base
                await self.knowledge_base.update(new_knowledge)
                
                # Wait before next update
                await asyncio.sleep(86400)  # Update daily
                
            except Exception as e:
                logger.error(f"Error updating knowledge base: {str(e)}")
                await asyncio.sleep(3600)  # Wait before retrying
                
    async def _save_model(self, model_id: str):
        """Save a model to storage"""
        try:
            model = self.models[model_id]
            models_dir = Path("data/models")
            models_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = models_dir / f"{model_id}.json"
            with open(output_file, 'w') as f:
                json.dump(model.to_dict(), f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving model {model_id}: {str(e)}")
            
    async def get_model(self, model_id: str) -> Optional[LearningModel]:
        """Get a specific model"""
        return self.models.get(model_id)
        
    async def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        """Get a specific dataset"""
        return self.datasets.get(dataset_id)
        
    async def get_training_session(self, session_id: str) -> Optional[TrainingSession]:
        """Get a specific training session"""
        return self.training_sessions.get(session_id)
        
    async def create_training_session(self, 
                                    model_id: str,
                                    dataset_id: str,
                                    parameters: Dict[str, Any]) -> TrainingSession:
        """Create a new training session"""
        try:
            session = TrainingSession(
                id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                model_id=model_id,
                dataset_id=dataset_id,
                parameters=parameters,
                status="created"
            )
            
            self.training_sessions[session.id] = session
            
            # Start training in background
            asyncio.create_task(self._run_training_session(session.id))
            
            return session
            
        except Exception as e:
            logger.error(f"Error creating training session: {str(e)}")
            raise
            
    async def _run_training_session(self, session_id: str):
        """Run a training session"""
        try:
            session = self.training_sessions[session_id]
            session.status = "running"
            
            # Get model and dataset
            model = await self.get_model(session.model_id)
            dataset = await self.get_dataset(session.dataset_id)
            
            if not model or not dataset:
                session.status = "failed"
                return
                
            # Train model
            updated_model = await self.model_trainer.train(
                model=model,
                dataset=dataset,
                parameters=session.parameters
            )
            
            # Update model
            self.models[session.model_id] = updated_model
            await self._save_model(session.model_id)
            
            # Update session
            session.status = "completed"
            session.completed_at = datetime.now()
            
        except Exception as e:
            logger.error(f"Error running training session {session_id}: {str(e)}")
            session.status = "failed"
            session.error = str(e) 