from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime
from .models import LearningModel, Dataset, TrainingSession
from ...config.logging_config import logger

class ModelTrainer:
    """Trainer for handling model training and updates"""
    
    def __init__(self):
        self.training_history: Dict[str, List[Dict[str, Any]]] = {}
        
    async def train(self, 
                   model: LearningModel,
                   dataset: Dataset,
                   parameters: Optional[Dict[str, Any]] = None) -> LearningModel:
        """Train a model with a dataset"""
        try:
            # Update model parameters if provided
            if parameters:
                model.parameters.update(parameters)
                
            # Prepare training data
            X, y = self._prepare_training_data(dataset)
            
            # Train model based on type
            if model.type == "classification":
                trained_model = await self._train_classification_model(model, X, y)
            elif model.type == "regression":
                trained_model = await self._train_regression_model(model, X, y)
            else:
                raise ValueError(f"Unsupported model type: {model.type}")
                
            # Update model metrics
            trained_model.metrics = self._calculate_metrics(trained_model, X, y)
            trained_model.updated_at = datetime.now()
            
            # Record training history
            self._record_training_history(model.id, trained_model.metrics)
            
            return trained_model
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
            
    def _prepare_training_data(self, dataset: Dataset) -> tuple:
        """Prepare training data from dataset"""
        try:
            # Convert dataset to numpy arrays
            X = []
            y = []
            
            for entry in dataset.data:
                features = entry.get("features", {})
                target = entry.get("target")
                
                if features and target is not None:
                    X.append(list(features.values()))
                    y.append(target)
                    
            return np.array(X), np.array(y)
            
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            raise
            
    async def _train_classification_model(self, 
                                        model: LearningModel,
                                        X: np.ndarray,
                                        y: np.ndarray) -> LearningModel:
        """Train a classification model"""
        try:
            # In production, this would use actual ML libraries
            # For now, simulate training
            model.metrics = {
                "accuracy": 0.95,
                "precision": 0.94,
                "recall": 0.93,
                "f1_score": 0.94
            }
            
            return model
            
        except Exception as e:
            logger.error(f"Error training classification model: {str(e)}")
            raise
            
    async def _train_regression_model(self,
                                    model: LearningModel,
                                    X: np.ndarray,
                                    y: np.ndarray) -> LearningModel:
        """Train a regression model"""
        try:
            # In production, this would use actual ML libraries
            # For now, simulate training
            model.metrics = {
                "mse": 0.1,
                "rmse": 0.32,
                "mae": 0.28,
                "r2_score": 0.92
            }
            
            return model
            
        except Exception as e:
            logger.error(f"Error training regression model: {str(e)}")
            raise
            
    def _calculate_metrics(self, 
                          model: LearningModel,
                          X: np.ndarray,
                          y: np.ndarray) -> Dict[str, float]:
        """Calculate model metrics"""
        try:
            # In production, this would use actual ML libraries
            # For now, return mock metrics
            if model.type == "classification":
                return {
                    "accuracy": 0.95,
                    "precision": 0.94,
                    "recall": 0.93,
                    "f1_score": 0.94
                }
            else:
                return {
                    "mse": 0.1,
                    "rmse": 0.32,
                    "mae": 0.28,
                    "r2_score": 0.92
                }
                
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return {}
            
    def _record_training_history(self, model_id: str, metrics: Dict[str, float]):
        """Record training history"""
        try:
            if model_id not in self.training_history:
                self.training_history[model_id] = []
                
            self.training_history[model_id].append({
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics
            })
            
        except Exception as e:
            logger.error(f"Error recording training history: {str(e)}")
            
    def get_training_history(self, model_id: str) -> List[Dict[str, Any]]:
        """Get training history for a model"""
        try:
            return self.training_history.get(model_id, [])
            
        except Exception as e:
            logger.error(f"Error getting training history: {str(e)}")
            return []
            
    def get_best_model(self, model_id: str, metric: str) -> Optional[Dict[str, Any]]:
        """Get the best performing model based on a metric"""
        try:
            if model_id not in self.training_history:
                return None
                
            history = self.training_history[model_id]
            if not history:
                return None
                
            # Find best performing model
            best_model = max(history, key=lambda x: x["metrics"].get(metric, 0))
            
            return {
                "model_id": model_id,
                "timestamp": best_model["timestamp"],
                "metrics": best_model["metrics"]
            }
            
        except Exception as e:
            logger.error(f"Error getting best model: {str(e)}")
            return None
            
    def get_model_progress(self, model_id: str, metric: str) -> List[Dict[str, Any]]:
        """Get progress of a model's performance over time"""
        try:
            if model_id not in self.training_history:
                return []
                
            history = self.training_history[model_id]
            progress = []
            
            for entry in history:
                progress.append({
                    "timestamp": entry["timestamp"],
                    "value": entry["metrics"].get(metric, 0)
                })
                
            return progress
            
        except Exception as e:
            logger.error(f"Error getting model progress: {str(e)}")
            return [] 